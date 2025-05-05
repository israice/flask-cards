import sys
sys.dont_write_bytecode = True  # disable writing .pyc files into __pycache__

from flask import Flask, render_template, redirect, url_for, session, jsonify, Response, abort, send_from_directory, request
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv
import json
import time
import logging
import csv
import subprocess

# ─── CONFIGURATION ──────────────────────────────────────────────────────────────
load_dotenv()

APP_SECRET = os.getenv('SESSION_SECRET')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

AUTH_USERS = os.getenv('AUTH_USERS')
SYSTEM_ADMIN_CSV = os.getenv('SYSTEM_ADMIN_CSV')
SYSTEM_CARDS_CSV = os.getenv('SYSTEM_CARDS_CSV')
TEMPLATE_FOLDER = os.getenv('TEMPLATE_FOLDER')
SYSTEM_CARD_AUTH_CSV = os.getenv('SYSTEM_CARD_AUTH_SCV')
CARDS_FOLDER = os.getenv('CARDS_BANK_FOLDER')

PORT = int(os.getenv('PORT', 5000))

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
        raise SystemExit(f"{name} must be set in .env")

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

KEY_TO_CARD_ID = {}
try:
    with open(SYSTEM_CARD_AUTH_CSV, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            KEY_TO_CARD_ID[row['KEY_IN']] = row['CARD_ID']
except Exception:
    pass

def get_user_cards(email):
    records, columns = load_cards()
    user_cards = []
    for record in records:
        if len(columns) >= 3 and record[columns[2]].strip().lower() == email.strip().lower():
            card_id = record[columns[0]]
            for ext in ['.png', '.jpg', '.jpeg']:
                fname = card_id + ext
                if os.path.exists(os.path.join(CARDS_FOLDER, fname)):
                    url = url_for('card_image', filename=fname)
                    user_cards.append({'card_id': card_id, 'url': url})
                    break
    return user_cards

def load_cards():
    rows = []
    max_columns = 0
    if not os.path.exists(SYSTEM_CARDS_CSV):
        return [], []
    try:
        with open(SYSTEM_CARDS_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                rows.append(row)
                if len(row) > max_columns:
                    max_columns = len(row)
        columns = [f'col_{i + 1}' for i in range(max_columns)]
        records = []
        for row in rows:
            record = {}
            for i in range(max_columns):
                record[columns[i]] = row[i] if i < len(row) else ''
            records.append(record)
        return records, columns
    except Exception:
        return [], []

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
        if user_info:
            email = user_info.get('email')
            session['user'] = {'email': email}
            next_page = session.pop('next_page', None)
            if next_page == 'add_card_owner':
                try:
                    subprocess.run(['python', 'core/BACKEND/C_change_card_owner/C_run_change_card_owner.py'], check=True)
                except subprocess.CalledProcessError:
                    pass
            return redirect(url_for('profile'))
    except Exception:
        pass
    return '', 204

@app.route('/profile')
def profile():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    admin_emails = set()
    if os.path.exists(SYSTEM_ADMIN_CSV):
        try:
            with open(SYSTEM_ADMIN_CSV, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    admin_emails.add(row['admin_email'].strip().lower())
        except Exception:
            pass
    user_email = user['email'].strip().lower()
    is_admin = user_email in admin_emails
    user_cards = get_user_cards(user_email)
    return render_template('profile.html', user=user, is_admin=is_admin, cards=user_cards)

@app.route('/table')
def table():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    admin_emails = set()
    if os.path.exists(SYSTEM_ADMIN_CSV):
        try:
            with open(SYSTEM_ADMIN_CSV, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    admin_emails.add(row['admin_email'].strip().lower())
        except Exception:
            pass
    user_email = user['email'].strip().lower()
    if user_email not in admin_emails:
        return redirect(url_for('profile'))
    return render_template('table.html', user=user)

@app.route('/get_users')
def get_users():
    records, columns = load_cards()
    return jsonify({'columns': columns, 'records': records})

@app.route('/stream')
def stream():
    def event_stream():
        last_mtime = 0
        while True:
            if os.path.exists(SYSTEM_CARDS_CSV):
                current_mtime = os.path.getmtime(SYSTEM_CARDS_CSV)
                if current_mtime != last_mtime:
                    last_mtime = current_mtime
                    records, columns = load_cards()
                    payload = {'columns': columns, 'records': records}
                    yield f"data: {json.dumps(payload)}\n\n"
            time.sleep(1)
    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/card/<path:key>')
def serve_card_page(key):
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
    return send_from_directory(CARDS_FOLDER, filename)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    print(f"- - http://localhost:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)