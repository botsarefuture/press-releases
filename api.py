from flask import Blueprint, jsonify, request, session, abort
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Dict, Any, List
from db import PressReleaseDatabase
from emailer.EmailSender import EmailSender  # Import your EmailSender class

api = Blueprint("api", __name__)

# Initialize the PressReleaseDatabase
PRDB = PressReleaseDatabase()

# Initialize EmailSender
email_sender = EmailSender()

def get_pressers(PRDB):
    return list(PRDB.db.press.find({"unsubscribed": False}))

pressers = get_pressers(PRDB)


@api.route("/login", methods=["POST"])
def login() -> Dict[str, Any]:
    """
    Authenticate user and start a session.
    """
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        abort(400, description="Username and password are required")

    user = PRDB.get_user(username)
    if user and check_password_hash(user["password"], password):
        session["username"] = username
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401


@api.route("/logout", methods=["GET"])
def logout() -> Dict[str, Any]:
    """
    End user session.
    """
    session.pop("username", None)
    return jsonify({"message": "Logout successful"}), 200


@api.route("/press-releases", methods=["GET"])
def get_press_releases() -> Dict[str, Any]:
    """
    Retrieve all press releases.
    """
    press_releases = PRDB.get_press_releases()
    if not press_releases:
        return jsonify({"message": "No press releases found"}), 404
    return jsonify(press_releases), 200


@api.route("/new-release", methods=["POST"])
def new_press_release() -> Dict[str, Any]:
    """
    Create a new press release and notify subscribers.
    """
    if "username" not in session:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.json
    required_fields = [
        "title",
        "content",
        "organization",
        "contact_name",
        "contact_email",
        "contact_phone",
    ]
    if not all(field in data for field in required_fields):
        return jsonify({"message": "All fields are required"}), 400

    current_datetime = datetime.now()
    publish_date = current_datetime.strftime("%d.%m.%Y %H:%M")
    data["publish_date"] = publish_date

    try:
        _id = PRDB.save_press_release(data)
        # Prepare email context
        email_context = {
            "title": data.get("title"),
            "publish_date": data.get("publish_date"),
            "content": data.get("content"),
            "contact_name": data.get("contact_name"),
            "contact_email": data.get("contact_email"),
            "contact_phone": data.get("contact_phone"),
            "current_year": datetime.now().year,
        }

        email_sender.queue_email(
            template_name="press_release_template.html",  # Specify the template name
            subject="Lehdistötiedotteiden jakelupalvelu",
            recipients=pressers,
            context=email_context,
        )
        return jsonify({"message": "Press release added successfully"}), 201
    except Exception as e:
        return jsonify({"message": "Failed to add press release", "error": str(e)}), 500


@api.route("/register", methods=["POST"])
def register() -> Dict[str, Any]:
    """
    Register a new user.
    """
    data = request.json
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    if not all([username, password, email]):
        return jsonify({"message": "Username, password, and email are required"}), 400

    if PRDB.does_user_exist(username):
        return jsonify({"message": "Username already exists"}), 400

    hashed_password = generate_password_hash(password, method="sha256")
    try:
        PRDB.save_user(username, hashed_password, email)
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"message": "Registration failed", "error": str(e)}), 500
