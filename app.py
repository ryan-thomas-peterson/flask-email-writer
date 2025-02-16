import os
import smtplib
from email.message import EmailMessage
from flask import Flask
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

app = Flask(__name__)

def send_email(to_email, subject, body):
    msg = EmailMessage()
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        return "Email sent successfully!"
    except Exception as e:
        return f"Error sending email: {e}"

@app.route('/')
def home():
    return "<h1>Welcome to the Email Writer</h1><p>This will generate and send emails soon.</p>"

@app.route('/send-test-email')
def send_test_email():
    test_email = "petersonryanace@hotmail.com"  # Replace with your email for testing
    subject = "Test Email from Flask App"
    body = "This is a test email sent from the Flask email app!"
    return send_email(test_email, subject, body)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

