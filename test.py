import sys
sys.dont_write_bytecode = True  # disable writing .pyc files into __pycache__

from flask import Flask, render_template, redirect, url_for, session, jsonify, Response, abort, send_from_directory
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv
import pandas as pd
import json
import time
import logging
import csv

# ─── CONFIGURATION ──────────────────────────────────────────────────────────────
load_dotenv()

# Setup application logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Application secrets and OAuth credentials
APP_SECRET = os.getenv('SESSION_SECRET')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

# Paths from .env
AUTH_USERS = os.getenv('AUTH_USERS')
SYSTEM_ADMIN_CSV = os.getenv('SYSTEM_ADMIN_CSV')
SYSTEM_CARDS_CSV = os.getenv('SYSTEM_CARDS_CSV')
TEMPLATE_FOLDER = os.getenv('TEMPLATE_FOLDER')
SYSTEM_CARD_AUTH_CSV = os.getenv('SYSTEM_CARD_AUTH_SCV')  # CSV for key-to-card mappings
CARDS_FOLDER = os.getenv('CARDS_BANK_FOLDER')             # Folder for card images

# Server port
PORT = int(os.getenv('PORT', 5000))

# Validate mandatory environment variables
required_envs = {
    'SESSION_SECRET': APP_SECRET,
    'AUTH_USERS': AUTH_USERS,
    'SYSTEM_ADMIN_CSV': SYSTEM_ADMIN_CSV,
    'SYSTEM_CARDS_CSV': SYSTEM_CARDS_CSV,
    'TEMPLATE_FOLDER': TEMPLATE_FOLDER,
    'SYSTEM_CARD_AUTH_SCV': SYSTEM_CARD_AUTH_CSV,
    'CARDS_BANK_FOLDER': CARDS_FOLDER
}
for name, val in required_envs.items():
    if not val:
        logger.error(f"Environment variable {name} is missing")
        raise SystemExit(f"{name} must be set in .env")

# ─── SUPPRESS FLASK AND WERKZEUG LOGS ───────────────────────────────────────────
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.CRITICAL)

# ─── FLASK & OAUTH SETUP ────────────────────────────────────────────────────────
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

# ─── LOAD MAPPINGS FROM CSV ─────────────────────────────────────────────────────
KEY_TO_CARD_ID = {}
try:
    with open(SYSTEM_CARD_AUTH_CSV, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            KEY_TO_CARD_ID[row['KEY_IN']] = row['CARD_ID']
except Exception as e:
    logger.error(f"Failed to load key-to-card mappings from {SYSTEM_CARD_AUTH_CSV}: {e}")

# ─── HELPER FUNCTIONS ───────────────────────────────────────────────────────────
def load_users():
    """Load CSV of authorized users, return empty if missing or error."""
    if not os.path.exists(AUTH_USERS):
        logger.error(f"Authorized users CSV not found at: {AUTH_USERS}")
        return pd.DataFrame()
    try:
        return pd.read_csv(AUTH_USERS)
    except Exception as e:
        logger.error(f"Error reading authorized users CSV at {AUTH_USERS}: {e}")
        return pd.DataFrame()

def save_user(email):
    """Append new user email to authorized users CSV, log errors."""
    users = load_users()
    if 'email' in users.columns and email not in users['email'].values:
        users = pd.concat([users, pd.DataFrame({'email': [email]})], ignore_index=True)
        try:
            users.to_csv(AUTH_USERS, index=False)
        except Exception as e:
            logger.error(f"Error writing authorized users CSV at {AUTH_USERS}: {e}")

def load_admin_emails():
    """Load admin emails from CSV, return as a set."""
    if not os.path.exists(SYSTEM_ADMIN_CSV):
        logger.error(f"Admin CSV not found at: {SYSTEM_ADMIN_CSV}")
        return set()
    try:
        admins = pd.read_csv(SYSTEM_ADMIN_CSV)
        return set(admins['admin_email'].str.strip().str.lower().values)
    except Exception as e:
        logger.error(f"Error reading admin CSV at {SYSTEM_ADMIN_CSV}: {e}")
        return set()

def load_cards():
    """Load system cards data for table view, return DataFrame."""
    if not os.path.exists(SYSTEM_CARDS_CSV):
        logger.error(f"System cards CSV not found at {SYSTEM_CARDS_CSV}")
        return pd.DataFrame(columns=['CARD_ID','PACK_ID','OWNER'])
    try:
        return pd.read_csv(SYSTEM_CARDS_CSV)
    except Exception as e:
        logger.error(f"Error reading system cards CSV at {SYSTEM_CARDS_CSV}: {e}")
        return pd.DataFrame(columns=['CARD_ID','PACK_ID','OWNER'])

def get_user_cards(email):
    """Return list of this user’s card image URLs and IDs."""
    df = load_cards()
    user_df = df[df['OWNER'].str.strip().str.lower() == email.strip().lower()]
    cards = []
    for _, row in user_df.iterrows():
        card_id = row['CARD_ID']
        # detect extension
        for ext in ['.png', '.jpg', '.jpeg']:
            fname = card_id + ext
            if os.path.exists(os.path.join(CARDS_FOLDER, fname)):
                url = url_for('card_image', filename=fname)
                cards.append({'card_id': card_id, 'url': url})
                break
    return cards

# ─── ROUTES ─────────────────────────────────────────────────────────────────────
@app.route('/')
def root():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/google-login')
def google_login():
    return google.authorize_redirect(url_for('authorize', _external=True))

@app.route('/auth/google/callback')
def authorize():
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        if user_info:
            email = user_info.get('email')
            save_user(email)
            session['user'] = {'email': email}
            return redirect(url_for('profile'))
    except Exception as e:
        logger.error(f"Google auth error: {e}")
    return '', 204

@app.route('/profile')
def profile():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    admin_emails = load_admin_emails()
    user_email = user['email'].strip().lower()
    is_admin = user_email in admin_emails

    # load only this user's cards
    user_cards = get_user_cards(user_email)

    return render_template('profile.html',
                           user=user,
                           is_admin=is_admin,
                           cards=user_cards)

@app.route('/table')
def table():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    admin_emails = load_admin_emails()
    user_email = user['email'].strip().lower()
    if user_email not in admin_emails:
        return redirect(url_for('profile'))

    # render admin table view
    return render_template('table.html', user=user)

@app.route('/get_users')
def get_users():
    """Return both columns and records from system cards CSV as JSON."""
    df = load_cards()
    cols = df.columns.tolist()
    records = df.to_dict(orient='records')
    return jsonify({'columns': cols, 'records': records})

@app.route('/stream')
def stream():
    """Server-sent events stream on system cards CSV modifications."""
    def event_stream():
        last_mtime = 0
        while True:
            if os.path.exists(SYSTEM_CARDS_CSV):
                current_mtime = os.path.getmtime(SYSTEM_CARDS_CSV)
                if current_mtime != last_mtime:
                    last_mtime = current_mtime
                    df = load_cards()
                    payload = {
                        'columns': df.columns.tolist(),
                        'records': df.to_dict(orient='records')
                    }
                    yield f"data: {json.dumps(payload)}\n\n"
            time.sleep(1)
    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/card/<path:key>')
def serve_card_page(key):
    """Serve the card page for a given key if it exists."""
    full_url = f'http://localhost:{PORT}/card/{key}'
    if full_url in KEY_TO_CARD_ID:
        card_id = KEY_TO_CARD_ID[full_url]
        image_url = None
        for ext in ['.png', '.jpg', '.jpeg']:
            image_filename = card_id + ext
            image_path = os.path.join(CARDS_FOLDER, image_filename)
            if os.path.exists(image_path):
                image_url = f'/card_image/{image_filename}'
                break
        return render_template('add_card_owner.html', image_url=image_url)
    else:
        abort(404)

@app.route('/card_image/<filename>')
def card_image(filename):
    """Serve image files from the cards folder."""
    return send_from_directory(CARDS_FOLDER, filename)

@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 error handler."""
    return render_template('404.html'), 404

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ─── ENTRY POINT ────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print(f"- - http://localhost:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)
