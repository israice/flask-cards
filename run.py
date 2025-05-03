from flask import Flask, render_template, redirect, url_for, session, jsonify, Response
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv
import pandas as pd
import logging
import json
import time

# ─── CONFIGURATION ──────────────────────────────────────────────────────────────
load_dotenv()

APP_SECRET = os.getenv('SESSION_SECRET')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
CSV_PATH = os.getenv('CSV_PATH', 'users_mails.csv')
ADMIN_CSV_PATH = 'data/admin_mails.csv'
PORT = int(os.getenv('PORT', 5000))

if not APP_SECRET:
    raise ValueError("SESSION_SECRET must be set in .env")

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

# ─── LOGGING ────────────────────────────────────────────────────────────────────
logging.getLogger('waitress').setLevel(logging.ERROR)

# ─── HELPER FUNCTIONS ───────────────────────────────────────────────────────────
def load_users():
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    return pd.DataFrame(columns=['email', 'name'])

def save_user(email, name):
    users = load_users()
    if email not in users['email'].values:
        users = pd.concat([users, pd.DataFrame({'email': [email], 'name': [name]})], ignore_index=True)
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
            email, name = user_info.get('email'), user_info.get('name')
            print(f"User authenticated: {email}, {name}")
            save_user(email, name)
            session['user'] = {'email': email, 'name': name}
            return redirect(url_for('profile'))
        print("No user info received from Google")
    except Exception as e:
        print(f"Error in authorize: {str(e)}")
    return "Authorization failed. Please try again."

@app.route('/profile')
def profile():
    user = session.get('user')
    if not user:
        print("No user in session, redirecting to login")
        return redirect(url_for('login'))
    
    admin_emails = load_admin_emails()
    user_email = user['email'].strip().lower()
    is_admin = user_email in admin_emails
    
    return render_template('profile.html', user=user, is_admin=is_admin)

@app.route('/table')
def table():
    user = session.get('user')
    if not user:
        print("No user in session, redirecting to login")
        return redirect(url_for('login'))
    
    admin_emails = load_admin_emails()
    user_email = user['email'].strip().lower()
    if user_email not in admin_emails:
        print("User is not admin, redirecting to profile")
        return redirect(url_for('profile'))
    
    return render_template('table.html', user=user)

@app.route('/get_users')
def get_users():
    users = load_users()
    return jsonify({'users': users.to_dict(orient='records')})

@app.route('/stream')
def stream():
    def event_stream():
        last_mtime = 0
        while True:
            current_mtime = os.path.getmtime(CSV_PATH)
            if current_mtime != last_mtime:
                last_mtime = current_mtime
                users = load_users().to_dict(orient='records')
                yield f"data: {json.dumps(users)}\n\n"
            time.sleep(1)
    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ─── ENTRY POINT ────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print(f"- - http://localhost:{PORT}")
    from waitress import serve
    serve(app, host='0.0.0.0', port=PORT)
