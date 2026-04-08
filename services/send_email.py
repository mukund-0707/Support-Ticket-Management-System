import smtplib
from email.mime.text import MIMEText


def send_email(to_email: str, subject: str, body: str):
    print("START EMAIL")
    try:
        sender_email = "mukundpatil0707@gmail.com"
        password = "chxk upzq eoeq mdey"
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = to_email

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.set_debuglevel(1)
            server.starttls()
            server.login(sender_email, password)
            server.send_message(msg)

        print("EMAIL SENT SUCCESS")

    except Exception as e:
        print("ERROR:", e)
