import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_test_email(recipient="test@voidmail.local", subject="Hello from VoidMail", body="This is a test email."):
    sender = "sender@example.com"
    
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the local SMTP server on the configured port
        with smtplib.SMTP('localhost', 2525) as server:
            server.sendmail(sender, [recipient], msg.as_string())
        print(f"Successfully sent email to {recipient}")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    send_test_email()
