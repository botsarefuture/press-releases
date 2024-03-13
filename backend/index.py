import requests
from flask import Flask, jsonify, request
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json

app = Flask(__name__)

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
    with open('press_releases.json', 'w') as f:
        json.dump(press_releases, f, indent=4)

@app.route('/api/press-releases', methods=['GET'])
def get_press_releases():
    return jsonify(press_releases)

@app.route('/api/new-release', methods=['POST'])
def new_press_release():
    data = request.json
    press_releases.append(data)
    
    # Save press releases to file
    save_press_releases_to_file(press_releases)

    # Send email to all journalists
    send_email_to_journalists(data['title'], data['content'])

    return jsonify({"message": "Press release added successfully"})

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
    app.run(debug=True)
