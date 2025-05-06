import sys
sys.dont_write_bytecode = True  # disable writing .pyc files into __pycache__

from flask import Flask, render_template, redirect, url_for, session, jsonify, abort, send_from_directory, request
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv
import logging
import csv
import subprocess

# ─── CONFIGURATION ──────────────────────────────────────────────────────────────
load_dotenv()

APP_SECRET = os.getenv('SESSION_SECRET')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

SYSTEM_FULL_DB_CSV = os.getenv('SYSTEM_FULL_DB_CSV')
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
}
for name, val in required_envs.items():
    if not val:
        raise SystemExit(f"{name} must be set in .env")

werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.CRITICAL)

app = Flask(__name__, template_folder=TEMPLATE_FOLDER)
app.secret_key = APP_SECRET

# google OAuth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# ─── UTILS ──────────────────────────────────────────────────────────────────────

def load_csv_data():
    if not os.path.exists(SYSTEM_FULL_DB_CSV):
        return [], []
    with open(SYSTEM_FULL_DB_CSV, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        records = []
        for row in reader:
            # Raise error if any value is None (enforce complete data)
            if None in row.values():
                raise ValueError("CSV contains missing (None) values")
            records.append(dict(row))
        columns = reader.fieldnames
        if not columns:
            raise ValueError("CSV header is missing or empty")
        return records, columns

def get_admin_emails(records):
    admin_emails = set()
    for row in records:
        if 'USER_TYPE' not in row or 'CARD_OWNER' not in row:
            raise KeyError("CSV row missing 'USER_TYPE' or 'CARD_OWNER'")
        user_type = row['USER_TYPE'].strip().upper()
        card_owner = row['CARD_OWNER'].strip().lower()
        if user_type == 'ADMIN' and card_owner:
            admin_emails.add(card_owner)
    return admin_emails

def get_user_cards(email, records, columns):
    if 'CARD_ID' not in columns or 'CARD_OWNER' not in columns:
        raise ValueError("CSV must have 'CARD_ID' and 'CARD_OWNER' columns")
    user_cards = []
    for record in records:
        if 'CARD_OWNER' not in record or 'CARD_ID' not in record:
            raise KeyError("CSV record missing 'CARD_OWNER' or 'CARD_ID'")
        if record['CARD_OWNER'] == email:
            card_id = record['CARD_ID']
            for ext in ['.png', '.jpg', '.jpeg']:
                fname = card_id + ext
                if os.path.exists(os.path.join(CARDS_FOLDER, fname)):
                    url = url_for('card_image', filename=fname)
                    user_cards.append({'CARD_ID': card_id, 'url': url})
                    break
    return user_cards

# ─── INITIAL SETUP ──────────────────────────────────────────────────────────────

SYSTEM_RECORDS, SYSTEM_COLUMNS = load_csv_data()
KEY_TO_CARD_ID = {}
for row in SYSTEM_RECORDS:
    if 'CARD_URL' not in row or 'CARD_ID' not in row:
        raise KeyError("CSV record missing 'CARD_URL' or 'CARD_ID'")
    KEY_TO_CARD_ID[row['CARD_URL']] = row['CARD_ID']
ADMIN_EMAILS = get_admin_emails(SYSTEM_RECORDS)

# ─── ROUTES ─────────────────────────────────────────────────────────────────────

@app.route('/')
def root():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/google-login')
def google_login():
    next_page = request.args.get('next')
    if next_page:
        session['next_page'] = next_page
    return google.authorize_redirect(url_for('authorize', _external=True))

@app.route('/auth/google/callback')
def authorize():
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        if user_info and 'email' in user_info:
            email = user_info['email']
            session['user'] = {'email': email}
            next_page = session.pop('next_page', None)
            if next_page == 'add_card_owner':
                try:
                    subprocess.run(['python', 'core/BACKEND/D_change_card_owner/D_run_change_card_owner.py'], check=True)
                except subprocess.CalledProcessError:
                    pass
            return redirect(url_for('profile'))
    except Exception as e:
        print(f"Error in authorize: {e}")
    return '', 204

@app.route('/profile')
def profile():
    user = session.get('user')
    if not user or 'email' not in user:
        return redirect(url_for('login'))

    user_email = user['email'].strip().lower()
    is_admin = user_email in ADMIN_EMAILS

    try:
        user_cards = get_user_cards(user_email, SYSTEM_RECORDS, SYSTEM_COLUMNS)
    except Exception as e:
        print(f"Error loading user cards: {e}")
        user_cards = []

    return render_template('profile.html', user=user, is_admin=is_admin, cards=user_cards)

@app.route('/logout')
def logout():
    try:
        session.clear()
        return redirect(url_for('login'))
    except Exception as e:
        print(f"Error in /logout: {e}")
        return "Internal Server Error", 500

@app.route('/table')
def table():
    user = session.get('user')
    if not user or 'email' not in user:
        return redirect(url_for('login'))

    user_email = user['email'].strip().lower()
    if user_email not in ADMIN_EMAILS:
        return redirect(url_for('profile'))

    return render_template('table.html', user=user)

@app.route('/get_users')
def get_users():
    return jsonify({'columns': SYSTEM_COLUMNS, 'records': SYSTEM_RECORDS})

@app.route('/card/<path:key>')
def serve_card_page(key):
    full_url = f'http://localhost:{PORT}/card/{key}'
    if full_url in KEY_TO_CARD_ID:
        card_id = KEY_TO_CARD_ID[full_url]
        image_url = next(
            (f'/card_image/{card_id + ext}' for ext in ['.png', '.jpg', '.jpeg']
             if os.path.exists(os.path.join(CARDS_FOLDER, card_id + ext))),
            None
        )
        return render_template('add_card_owner.html', image_url=image_url)
    else:
        abort(404)

@app.route('/card_image/<filename>')
def card_image(filename):
    return send_from_directory(CARDS_FOLDER, filename)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    print(f"- - http://localhost:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)
