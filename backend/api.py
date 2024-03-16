from flask import Blueprint, jsonify, request, session
from functions import load_releases, save_releases
from datetime import datetime
from db import PressReleaseDatabase

api = Blueprint('api', __name__)

PRDB = PressReleaseDatabase()

@api.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if PRDB.confirm_user(username, password):
        session['username'] = username
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@api.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return jsonify({"message": "Logout successful"}), 200

@api.route('/press-releases', methods=['GET'])
def get_press_releases():
    return jsonify(PRDB.get_press_releases())

@api.route('/new-release', methods=['POST'])
def new_press_release():
    if 'username' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.json

    # Get the current date and time
    current_datetime = datetime.now()

    # Format the date and time as DD.MM.YYYY HH:MM
    publish_date = current_datetime.strftime('%d.%m.%Y %H:%M')

    # Set the publish_date in the data dictionary
    data["publish_date"] = publish_date
    PRDB.save_press_release(data)

    return jsonify({"message": "Press release added successfully"})

@api.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not (username and password and email):
        return jsonify({"message": "Username, password, and email are required fields"}), 400

    if PRDB.does_user_exist(username):
        return jsonify({"message": "Username already exists"}), 400

    PRDB.save_user(username, password, email)
    return jsonify({"message": "User registered successfully"}), 200
