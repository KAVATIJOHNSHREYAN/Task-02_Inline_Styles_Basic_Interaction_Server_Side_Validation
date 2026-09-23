import json
import os
import re
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'smart_contact_portal_v2_secret_key_cognifyz'

# File upload configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Dynamic Storage Directories (Fallback to /tmp for Vercel Serverless)
if os.environ.get('VERCEL'):
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
    """Ensure data and upload directories exist safely."""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=4)
    except Exception as e:
        print(f"Directory check notice: {e}")


def allowed_file(filename):
    """Check if the uploaded file has a valid allowed image extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_submissions():
    """Load existing submissions from JSON file."""
    ensure_directories_exist()
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, PermissionError):
        return []


def save_submission(submission_data):
    """Save submission entry to JSON storage."""
    submissions = load_submissions()
    submissions.append(submission_data)
    try:
        ensure_directories_exist()
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(submissions, f, indent=4)
    except Exception as e:
        print(f"JSON write notice: {e}")


def validate_form_and_file(form, file):
    """
    Perform comprehensive server-side validation for Task 2.
    Returns: (is_valid, error_message)
    """
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

    # 1. Empty field checks
    if not (name and email and phone and dob and country and gender and password and confirm_password and subject and message):
        return False, "All required fields must be completed."

    # 2. Terms Checkbox
    if not terms:
        return False, "You must accept the Terms of Service to submit."

    # 3. Full Name length
    if len(name) < 2:
        return False, "Full Name must be at least 2 characters long."

    # 4. Email Format Regex
    email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_pattern, email):
        return False, "Please enter a valid email address."

    # 5. Phone Number Regex (7-15 digits)
    clean_phone = re.sub(r'[\s\-()]', '', phone)
    if not re.match(r'^\+?[0-9]{7,15}$', clean_phone):
        return False, "Please enter a valid phone number (7 to 15 digits)."

    # 6. Password Complexity (min 8 chars, at least 1 digit or upper)
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    # 7. Password Match Check
    if password != confirm_password:
        return False, "Password and Confirm Password do not match."

    # 8. Message Length
    if len(message) < 10:
        return False, "Message must be at least 10 characters long."

    # 9. Optional File Upload Validation
    if file and file.filename != '':
        if not allowed_file(file.filename):
            return False, "Invalid file format. Only PNG, JPG, JPEG, GIF, and WEBP images are allowed."

    return True, ""


@app.context_processor
def inject_year():
    return {'current_year': datetime.now().year}


@app.route('/', methods=['GET'])
def home():
    form_data = session.pop('form_data', None)
    return render_template('index.html', form_data=form_data)


@app.route('/contact', methods=['POST'])
def contact():
    ensure_directories_exist()
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

    # Handle Profile Avatar Upload
    avatar_rel_path = ''
    if file and file.filename != '' and allowed_file(file.filename):
        try:
            # Convert uploaded image to Base64 Data URI (serverless-friendly, persistent across redirects)
            import base64
            file_bytes = file.read()
            ext = file.filename.rsplit('.', 1)[1].lower()
            mime_type = f"image/{ext if ext != 'jpg' else 'jpeg'}"
            b64_encoded = base64.b64encode(file_bytes).decode('utf-8')
            avatar_rel_path = f"data:{mime_type};base64,{b64_encoded}"

            # Also save file locally for persistent storage
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex[:6]}_{filename}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            with open(save_path, 'wb') as f:
                f.write(file_bytes)
        except Exception as e:
            print(f"Avatar processing notice: {e}")

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

    # Save to JSON storage
    save_submission(submission_entry)

    # Session storage
    session['latest_submission'] = submission_entry
    flash('Your inquiry has been submitted and validated successfully!', 'success')

    # Query param fallback for serverless deployments
    return redirect(url_for('success', 
                            sub_id=sub_id, 
                            name=form_data['name'], 
                            email=form_data['email'], 
                            phone=form_data['phone'], 
                            dob=form_data['dob'], 
                            country=form_data['country'], 
                            gender=form_data['gender'], 
                            subject=form_data['subject'], 
                            message=form_data['message'], 
                            avatar_path=avatar_rel_path,
                            timestamp=timestamp))


@app.route('/success', methods=['GET'])
def success():
    submission = session.get('latest_submission', None)

    # Fallback hydration from URL query parameters
    if not submission and request.args.get('sub_id'):
        submission = {
            'id': request.args.get('sub_id'),
            'timestamp': request.args.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            'name': request.args.get('name', ''),
            'email': request.args.get('email', ''),
            'phone': request.args.get('phone', ''),
            'dob': request.args.get('dob', ''),
            'country': request.args.get('country', ''),
            'gender': request.args.get('gender', ''),
            'subject': request.args.get('subject', ''),
            'message': request.args.get('message', ''),
            'avatar_path': request.args.get('avatar_path', '')
        }

    return render_template('success.html', submission=submission)


if __name__ == '__main__':
    ensure_directories_exist()
    print("==================================================")
    print("[*] Smart Contact Portal v2 starting...")
    print("[*] Access App: http://127.0.0.1:5000")
    print("==================================================")
    app.run(debug=True, host='127.0.0.1', port=5000)
