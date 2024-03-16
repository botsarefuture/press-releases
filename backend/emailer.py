import yagmail
import json

with open("config.json") as f:
    config = json.load(f)

def send_email(sender_name, receiver_emails, release_title, publish_date, release_id):
    email_username = config.get("sender_email")
    email_password = config.get("sender_password")

    # Initialize yagmail SMTP connection
    yag = yagmail.SMTP(email_username, email_password, host="mail.luova.club")

    # Construct email content
    email_content = f"""
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

    # Send email to each recipient
    for receiver_email in receiver_emails:
        yag.send(
            to=receiver_email,
            subject=f"Uusi tiedote: {release_title}",
            contents=email_content
        )

if __name__ == '__main__':
    send_email("12", ["vuoreol@gmail.com", "postmaster@luova.club"], "FUCK U", "EILEN", "none")
