# Send an alert email for a node or website is down.
import smtplib
from email import EmailMessage

msg_from = "<email@example.com"
msg_to = "email@example.com"
msg_content = f"{} is down"

e = EmailMessage()
e["From"] = msg_from
e["To"] = msg_to
e["Subject"] = f"{} is down"

send = smtplib.SMTP("<SMTP of email provider")
send.starttls()
send.login(msg_from, "<Password")
send.sendmail(msg_from, msg_to, e.as_string)
send.quit()