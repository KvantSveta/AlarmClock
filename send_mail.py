import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

__author__ = "Evgeny Goncharov"


def send_mail(message):
    with open("user.data", "r") as f:
        json_data = f.read()

    json_data = json.loads(json_data)

    login = json_data["login"]
    password = json_data["password"]
    email_from = json_data["email_from"]
    email_to = json_data["email_to"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Alert"
    msg["From"] = email_from
    msg["To"] = email_to

    html = """
    <html>
        <body>
            <p>{0}</p>
            <p>{1}</p>
        </body>
    </html>
    """.format(email_from, message)
    part2 = MIMEText(html, "html")

    msg.attach(part2)

    smtp_client = smtplib.SMTP_SSL("smtp.gmail.com")
    smtp_client.login(login, password)
    smtp_client.sendmail(from_addr=email_from, to_addrs=email_to, msg=msg.as_string())
    smtp_client.quit()
