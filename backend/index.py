from flask import (
    Flask,
    session,
    redirect,
    url_for,
    render_template,
    send_from_directory,
)
from flask_cors import CORS
from db import PressReleaseDatabase
from api import api

PRDB = PressReleaseDatabase()

app = Flask(__name__, template_folder="html")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.register_blueprint(api, url_prefix="/api")
CORS(app, origins="*")


@app.route("/")
def index():
    press_releases = PRDB.get_press_releases()
    for item in press_releases:
        item["review"] = str(item["content"])[0:50]
    return render_template("index.html", press_releases=press_releases)


@app.route("/releases/<id>")
def release(id):
    release = PRDB.get_press_release(id)
    return render_template("release.html", release=release)


@app.route("/login/")
def login_v2():
    return render_template("login.html")


@app.route("/new_release/")
def new():
    if "username" not in session:
        return redirect(url_for("login_v2"))
    return render_template("create_release.html")


@app.route("/<name>")
def ro(name):
    try:
        with open(f"html/{name}") as f:
            return f.read()
    except FileNotFoundError:
        return "File not found", 404


@app.route("/static/<path:path>")
def static_file(path):
    return send_from_directory("static", path)


if __name__ == "__main__":
    app.run()
