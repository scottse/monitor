# Send an alert email for a node or website is down.
import smtplib

def send_email():
    alert_from = ""
    alert_to = ""
    hostdown = ""

    with open("alert_msg.txt") as em:
        msg = ''
        msg.set_content(em.read())

        msg[ 'Subject' ] = str(f"Alert Message: {hostdown} is down") # Subject line here
        msg[ 'From' ] = alert_from # Sending email account
        msg[ 'To' ] = alert_to # Receiving email account

    send = smtplib.SMTP("localhost")
    send.send_message(msg)
    send.quit()