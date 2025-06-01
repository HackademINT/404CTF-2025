import os

from flask import Flask, render_template
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET", default="WHERE IS ZE DOTENV ?")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

app.run(debug=False, host="0.0.0.0", port=5000)