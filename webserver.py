from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def start_web():
    thread = threading.Thread(target=run)
    thread.start()