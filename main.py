from dotenv import load_dotenv
load_dotenv()

from flask import Flask, send_from_directory, render_template, request, session
from auth import decode_token, extract_info
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.getenv('SECRET_KEY')

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory('static', 'manifest.json', mimetype='application/manifest+json')

@app.route('/sw.js')
def serve_sw():
    return send_from_directory('static', 'sw.js', mimetype='application/javascript')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user_data' not in session:
        return redirect(url_for('home'))
    return render_template('dashboard.html', user_data=session['user_data'])

@app.route('/auth', methods=['POST'])
def auth():
    try:
        token = request.json['token']
        decoded_token = decode_token(token)
        extracted_info = extract_info(decoded_token, ['email', 'name', 'picture'])
        session['user_data'] = extracted_info
        return {'status_code': 200}
    except Exception as e:
        return {'status_code': 500, 'error': str(e)}