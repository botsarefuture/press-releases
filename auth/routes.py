from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
)
from flask_login import login_user, logout_user, login_required
from auth.models import User
import jwt
import datetime
from emailer.EmailSender import EmailSender
from database_manager import DatabaseManager

db_manager = DatabaseManager()
mongo = db_manager.get_db()

email_sender = EmailSender()
auth_bp = Blueprint("auth", __name__, template_folder="/auth/templates/")


def verify_emailer(email, username):
    token = generate_confirmation_token(email)
    confirmation_url = url_for("auth.confirm_email", token=token, _external=True)

    email_sender.queue_email(
        template_name="registration_confirmation_email.html",
        subject="Vahvista rekisteröitymisesi",
        recipients=[email],
        context={"confirmation_url": confirmation_url, "user_name": username},
    )


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")

        if not username or not password or len(username) < 3 or len(password) < 6:
            flash(
                "Virheellinen syöte. Käyttäjänimen tulee olla vähintään 3 merkkiä pitkä ja salasanan vähintään 6 merkkiä pitkä.",
                "error",
            )
            return redirect(url_for("auth.register"))

        if mongo.users.find_one({"username": username}):
            flash("Käyttäjänimi on jo käytössä.", "warning")
            return redirect(url_for("auth.register"))

        if mongo.users.find_one({"email": email}):
            flash(
                "Sähköpostiosoite on jo rekisteröity. Kirjaudu sisään sen sijaan.",
                "warning",
            )
            return redirect(url_for("auth.login"))

        user_data = User.create_user(username, password, email)
        mongo.users.insert_one(user_data)

        try:
            verify_emailer(email, username)
            flash(
                "Rekisteröinti onnistui! Tarkista sähköpostisi vahvistaaksesi tilisi.",
                "info",
            )
        except Exception as e:
            flash(f"Virhe vahvistusviestin lähettämisessä: {e}", "error")

        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/confirm_email/<token>")
def confirm_email(token):
    email = verify_confirmation_token(token)
    if email:
        user = mongo.users.find_one({"email": email})
        if user:
            mongo.users.update_one({"email": email}, {"$set": {"confirmed": True}})
            flash(
                "Sähköpostiosoitteesi on vahvistettu. Voit nyt kirjautua sisään.",
                "info",
            )
        else:
            flash("Käyttäjää ei löytynyt.", "error")
    else:
        flash("Vahvistuslinkki on virheellinen tai vanhentunut.", "warning")

    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Anna sekä käyttäjänimi että salasana.", "warning")
            return redirect(url_for("auth.login"))

        user_doc = mongo.users.find_one({"username": username})

        if not user_doc:
            flash(f"Käyttäjänimellä '{username}' ei löytynyt käyttäjiä.", "error")
            return redirect(url_for("auth.login"))

        user = User.from_db(user_doc)
        if not user.check_password(password):
            flash("Käyttäjänimi tai salasana on väärin.", "error")
            return redirect(url_for("auth.login"))

        if user.confirmed:
            login_user(user)
            return redirect(url_for("index"))

        else:
            flash("Sähköpostiosoitettasi ei ole vahvistettu. Tarkista sähköpostisi.")
            verify_emailer(user.email, username)
            return redirect(url_for("index"))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Kirjauduit onnistuneesti ulos", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/password_reset_request", methods=["GET", "POST"])
def password_reset_request():
    if request.method == "POST":
        email = request.form.get("email")
        user = mongo.users.find_one({"email": email})

        if user:
            token = generate_reset_token(email)
            reset_url = url_for("auth.password_reset", token=token, _external=True)

            try:
                email_sender.queue_email(
                    template_name="password_reset_email.html",
                    subject="Salasanan palautuspyyntö",
                    recipients=[email],
                    context={"reset_url": reset_url, "user_name": user.get("username")},
                )
                flash("Salasanan palautuslinkki on lähetetty sähköpostiisi.", "info")
            except Exception as e:
                flash(f"Virhe salasanan palautusviestin lähettämisessä: {e}", "error")

            return redirect(url_for("auth.login"))

        flash("Tilin sähköpostiosoitetta ei löytynyt.", "info")
        return redirect(url_for("auth.password_reset_request"))

    return render_template("password_reset_request.html")


@auth_bp.route("/password_reset/<token>", methods=["GET", "POST"])
def password_reset(token):
    email = verify_reset_token(token)
    if not email:
        flash("Salasanan palautuslinkki on virheellinen tai vanhentunut.", "warning")
        return redirect(url_for("auth.password_reset_request"))

    if request.method == "POST":
        password = request.form.get("password")

        user_doc = mongo.users.find_one({"email": email})
        if not user_doc:
            flash("Käyttäjää ei löytynyt.", "warning")
            return redirect(url_for("auth.password_reset_request"))

        user = User.from_db(user_doc)
        user.change_password(mongo, password)

        flash("Salasanasi on päivitetty onnistuneesti.", "success")
        return redirect(url_for("auth.login"))

    return render_template("password_reset.html", token=token)


def generate_reset_token(email):
    return jwt.encode(
        {
            "email": email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        },
        current_app.config["SECRET_KEY"],
        algorithm="HS256",
    )


def verify_reset_token(token):
    try:
        data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        return data["email"]
    except Exception:
        return None


def generate_confirmation_token(email):
    return jwt.encode(
        {
            "email": email,
            "exp": datetime.datetime.now(datetime.datetime.UTC())
            + datetime.timedelta(hours=1),
        },
        current_app.config["SECRET_KEY"],
        algorithm="HS256",
    )


def verify_confirmation_token(token):
    try:
        data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        return data["email"]
    except Exception:
        return None
