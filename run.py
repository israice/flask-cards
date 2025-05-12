import sys
sys.dont_write_bytecode = True  # disable writing .pyc files into **pycache**

from flask import Flask, render_template, redirect, url_for, session, jsonify, abort, send_from_directory, request
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv
import logging
import csv
import subprocess

# CONFIGURATION
load_dotenv()
APP_SECRET = os.getenv('SESSION_SECRET')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
SYSTEM_FULL_DB_CSV = os.getenv('SYSTEM_FULL_DB_CSV')
AUTH_USERS_CSV = os.getenv('AUTH_USERS')  # path to file for authenticated users logging
TEMPLATE_FOLDER = os.getenv('TEMPLATE_FOLDER')
CARDS_FOLDER = os.getenv('CARDS_BANK_FOLDER')
if os.getenv('PORT') is None:
    raise SystemExit("PORT must be set in .env")
PORT = int(os.getenv('PORT'))
required_envs = {
    'SESSION_SECRET': APP_SECRET,
    'TEMPLATE_FOLDER': TEMPLATE_FOLDER,
    'CARDS_BANK_FOLDER': CARDS_FOLDER,
    'SYSTEM_FULL_DB_CSV': SYSTEM_FULL_DB_CSV,
    'AUTH_USERS': AUTH_USERS_CSV,
}
for name, val in required_envs.items():
    if not val:
        raise SystemExit(f"{name} must be set in .env")

# Silence werkzeug logs
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.CRITICAL)

app = Flask(__name__, template_folder=TEMPLATE_FOLDER)
app.secret_key = APP_SECRET

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# UTILS

def load_csv_data():
    """Load CSV and return list of records and list of column names"""
    if not os.path.exists(SYSTEM_FULL_DB_CSV):
        return [], []
    with open(SYSTEM_FULL_DB_CSV, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        records = []
        for row in reader:
            if None in row.values():
                raise ValueError("CSV contains missing (None) values")
            records.append(dict(row))
        columns = reader.fieldnames or []
    return records, columns


def get_admin_emails(records):
    """Extract set of admin emails from CSV records"""
    admin_emails = set()
    for row in records:
        user_type = row.get('USER_TYPE', '').strip().upper()
        card_owner = row.get('CARD_OWNER', '').strip().lower()
        if user_type == 'ADMIN' and card_owner:
            admin_emails.add(card_owner)
    return admin_emails


def get_user_cards(email, records, columns):
    """Filter records for given email and find matching card images"""
    if 'CARD_ID' not in columns or 'CARD_OWNER' not in columns:
        raise ValueError("CSV must have 'CARD_ID' and 'CARD_OWNER' columns")
    user_cards = []
    for record in records:
        if record.get('CARD_OWNER') == email:
            card_id = record['CARD_ID']
            for ext in ['.png', '.jpg', '.jpeg']:
                fname = card_id + ext
                if os.path.exists(os.path.join(CARDS_FOLDER, fname)):
                    url = url_for('card_image', filename=fname)
                    user_cards.append({
                        'CARD_ID': card_id,
                        'url': url,
                        'transactions': record.get('TRANSACTIONS', ''),
                        'balance': record.get('BALANCE', ''),
                        'status': record.get('STATUS', '')
                    })
                    break
    return user_cards

# INITIAL SETUP (retain loading for other endpoints)
SYSTEM_RECORDS, SYSTEM_COLUMNS = load_csv_data()
ADMIN_EMAILS = get_admin_emails(SYSTEM_RECORDS)
KEY_TO_CARD_ID = {row.get('CARD_URL', ''): row.get('CARD_ID', '') for row in SYSTEM_RECORDS}

# ROUTES

@app.route('/')
def root():
    """Redirect to login page"""
    return redirect(url_for('login'))

@app.route('/login')
def login():
    """Render login template"""
    return render_template('login.html')

@app.route('/google-login')
def google_login():
    """Initiate Google OAuth flow"""
    next_page = request.args.get('next')
    if next_page:
        session['next_page'] = next_page
        if next_page == 'add_card_owner':
            session['ref_url'] = request.referrer
    return google.authorize_redirect(url_for('authorize', _external=True))

@app.route('/auth/google/callback')
def authorize():
    """Handle Google OAuth callback and set session user"""
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo', {})
        email = user_info.get('email', '').strip().lower()
        if not email:
            return redirect(url_for('login'))
        session['user'] = {'email': email}
        next_page = session.pop('next_page', None)
        if next_page == 'add_card_owner':
            if AUTH_USERS_CSV:
                os.makedirs(os.path.dirname(AUTH_USERS_CSV), exist_ok=True)
                with open(AUTH_USERS_CSV, 'a', newline='', encoding='utf-8') as f:
                    csv.writer(f).writerow([email, session.pop('ref_url', '')])
            try:
                subprocess.run(
                    ['python', 'core/BACKEND/D_change_card_owner/D_run_change_card_owner.py'],
                    check=True
                )
            except subprocess.CalledProcessError:
                pass
            return redirect(url_for('profile'))
        if next_page and next_page in app.view_functions:
            return redirect(url_for(next_page))
        return redirect(url_for('profile'))
    except Exception as e:
        print(f"Error in authorize: {e}")
        return redirect(url_for('login'))

@app.route('/profile')
def profile():
    """Render user profile with cards and always show table button for admins"""
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    email = user['email']
    # Reload CSV data to reflect any changes from add_card_owner
    records, columns = load_csv_data()
    admin_emails = get_admin_emails(records)
    is_admin = email in admin_emails
    try:
        cards = get_user_cards(email, records, columns)
    except Exception:
        cards = []
    return render_template('profile.html', user=user, is_admin=is_admin, cards=cards)

@app.route('/logout')
def logout():
    """Clear session and redirect to login"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/table')
def table():
    """Render admin table view"""
    user = session.get('user')
    # Ensure ADMIN_EMAILS is up-to-date
    records, _ = load_csv_data()
    admin_emails = get_admin_emails(records)
    if not user or user['email'] not in admin_emails:
        return redirect(url_for('profile'))
    return render_template('table.html', user=user)

@app.route('/get_users')
def get_users():
    """Return fresh JSON with CSV data for AJAX updating"""
    records, columns = load_csv_data()  # reload CSV on each request
    return jsonify({'columns': columns, 'records': records})

@app.route('/api/cards')
def api_cards():
    """Return JSON list of user cards for AJAX updating"""
    user = session.get('user')
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    email = user['email']
    records, columns = load_csv_data()
    cards = get_user_cards(email, records, columns)
    return jsonify(cards)

@app.route('/card/<path:key>')
def serve_card_page(key):
    """Serve individual card page for adding card owner"""
    full_url = f'https://nakama.wfork.org/card/{key}'
    if full_url not in KEY_TO_CARD_ID:
        abort(404)
    card_id = KEY_TO_CARD_ID[full_url]
    image_url = next(
        (f'/card_image/{card_id + ext}' for ext in ['.png', '.jpg', '.jpeg']
         if os.path.exists(os.path.join(CARDS_FOLDER, card_id + ext))),
        None
    )
    return render_template('add_card_owner.html', image_url=image_url)

@app.route('/card_image/<filename>')
def card_image(filename):
    """Serve card image files"""
    return send_from_directory(CARDS_FOLDER, filename)

# NEW ROUTE: Trigger card creation script
@app.route('/run_create_cards', methods=['POST'])
def run_create_cards():
    """Run the A_run_create_cards.py script on button click"""
    user = session.get('user')
    # Reload admin list to ensure up-to-date permissions
    records, _ = load_csv_data()
    admin_emails = get_admin_emails(records)
    if not user or user['email'] not in admin_emails:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    try:
        subprocess.run(
            ['python', os.path.join('core', 'BACKEND', 'A_create_cards', 'A_run_create_cards.py')],
            check=True
        )
        return jsonify({'status': 'success'})
    except subprocess.CalledProcessError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.errorhandler(404)
def page_not_found(e):
    """Render custom 404 page"""
    return render_template('404.html'), 404

if __name__ == '__main__':
    print(f"- - https://nakama.wfork.org")
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)
