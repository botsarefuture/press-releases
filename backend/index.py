import requests
from flask import Flask, jsonify, request
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

press_releases = []

def get_journalists_from_github():
    # GitHub repository details
    github_username = 'your_github_username'
    github_repo = 'your_github_repository'
    filepath = 'journalists.txt'

    # GitHub API request
    url = f'https://api.github.com/repos/{github_username}/{github_repo}/contents/{filepath}'
    response = requests.get(url)
    data = response.json()

    # Decode content from Base64 and split into list of emails
    content = data['content']
    journalists = content.decode('base64').split('\n')

    return journalists

@app.route('/api/press-releases', methods=['GET'])
def get_press_releases():
    return jsonify(press_releases)

@app.route('/api/new-release', methods=['POST'])
def new_press_release():
    data = request.json
    press_releases.append(data)

    # Send email to all journalists
    send_email_to_journalists(data['title'], data['content'])

    return jsonify({"message": "Press release added successfully"})

def send_email_to_journalists(title, content):
    # SMTP server configuration
    smtp_server = 'your_smtp_server'
    smtp_port = 587
    sender_email = 'your_email@example.com'
    password = 'your_password'

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
            server.login(sender_email, password)
            server.sendmail(sender_email, journalist_email, msg.as_string())

if __name__ == '__main__':
    app.run(debug=True)
