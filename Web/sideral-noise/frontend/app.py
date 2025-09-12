from flask import Flask, render_template, jsonify, request
from nanoid import generate
from os import environ
from bot import fetch_noise
from re import match
from waitress import serve

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/noise', methods=['POST'])
def noise():
    content = request.json
    noise_id = content['noise_id'] if match(r'^[A-Za-z0-9_-]{21}$', content.get('noise_id','')) else generate()
    noise = fetch_noise(noise_id)
    return jsonify({'noise': noise})

if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=environ.get('PORT', 5000))