from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Welcome to the Email Writer</h1><p>This will generate and send emails soon.</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
