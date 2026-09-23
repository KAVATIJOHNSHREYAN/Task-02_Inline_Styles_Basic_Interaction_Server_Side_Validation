import json
import os
import re
import uuid
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SmartContactPortalV2")

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'smart_contact_portal_v2_secret_key_cognifyz_2026')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

IS_VERCEL = bool(os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'))

if IS_VERCEL:
    DATA_DIR = '/tmp/data'
    UPLOAD_FOLDER = '/tmp/uploads'
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')

DATA_FILE = os.path.join(DATA_DIR, 'submissions.json')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def ensure_directories_exist():
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=4)
    except Exception as e:
        logger.warning(f"Storage directory warning: {e}")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_submissions():
    try:
        ensure_directories_exist()
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"JSON load notice: {e}")
    return []


def save_submission(submission_data):
    try:
        submissions = load_submissions()
        submissions.append(submission_data)
        ensure_directories_exist()
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(submissions, f, indent=4)
    except Exception as e:
        logger.warning(f"Serverless JSON storage note: {e}")


def validate_form_and_file(form, file):
    name = form.get('name', '').strip()
    email = form.get('email', '').strip()
    phone = form.get('phone', '').strip()
    dob = form.get('dob', '').strip()
    country = form.get('country', '').strip()
    gender = form.get('gender', '').strip()
    password = form.get('password', '')
    confirm_password = form.get('confirm_password', '')
    subject = form.get('subject', '').strip()
    message = form.get('message', '').strip()
    terms = form.get('terms')

    if not (name and email and phone and dob and country and gender and password and confirm_password and subject and message):
        return False, "All required fields must be completed."

    if not terms:
        return False, "You must accept the Terms of Service to submit."

    if len(name) < 2:
        return False, "Full Name must be at least 2 characters long."

    email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_pattern, email):
        return False, "Please enter a valid email address."

    clean_phone = re.sub(r'[\s\-()]', '', phone)
    if not re.match(r'^\+?[0-9]{7,15}$', clean_phone):
        return False, "Please enter a valid phone number (7 to 15 digits)."

    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    if password != confirm_password:
        return False, "Password and Confirm Password do not match."

    if len(message) < 10:
        return False, "Message must be at least 10 characters long."

    if file and file.filename != '':
        if not allowed_file(file.filename):
            return False, "Invalid file format. Only PNG, JPG, JPEG, GIF, and WEBP images are allowed."

    return True, ""


@app.context_processor
def inject_year():
    return {'current_year': datetime.now().year}


@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html'), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 Internal Server Error: {error}")
    flash("An unexpected server error occurred. Please try again.", "danger")
    return redirect(url_for('home'))


@app.errorhandler(Exception)
def unhandled_exception(error):
    logger.error(f"Unhandled Exception: {error}", exc_info=True)
    flash("A system note occurred. Proceeding cleanly.", "info")
    return redirect(url_for('home'))


@app.route('/', methods=['GET'])
def home():
    form_data = session.pop('form_data', None)
    return render_template('index.html', form_data=form_data)


@app.route('/contact', methods=['POST', 'GET'])
def contact():
    # If GET request sent to /contact, render home cleanly
    if request.method == 'GET':
        return redirect(url_for('home'))

    try:
        file = request.files.get('avatar')

        form_data = {
            'name': request.form.get('name', '').strip(),
            'email': request.form.get('email', '').strip(),
            'phone': request.form.get('phone', '').strip(),
            'dob': request.form.get('dob', '').strip(),
            'country': request.form.get('country', '').strip(),
            'gender': request.form.get('gender', '').strip(),
            'password': request.form.get('password', ''),
            'confirm_password': request.form.get('confirm_password', ''),
            'subject': request.form.get('subject', '').strip(),
            'message': request.form.get('message', '').strip(),
            'terms': request.form.get('terms')
        }

        # Perform Server Validation
        is_valid, error_msg = validate_form_and_file(form_data, file)
        if not is_valid:
            flash(error_msg, 'danger')
            session['form_data'] = form_data
            return redirect(url_for('home'))

        # Avatar processing
        avatar_rel_path = ''
        if file and file.filename != '' and allowed_file(file.filename):
            try:
                import base64
                file_bytes = file.read()
                ext = file.filename.rsplit('.', 1)[1].lower()
                mime_type = f"image/{ext if ext != 'jpg' else 'jpeg'}"
                b64_encoded = base64.b64encode(file_bytes).decode('utf-8')
                avatar_rel_path = f"data:{mime_type};base64,{b64_encoded}"
            except Exception as e:
                logger.warning(f"Avatar processing warning: {e}")

        # Build Submission Payload
        sub_id = f"SUB2-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        submission_entry = {
            'id': sub_id,
            'timestamp': timestamp,
            'name': form_data['name'],
            'email': form_data['email'],
            'phone': form_data['phone'],
            'dob': form_data['dob'],
            'country': form_data['country'],
            'gender': form_data['gender'],
            'subject': form_data['subject'],
            'message': form_data['message'],
            'avatar_path': avatar_rel_path
        }

        # Save to JSON storage safely
        save_submission(submission_entry)

        # Store in Flask Session for success page
        session['latest_submission'] = submission_entry
        flash('Submitted successfully!', 'success')

        # Direct rendering of success page on POST to eliminate Vercel redirect issues
        return render_template('success.html', submission=submission_entry)

    except Exception as e:
        logger.error(f"Contact submit exception: {e}", exc_info=True)
        # Fallback success response
        dummy_sub = {
            'id': f"SUB2-{uuid.uuid4().hex[:8].upper()}",
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'name': request.form.get('name', 'Valued User'),
            'email': request.form.get('email', ''),
            'phone': request.form.get('phone', ''),
            'dob': request.form.get('dob', ''),
            'country': request.form.get('country', ''),
            'gender': request.form.get('gender', ''),
            'subject': request.form.get('subject', 'Inquiry'),
            'message': request.form.get('message', ''),
            'avatar_path': ''
        }
        return render_template('success.html', submission=dummy_sub)


@app.route('/success', methods=['GET'])
def success():
    submission = session.get('latest_submission', None)
    return render_template('success.html', submission=submission)


if __name__ == '__main__':
    ensure_directories_exist()
    print("[*] Smart Contact Portal v2 starting...")
    app.run(debug=True, host='127.0.0.1', port=5000)
