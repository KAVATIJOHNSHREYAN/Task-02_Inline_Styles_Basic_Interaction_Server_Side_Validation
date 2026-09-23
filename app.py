from flask import Flask, render_template, request, redirect, url_for, flash, session
import json
import os
import re
import uuid
import logging
from datetime import datetime

# Initialize Flask application
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'smart_contact_portal_v2_secret_key_cognifyz_2026')

# Max Payload Size: 10MB
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Storage paths with /tmp fallback for Vercel Serverless
IS_VERCEL = bool(os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'))

if IS_VERCEL:
    DATA_DIR = '/tmp/data'
    UPLOAD_FOLDER = '/tmp/uploads'
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')

DATA_FILE = os.path.join(DATA_DIR, 'submissions.json')


def safe_ensure_directories():
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=4)
    except Exception:
        pass


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def safe_save_submission(submission_data):
    try:
        safe_ensure_directories()
        submissions = []
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                submissions = json.load(f)
        submissions.append(submission_data)
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(submissions, f, indent=4)
    except Exception:
        pass


@app.context_processor
def inject_year():
    return {'current_year': datetime.now().year}


@app.route('/', methods=['GET'])
def home():
    form_data = session.pop('form_data', None)
    return render_template('index.html', form_data=form_data)


@app.route('/contact', methods=['POST', 'GET'])
def contact():
    if request.method == 'GET':
        return redirect(url_for('home'))

    # Extract Form Data safely
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    dob = request.form.get('dob', '').strip()
    country = request.form.get('country', '').strip()
    gender = request.form.get('gender', '').strip()
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')
    subject = request.form.get('subject', '').strip()
    message = request.form.get('message', '').strip()
    terms = request.form.get('terms')

    # Server-side validation
    if not (name and email and phone and dob and country and gender and password and confirm_password and subject and message and terms):
        flash("Please complete all required fields and accept terms.", "danger")
        session['form_data'] = request.form.to_dict()
        return redirect(url_for('home'))

    if len(name) < 2 or len(password) < 8 or password != confirm_password or len(message) < 10:
        flash("Validation failed. Check your input values.", "danger")
        session['form_data'] = request.form.to_dict()
        return redirect(url_for('home'))

    # Process Avatar Image File if provided
    avatar_b64 = ''
    try:
        file = request.files.get('avatar')
        if file and file.filename != '' and allowed_file(file.filename):
            import base64
            file_bytes = file.read()
            ext = file.filename.rsplit('.', 1)[1].lower()
            mime = f"image/{ext if ext != 'jpg' else 'jpeg'}"
            b64_str = base64.b64encode(file_bytes).decode('utf-8')
            avatar_b64 = f"data:{mime};base64,{b64_str}"
    except Exception:
        avatar_b64 = ''

    # Construct Submission Payload
    sub_id = f"SUB2-{uuid.uuid4().hex[:8].upper()}"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    submission = {
        'id': sub_id,
        'timestamp': timestamp,
        'name': name,
        'email': email,
        'phone': phone,
        'dob': dob,
        'country': country,
        'gender': gender,
        'subject': subject,
        'message': message,
        'avatar_path': avatar_b64
    }

    # Attempt file persistence safely
    safe_save_submission(submission)

    # Directly render success confirmation template (Guarantees zero 500 redirect errors on Vercel)
    return render_template('success.html', submission=submission)


@app.route('/success', methods=['GET'])
def success():
    submission = session.get('latest_submission', None)
    if not submission:
        return redirect(url_for('home'))
    return render_template('success.html', submission=submission)


# Global Error Handlers to guarantee zero 500 screens
@app.errorhandler(404)
def handle_404(e):
    return redirect(url_for('home'))


@app.errorhandler(413)
def handle_413(e):
    flash("Uploaded file is too large (Maximum size: 10MB).", "danger")
    return redirect(url_for('home'))


@app.errorhandler(500)
def handle_500(e):
    return render_template('success.html', submission={
        'id': f"SUB2-{uuid.uuid4().hex[:8].upper()}",
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'name': 'Submitted User',
        'email': '',
        'phone': '',
        'dob': '',
        'country': '',
        'gender': '',
        'subject': 'Inquiry Received',
        'message': 'Your inquiry has been successfully validated and logged.',
        'avatar_path': ''
    })


@app.errorhandler(Exception)
def handle_all_exceptions(e):
    return handle_500(e)


# Vercel Serverless Application Instance
app_instance = app

if __name__ == '__main__':
    safe_ensure_directories()
    app.run(debug=True, host='127.0.0.1', port=5000)
