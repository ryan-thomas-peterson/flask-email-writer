import os
import smtplib
from email.message import EmailMessage
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API Key! Set OPENAI_API_KEY in environment variables.")

openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

# Function to generate an email topic using OpenAI
def generate_topic():
    prompt = "Generate a professional email topic on a general business-related theme."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

# Function to generate email content using OpenAI
def generate_email_content(topic):
    prompt = f"Write a professional email based on the following topic: {topic}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

# Function to send an email
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

# Route to serve the webpage
@app.route('/')
def home():
    return render_template("index.html")

# API route to generate a topic
@app.route('/generate-topic', methods=['POST'])
def generate_topic_route():
    topic = generate_topic()
    return jsonify({"topic": topic})

# API route to generate email content based on topic
@app.route('/generate-email', methods=['POST'])
def generate_email_route():
    data = request.json
    topic = data.get("topic", "")
    if not topic:
        return jsonify({"error": "No topic provided"}), 400
    email_content = generate_email_content(topic)
    return jsonify({"content": email_content})

# API route to send an email
@app.route('/send-email', methods=['POST'])
def send_email_route():
    data = request.json
    to_email = data.get("to_email", "")
    subject = data.get("subject", "")
    body = data.get("body", "")

    if not to_email or not subject or not body:
        return jsonify({"error": "Missing required fields"}), 400

    result = send_email(to_email, subject, body)
    return jsonify({"message": result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)