from flask import Flask, jsonify, request, session, redirect, url_for, render_template
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import requests


from flask import Flask, jsonify, request, session, redirect, url_for
from flask_cors import CORS # Import CORS module

from functions import load_releases, save_releases

app = Flask(__name__, template_folder="html")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Enable CORS for all domains
CORS(app, origins='*')

press_releases = []
press_releases = load_releases()

to_replace = [("Ã¤", "ä"), ("Ã¶", "ö"), ("Ã„", "Ä"), ("Ã–", "Ö")]

for press_release in press_releases:
    for to_repla in to_replace:
        press_release["content"] = press_release["content"].replace(to_repla[0], to_repla[1])

# Sample user data for demonstration purposes
users = {
    "user1": {"password": "password1", "email": "user1@example.com"},
    "user2": {"password": "password2", "email": "user2@example.com"}
}

# Load config from config.json
with open('config.json') as f:
    config = json.load(f)

# Extract config values
github_username = config['github_username']
github_repo = config['github_repo']
github_filepath = config['github_filepath']
smtp_server = config['smtp_server']
smtp_port = config['smtp_port']
sender_email = config['sender_email']
sender_password = config['sender_password']

def generate_example_press_releases(num_releases=5):
    examples = []
    for i in range(num_releases):
        example = {
            "title": f"Example Press Release {i+1}",
            "content": f"This is an example press release {i+1}. Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        }
        examples.append(example)
    return examples

#press_releases = generate_example_press_releases()

def get_journalists_from_github():
    # GitHub repository details
    url = f'https://api.github.com/repos/{github_username}/{github_repo}/contents/{github_filepath}'
    response = requests.get(url)
    data = response.json()

    # Decode content from Base64 and split into list of emails
    content = data['content']
    journalists = content.decode('base64').split('\n')

    return journalists

def save_press_releases_to_file(press_releases):
    save_releases(press_releases)
    raise PendingDeprecationWarning("This will be depraced in next version. Use save_releases() instead.")

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
    press_releases.append(data)

    # Save press releases to file
    save_press_releases_to_file(press_releases)

    # Send email to all journalists
    #send_email_to_journalists(data['title'], data['content'])

    return jsonify({"message": "Press release added successfully"})

@app.route("/")
def index():
    #with open("../html/index.html") as f:
        #return f.read()
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
    return render_template("create_release.html")

@app.route("/<name>")
def ro(name):
    with open(f"html/{name}") as f:
        return f.read()
    

from flask import send_file

@app.route("/static/<path:path>")
def static_file(path):
    # Determine content type based on file extension
    if path.endswith('.css'):
        content_type = 'text/css'
    elif path.endswith('.js'):
        content_type = 'text/javascript'
    else:
        content_type = 'text/plain'  # Default to plain text if content type is unknown

    # Return the static file with appropriate content type
    return send_file(f"static/{path}", mimetype=content_type)


def send_email_to_journalists(title, content):
    # Email content
    subject = f'New Press Release: {title}'
    body = content

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Fetch list of journalists from GitHub
    journalists = get_journalists_from_github()

    # Send email to each journalist
    for journalist_email in journalists:
        msg['To'] = journalist_email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, journalist_email, msg.as_string())

if __name__ == '__main__':
    app.run()