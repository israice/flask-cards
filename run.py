import sys
sys.dont_write_bytecode = True  # disable writing .pyc files into **pycache**

import os
from flask import (
    Flask, render_template, redirect, url_for, session,
    jsonify, abort, send_from_directory, request
)
from werkzeug.middleware.proxy_fix import ProxyFix
from authlib.integrations.flask_client import OAuth
import logging
import csv  # for authenticated users logging
import subprocess
import requests  # for Airtable API requests
from dotenv import load_dotenv

# CONFIGURATION
load_dotenv()
APP_SECRET = os.getenv('SESSION_SECRET')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_ID = os.getenv('AIRTABLE_TABLE_ID')
AIRTABLE_VIEW_NAME = os.getenv('AIRTABLE_VIEW_NAME')
AUTH_USERS_CSV = os.getenv('AUTH_USERS')  # path to file for authenticated users logging
TEMPLATE_FOLDER = os.getenv('TEMPLATE_FOLDER')
CARDS_FOLDER = os.getenv('CARDS_BANK_FOLDER')
if os.getenv('PORT') is None:
    raise SystemExit("PORT must be set in .env")
PORT = int(os.getenv('PORT'))

# Ensure required envs are set
required_envs = {
    'SESSION_SECRET': APP_SECRET,
    'TEMPLATE_FOLDER': TEMPLATE_FOLDER,
    'CARDS_BANK_FOLDER': CARDS_FOLDER,
    'AUTH_USERS': AUTH_USERS_CSV,
    'AIRTABLE_API_KEY': AIRTABLE_API_KEY,
    'AIRTABLE_BASE_ID': AIRTABLE_BASE_ID,
    'AIRTABLE_TABLE_ID': AIRTABLE_TABLE_ID,
    'AIRTABLE_VIEW_NAME': AIRTABLE_VIEW_NAME,
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
# This ensures url_for(..., _external=True) generates HTTPS URLs behind a proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
# Force external URL generation to use HTTPS
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

# Airtable helper: persistent HTTP session
airtable_session = requests.Session()
airtable_session.headers.update({'Authorization': f'Bearer {AIRTABLE_API_KEY}'})
API_URL = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}'

def fetch_airtable_records(filter_formula=None):
    """Fetch records from Airtable with optional filter, using pagination."""
    params = {'view': AIRTABLE_VIEW_NAME, 'pageSize': 100}
    if filter_formula:
        params['filterByFormula'] = filter_formula
    records = []
    offset = None
    while True:
        if offset:
            params['offset'] = offset
        resp = airtable_session.get(API_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
        records.extend(data.get('records', []))
        offset = data.get('offset')
        if not offset:
            break
    return records

def get_admin_emails():
    """Extract set of admin emails by filtering only ADMIN rows in Airtable."""
    records = fetch_airtable_records("AND({USER_TYPE}='ADMIN',{CARD_OWNER}!='')")
    admin_emails = set()
    for rec in records:
        owner = rec.get('fields', {}).get('CARD_OWNER', '').strip().lower()
        if owner:
            admin_emails.add(owner)
    return admin_emails

def get_user_cards(email):
    """Fetch and build card list only for the specified user."""
    records = fetch_airtable_records(f"{{CARD_OWNER}}='{email}'")
    user_cards = []
    for rec in records:
        fields = rec.get('fields', {})
        card_id = fields.get('CARD_ID')
        if not card_id:
            continue
        for ext in ['.png', '.jpg', '.jpeg']:
            fname = card_id + ext
            path = os.path.join(CARDS_FOLDER, fname)
            if os.path.exists(path):
                url = url_for('card_image', filename=fname)
                user_cards.append({
                    'CARD_ID': card_id,
                    'url': url,
                    'transactions': fields.get('TRANSACTIONS', ''),
                    'balance': fields.get('BALANCE', ''),
                    'status': fields.get('STATUS', '')
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
    # Redirect to Google OAuth, preserving next-page information
    next_page = request.args.get('next')
    if next_page:
        session['next_page'] = next_page
        if next_page == 'add_card_owner':
            session['ref_url'] = request.referrer
    return google.authorize_redirect(url_for('authorize', _external=True))

@app.route('/auth/google/callback')
def authorize():
    try:
        token = google.authorize_access_token()  # fetch token and userinfo
        user_info = token.get('userinfo', {})
        email = user_info.get('email', '').strip().lower()
        if not email:
            return redirect(url_for('login', _external=True))
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
            return redirect(url_for('profile', _external=True))
        if next_page and next_page in app.view_functions:
            return redirect(url_for(next_page, _external=True))
        return redirect(url_for('profile', _external=True))
    except Exception as e:
        print(f"Error in authorize: {e}")
        return redirect(url_for('login', _external=True))

@app.route('/profile')
def profile():
    user = session.get('user')
    if not user:
        return redirect(url_for('login', _external=True))
    email = user['email']
    admin_emails = get_admin_emails()
    is_admin = email in admin_emails
    cards = get_user_cards(email)
    return render_template('profile.html', user=user, is_admin=is_admin, cards=cards)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login', _external=True))

@app.route('/table')
def table():
    user = session.get('user')
    if not user:
        return redirect(url_for('profile', _external=True))
    admin_emails = get_admin_emails()
    if user['email'] not in admin_emails:
        return redirect(url_for('profile', _external=True))
    return render_template('table.html', user=user)

@app.route('/get_users')
def get_users():
    try:
        records = fetch_airtable_records()
        if not records:
            return jsonify({'columns': [], 'records': []})
        first_fields = records[0].get('fields', {})
        columns = list(first_fields.keys())
        plain_records = [r.get('fields', {}) for r in records]
        return jsonify({'columns': columns, 'records': plain_records})
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
    path = f'/card/{key}'  # match only path part
    filter_formula = f"REGEX_MATCH({{CARD_URL}}, '.*{path}$')"
    records = fetch_airtable_records(filter_formula)
    if not records:
        abort(404)
    record = records[0]
    fields = record.get('fields', {})
    owner = fields.get('CARD_OWNER', '').strip()
    if owner != 'SYSTEM':
        abort(404)
    card_id = fields.get('CARD_ID', '')
    image_url = next(
        (f'/card_image/{card_id + ext}' for ext in ['.png', '.jpg', '.jpeg']
         if os.path.exists(os.path.join(CARDS_FOLDER, card_id + ext))),
        None
    )
    return render_template('add_card_owner.html', image_url=image_url)

@app.route('/card_image/<filename>')
def card_image(filename):
    return send_from_directory(CARDS_FOLDER, filename)

@app.route('/run_create_cards', methods=['POST'])
def run_create_cards():
    user = session.get('user')
    if not user:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    admin_emails = get_admin_emails()
    if user['email'] not in admin_emails:
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
    # print(f"- - http://localhost:5001/")
    print(f"- - https://nakama.wfork.org/")
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)
