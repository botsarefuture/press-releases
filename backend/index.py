from flask import Flask, jsonify, request, session, redirect, url_for, render_template, send_file
from flask_cors import CORS
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import requests
from functions import load_releases, save_releases
from datetime import datetime



app = Flask(__name__, template_folder="html")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
CORS(app, origins='*')

press_releases = load_releases()

def load_config():
    with open('config.json') as f:
        return json.load(f)

config = load_config()

to_replace = {'Ã¤': 'ä', 'Ã¶': 'ö', 'Ã„': 'Ä', 'Ã–': 'Ö'}
def replace_characters(s):
    for item in to_replace:
        s.replace(item[0], item[1])
    
    return s
        
for press_release in press_releases:
    press_release["content"] = replace_characters(press_release["content"])

users = {
    "user1": {"password": "password1", "email": "user1@example.com"},
    "user2": {"password": "password2", "email": "user2@example.com"}
}

github_username = config['github_username']
github_repo = config['github_repo']
github_filepath = config['github_filepath']
smtp_server = config['smtp_server']
smtp_port = config['smtp_port']
sender_email = config['sender_email']
sender_password = config['sender_password']

def get_journalists_from_github():
    try:
        url = f'https://api.github.com/repos/{github_username}/{github_repo}/contents/{github_filepath}'
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for non-200 responses
        data = response.json()
        content = data.get('content', '')
        journalists = content.decode('base64').split('\n')
        return journalists
    except Exception as e:
        print(f"Error fetching journalists from GitHub: {e}")
        return []

def save_press_releases_to_file(press_releases):
    try:
        save_releases(press_releases)
    except Exception as e:
        print(f"Error saving press releases to file: {e}")

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username in users and users[username]["password"] == password:
        session['username'] = username
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return jsonify({"message": "Logout successful"}), 200

@app.route('/api/press-releases', methods=['GET'])
def get_press_releases():
    return jsonify(press_releases)

@app.route('/api/new-release', methods=['POST'])
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
    press_releases.append(data)
    save_press_releases_to_file(press_releases)

    return jsonify({"message": "Press release added successfully"})

@app.route("/")
def index():
    for item in press_releases:
        item["review"] = str(item["content"])[0:50]
    return render_template("index.html", press_releases=press_releases)

@app.route("/releases/<id>")
def release(id):
    release = press_releases[int(id)]
    return render_template("release.html", release=release)

@app.route("/login/")
def login_v2():
    return render_template("login.html")

@app.route("/new_release/")
def new():
    if 'username' not in session:
        return redirect(url_for('login_v2'))
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
    content_type = 'text/plain'  # Default to plain text if content type is unknown
    if path.endswith(('.css', '.js')):
        content_type = f'text/{path.rsplit(".", 1)[1]}'
    return send_file(f"static/{path}", mimetype=content_type)

if __name__ == '__main__':
    app.run()
