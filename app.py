from flask import Flask, request, jsonify, render_template
import openai
import smtplib
import os
import json
from dotenv import load_dotenv
from email.mime.text import MIMEText

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API Key! Set OPENAI_API_KEY in environment variables.")

openai_client = openai.Client(api_key=OPENAI_API_KEY)

app = Flask(__name__)

# OpenAI API Key

@app.route('/')
def home():
    return render_template("index.html")
    
# Function to generate a topic
@app.route('/generate-topic', methods=['POST'])
def generate_topic():
    data = request.get_json()
    category = data.get("prompt", "general political issues")  # Fixed: Now correctly gets prompt input
    prompt = f"Generate an impactful email topic about current frustrations with the US government around {category}."  # Fixed f-string formatting
    
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}]
    )
    topic = response["choices"][0]["message"]["content"]
    return jsonify({"topic": topic})

# Function to generate email content
@app.route('/generate-email', methods=['POST'])
def generate_email():
    data = request.get_json()
    topic = data.get("topic", "General Email Topic")
    prompt = data.get("prompt", "")
    current_content = data.get("content", "")
    
    email_prompt = f"Write a professional, impactful email directed at leaders and decision makers about US government and corporations frustrations around: {topic}.  The message should include references to founding documents, provide well reasoned logic about why current actions are wrong and damaging to society as awhole"
    if prompt:
        email_prompt += f" Consider the following user input: {prompt}."
    if current_content:
        email_prompt += f" Improve or refine this existing content: {current_content}."
    
    email_prompt += " Include the sender's details: Ryan Peterson, 44-year-old married father of two, living in Madison, WI, working as a healthcare analyst."
    
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": email_prompt}]
    )
    content = response["choices"][0]["message"]["content"]
    return jsonify({"content": content})

# Function to suggest a contact
@app.route('/suggest-contact', methods=['POST'])
def suggest_contact():
    data = request.get_json()
    topic = data.get("topic", "")
    content = data.get("content", "")
    
    contact_prompt = f"Based on the following email topic: '{topic}' and content: '{content}', suggest the most relevant recipient who would have the most impact. Provide the contact's email address and a brief reason why they are the best choice in the format: 'Email: example@email.com Reason: They are a key decision-maker in this field.'"

    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "systme", "content": contact_prompt}]
    )

    # Extract response content
    contact_response = response["choices"][0]["message"]["content"]

    # Parsing email and reason from response
    email = "Unknown"
    reason = "No reason provided."
    
    if "Email:" in contact_response and "Reason:" in contact_response:
        parts = contact_response.split("Reason:")
        email = parts[0].replace("Email:", "").strip()
        reason = parts[1].strip()

    return jsonify({"email": email, "reason": reason})

# Function to send an email
@app.route('/send-email', methods=['POST'])
def send_email():
    data = request.get_json()
    to_email = data.get("to_email")
    subject = data.get("subject")
    body = data.get("body")
    
    if not to_email or not subject or not body:
        return jsonify({"message": "Missing email fields"}), 400
    
    from_email = os.getenv("EMAIL_ADDRESS")
    app_password = os.getenv("EMAIL_APP_PASSWORD")

    # Safeguard for missing credentials
    if not from_email or not app_password:
        return jsonify({"message": "Email credentials not configured properly"}), 500
    
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(from_email, app_password)
            server.sendmail(from_email, to_email, msg.as_string())
        return jsonify({"message": "Email sent successfully!"})
    except Exception as e:
        return jsonify({"message": f"Failed to send email: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))  # Get port from environment, default to 5000 if missing
    app.run(host='0.0.0.0', port=port, debug=True)