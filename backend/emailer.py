import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
from concurrent.futures import ThreadPoolExecutor

with open("config.json") as f:
    config = json.load(f)


def send_email(sender_name, receiver_emails, release_title, publish_date, release_id):
    smtp_server = config.get("smtp_server")
    smtp_port = 587
    
    email_username = config.get("sender_email")
    email_password = config.get("sender_password")
    sender_email = config.get("sender_email")

    # Create message
    message = MIMEMultipart()
    message["From"] = f"{sender_name} <{sender_email}>"
    message["Subject"] = f"Uusi tiedote: {release_title}"

    # Body of the email (HTML version)
    email_html_body = f"""
    <html>
      <body>
        <p>Hei,</p>
        <p>PRESSI-palvelussa on uusi lehdistö- ja mediatiedote.</p>
        <br>
        <p>Alla tietoa tiedotteesta:</p>
        <h1>{release_title}</h1>
        <p><strong>Julkaistu:</strong> {publish_date}</p>
        <p>Tästä pääset lukemaan koko tiedotteen: <a href="https://pressi.luova.club/releases/{release_id}">linkki</a></p>
        <p>Ystävällisin terveisin,</p>
        <p>{sender_name}</p>
        <p>(Tämä viesti on automaattinen, ethän vastaa siihen.)</p>
      </body>
    </html>
    """
    
    # Body of the email (plain text version)
    email_plain_body = f"""
    Hei,

    PRESSI-palvelussa on uusi lehdistö- ja mediatiedote.

    Alla tietoa tiedotteesta:

    {release_title}
    Julkaistu: {publish_date}

    Tästä pääset lukemaan koko tiedotteen: https://pressi.luova.club/releases/{release_id}

    Ystävällisin terveisin,
    {sender_name}

    (Tämä viesti on automaattinen, ethän vastaa siihen.)
    """

    message.attach(MIMEText(email_html_body, "html"))
    message.attach(MIMEText(email_plain_body, "plain"))

    # Connect to SMTP server
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Enable TLS encryption
        server.login(email_username, email_password)
        
        # Send email to each recipient
        for receiver_email in receiver_emails:
            message["To"] = receiver_email
            server.sendmail(sender_email, receiver_email, message.as_string())