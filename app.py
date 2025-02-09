import os
from flask import Flask
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Welcome to the Email Writer</h1><p>This will generate and send emails soon.</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
