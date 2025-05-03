# run.py
import sys
sys.dont_write_bytecode = True  # disable writing .pyc files into __pycache__

from flask import Flask, render_template, redirect, url_for, session, jsonify, Response
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv
import pandas as pd
import json
import time
import logging

# ─── CONFIGURATION ──────────────────────────────────────────────────────────────
load_dotenv()

APP_SECRET = os.getenv('SESSION_SECRET')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
CSV_PATH = 'data/system_cards.csv'
ADMIN_CSV_PATH = 'data/system_admin.csv'
PORT = int(os.getenv('PORT', 5000))

if not APP_SECRET:
    raise SystemExit("SESSION_SECRET must be set in .env")

# ─── SUPPRESS FLASK AND WERKZEUG LOGS ───────────────────────────────────────────
log = logging.getLogger('werkzeug')
log.setLevel(logging.CRITICAL)

# ─── FLASK & OAUTH SETUP ────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = APP_SECRET

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# ─── HELPER FUNCTIONS ───────────────────────────────────────────────────────────
def load_users():
    """Load CSV into DataFrame, return empty if missing."""
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    return pd.DataFrame()

def save_user(email):
    users = load_users()
    if 'email' in users.columns and email not in users['email'].values:
        users = pd.concat([users, pd.DataFrame({'email': [email]})], ignore_index=True)
        users.to_csv(CSV_PATH, index=False)

def load_admin_emails():
    if os.path.exists(ADMIN_CSV_PATH):
        admins = pd.read_csv(ADMIN_CSV_PATH)
        return set(admins['admin_email'].str.strip().str.lower().values)
    return set()

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
    except Exception:
        pass
    return '', 204

@app.route('/profile')
def profile():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    
    admin_emails = load_admin_emails()
    user_email = user['email'].strip().lower()
    is_admin = user_email in admin_emails
    
    return render_template('profile.html', user=user, is_admin=is_admin)

@app.route('/table')
def table():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    
    admin_emails = load_admin_emails()
    user_email = user['email'].strip().lower()
    if user_email not in admin_emails:
        return redirect(url_for('profile'))
    
    return render_template('table.html', user=user)

# ─── UPDATED: return both columns order and records ────────────────────────────
@app.route('/get_users')
def get_users():
    df = load_users()
    cols = df.columns.tolist()
    records = df.to_dict(orient='records')
    return jsonify({'columns': cols, 'records': records})

@app.route('/stream')
def stream():
    def event_stream():
        last_mtime = 0
        while True:
            if os.path.exists(CSV_PATH):
                current_mtime = os.path.getmtime(CSV_PATH)
                if current_mtime != last_mtime:
                    last_mtime = current_mtime
                    df = load_users()
                    payload = {
                        'columns': df.columns.tolist(),
                        'records': df.to_dict(orient='records')
                    }
                    yield f"data: {json.dumps(payload)}\n\n"
            time.sleep(1)
    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ─── ENTRY POINT ────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print(f"- - http://localhost:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)
