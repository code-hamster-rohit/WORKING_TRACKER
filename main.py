from dotenv import load_dotenv
load_dotenv()
from rules import add, get, get_all, update, update_all, delete
from flask import Flask, send_from_directory, render_template, request, session, redirect, url_for
from auth import decode_token, extract_info
from datetime import datetime
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
    return render_template('dashboard.html', user_data=session['user_data'], today=datetime.now().strftime('%Y-%m-%d'))

@app.route('/settings')
def settings():
    if 'user_data' not in session:
        return redirect(url_for('home'))
    return render_template('settings.html', user_data=session['user_data'], today=datetime.now().strftime('%Y-%m-%d'))

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
    
@app.route('/add_hq_details', methods=['POST'])
def add_hq_details():
    if 'user_data' not in session:
        return redirect(url_for('home'))
    try:
        data = request.json
        for item in data:
            add('WORKING_TRACKER', 'HQ_DETAILS', item)
        return {'status_code': 200, 'message': 'HQ Details Added Successfully'}
    except Exception as e:
        return {'status_code': 500, 'error': str(e)}

@app.route('/get_hq_details')
def get_hq_details():
    if 'user_data' not in session:
        return redirect(url_for('home'))
    try:
        data = get_all('WORKING_TRACKER', 'HQ_DETAILS', {})
        for item in data: del item['_id']
        return {'status_code': 200, 'data': data}
    except Exception as e:
        return {'status_code': 500, 'error': str(e)}

@app.route('/update_hq_details', methods=['POST'])
def update_hq_details():
    if 'user_data' not in session:
        return redirect(url_for('home'))
    try:
        data = request.json
        for item in data:
            update('WORKING_TRACKER', 'HQ_DETAILS', {'mr_name': item['mr_name'], 'wp_name': item['old_wp_name']}, {'wp_name': item['new_wp_name']})
        return {'status_code': 200, 'message': 'HQ Details Updated Successfully'}
    except Exception as e:
        return {'status_code': 500, 'error': str(e)}

@app.route('/update_mr_details', methods=['POST'])
def update_mr_details():
    if 'user_data' not in session:
        return redirect(url_for('home'))
    try:
        data = request.json
        for item in data:
            update_all('WORKING_TRACKER', 'HQ_DETAILS', {'mr_name': item['old_mr_name']}, {'mr_name': item['new_mr_name']})
        return {'status_code': 200, 'message': 'MR Details Updated Successfully'}
    except Exception as e:
        return {'status_code': 500, 'error': str(e)}

@app.route('/add_working', methods=['POST'])
def add_working():
    if 'user_data' not in session:
        return redirect(url_for('home'))
    try:
        data = request.json
        add('WORKING_TRACKER', 'WORKING_DETAILS', data)
        return {'status_code': 200, 'message': 'Working Details Added Successfully'}
    except Exception as e:
        return {'status_code': 500, 'error': str(e)}

@app.route('/get_working_details', methods=['GET'])
def get_working_details():
    if 'user_data' not in session:
        return redirect(url_for('home'))
    try:
        data = get_all('WORKING_TRACKER', 'WORKING_DETAILS', {})
        for item in data: del item['_id']
        return {'status_code': 200, 'data': data}
    except Exception as e:
        return {'status_code': 500, 'error': str(e)}

if __name__ == '__main__':
    app.run()
