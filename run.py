import sys
sys.dont_write_bytecode = True  # disable writing .pyc files into **pycache**

import os
import csv
from flask import (
    Flask, render_template, redirect, url_for, session,
    jsonify, abort, send_from_directory, request
)
from werkzeug.middleware.proxy_fix import ProxyFix
from authlib.integrations.flask_client import OAuth
import logging
import subprocess
from dotenv import load_dotenv

# CONFIGURATION
load_dotenv()
APP_SECRET = os.getenv('SESSION_SECRET')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
AUTH_USERS_CSV = os.getenv('AUTH_USERS')  # path to file for authenticated users logging
TEMPLATE_FOLDER = os.getenv('TEMPLATE_FOLDER')
CARDS_FOLDER = os.getenv('CARDS_BANK_FOLDER')
SYSTEM_CSV = os.getenv('SYSTEM_FULL_DB_CSV')  # path to full DB CSV
# Paths to whitelist CSVs
ADMIN_DB = os.path.join('core', 'data', 'admin_db.csv')
USER_DB = os.path.join('core', 'data', 'user_db.csv')

if os.getenv('PORT') is None:
    raise SystemExit("PORT must be set in .env")
PORT = int(os.getenv('PORT'))

# Ensure required envs are set
required_envs = {
    'SESSION_SECRET': APP_SECRET,
    'TEMPLATE_FOLDER': TEMPLATE_FOLDER,
    'CARDS_BANK_FOLDER': CARDS_FOLDER,
    'AUTH_USERS': AUTH_USERS_CSV,
    'SYSTEM_FULL_DB_CSV': SYSTEM_CSV,
}
for name, val in required_envs.items():
    if not val:
        raise SystemExit(f"{name} must be set in .env")

# Silence werkzeug logs
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.CRITICAL)

# Initialize Flask
app = Flask(__name__, template_folder=TEMPLATE_FOLDER)
app.secret_key = APP_SECRET

# Trust proxy headers for correct scheme and host
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config['PREFERRED_URL_SCHEME'] = 'https'

# Initialize OAuth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    access_token_url='https://oauth2.googleapis.com/token',
    api_base_url='https://openidconnect.googleapis.com/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs',
    client_kwargs={'scope': 'openid email profile'}
)

def load_records_from_csv():
    """Load all records from the CSV source into a list of dicts."""
    with open(SYSTEM_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

# Whitelist management

def load_whitelist(path):
    """Load a single-column whitelist CSV (with header) into a set of lowercase emails."""
    if not os.path.exists(path):
        return set()
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        if len(rows) < 2:
            return set()
        # skip header, collect emails
        return {r[0].strip().lower() for r in rows[1:] if r and r[0].strip()}


def determine_user_is_admin(email):
    """Decide if email is in admin list; if not seen anywhere, add to user whitelist."""
    email = email.strip().lower()
    admins = load_whitelist(ADMIN_DB)
    users = load_whitelist(USER_DB)
    if email in admins:
        return True
    if email in users:
        return False
    # If new user, append to user whitelist
    os.makedirs(os.path.dirname(USER_DB), exist_ok=True)
    with open(USER_DB, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([email])  # add new user
    return False


def get_user_cards(email):
    """Fetch and build card list only for the specified user."""
    records = load_records_from_csv()
    user_cards = []
    for rec in records:
        if rec.get('CARD_OWNER', '').strip().lower() != email.lower():
            continue
        card_id = rec.get('CARD_ID')
        if not card_id:
            continue
        # find existing image file
        for ext in ['.png', '.jpg', '.jpeg']:
            fname = card_id + ext
            path = os.path.join(CARDS_FOLDER, fname)
            if os.path.exists(path):
                url = url_for('card_image', filename=fname)
                user_cards.append({
                    'CARD_ID': card_id,
                    'url': url,
                    'transactions': rec.get('CARD_COINS', ''),
                    'balance': rec.get('USD_AMMOUNT', ''),
                    'status': rec.get('CARD_TYPE', '')
                })
                break
    return user_cards

# ROUTES
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
        if next_page == 'add_card_owner':
            session['ref_url'] = request.referrer
    return google.authorize_redirect(url_for('authorize', _external=True))

@app.route('/auth/google/callback')
def authorize():
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo', {})
        email = user_info.get('email', '').strip().lower()
        if not email:
            return redirect(url_for('login', _external=True))
        session['user'] = {'email': email}
        next_page = session.pop('next_page', None)
        if next_page == 'add_card_owner' and AUTH_USERS_CSV:
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
            return redirect(url_for('profile', _external=True))
        if next_page and next_page in app.view_functions:
            return redirect(url_for(next_page, _external=True))
        return redirect(url_for('profile', _external=True))
    except Exception:
        return redirect(url_for('login', _external=True))

@app.route('/profile')
def profile():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    email = user['email']
    # determine admin status via whitelist files
    is_admin = determine_user_is_admin(email)
    cards = get_user_cards(email)
    return render_template('profile.html', user=user, is_admin=is_admin, cards=cards)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/table')
def table():
    user = session.get('user')
    if not user or not determine_user_is_admin(user['email']):
        return redirect(url_for('profile'))
    return render_template('table.html', user=user)

@app.route('/get_users')
def get_users():
    try:
        records = load_records_from_csv()
        if not records:
            return jsonify({'columns': [], 'records': []})
        columns = list(records[0].keys())
        return jsonify({'columns': columns, 'records': records})
    except Exception as e:
        return jsonify({'columns': [], 'records': [], 'error': str(e)}), 500

@app.route('/api/cards')
def api_cards():
    user = session.get('user')
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    cards = get_user_cards(user['email'])
    return jsonify(cards)

@app.route('/card/<path:key>')
def serve_card_page(key):
    path_suffix = f'/card/{key}'
    records = load_records_from_csv()
    match = next(
        (rec for rec in records if rec.get('CARD_URL', '').endswith(path_suffix)),
        None
    )
    if not match or match.get('CARD_OWNER') != 'SYSTEM':
        abort(404)
    card_id = match.get('CARD_ID', '')
    image_url = None
    for ext in ['.png', '.jpg', '.jpeg']:
        fname = card_id + ext
        if os.path.exists(os.path.join(CARDS_FOLDER, fname)):
            image_url = url_for('card_image', filename=fname)
            break
    return render_template('add_card_owner.html', image_url=image_url)

@app.route('/card_image/<filename>')
def card_image(filename):
    return send_from_directory(CARDS_FOLDER, filename)

@app.route('/run_create_cards', methods=['POST'])
def run_create_cards():
    user = session.get('user')
    if not user:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    if not determine_user_is_admin(user['email']):
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
    return render_template('404.html'), 404

if __name__ == '__main__':
    print(f"- - https://nakama.wfork.org/")
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)
