import os
import csv
import subprocess
from flask import (
    Blueprint, render_template, redirect, url_for, session,
    jsonify, abort, send_from_directory, request, current_app
)

bp = Blueprint('main', __name__)

# Helpers using current_app config

def load_records_from_csv():
    with open(current_app.config['SYSTEM_CSV'], newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def load_whitelist(path):
    if not os.path.exists(path):
        return set()
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        if len(rows) < 2:
            return set()
        return {r[0].strip().lower() for r in rows[1:]}

def determine_user_is_admin(email):
    email = email.strip().lower()
    admins = load_whitelist(current_app.config['ADMIN_DB'])
    users = load_whitelist(current_app.config['USER_DB'])
    if email in admins:
        return True
    if email in users:
        return False
    os.makedirs(os.path.dirname(current_app.config['USER_DB']), exist_ok=True)
    with open(current_app.config['USER_DB'], 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([email])
    return False

def get_user_cards(email):
    records = load_records_from_csv()
    cards = []
    for rec in records:
        if rec.get('CARD_OWNER', '').strip().lower() != email.lower():
            continue
        cid = rec.get('CARD_ID')
        if not cid:
            continue
        raw_status = rec.get('CARD_STATUS')
        status = raw_status.strip() if raw_status else ''

        for ext in ['.png', '.jpg', '.jpeg']:
            fname = cid + ext
            folder = current_app.config['CARDS_FOLDER']
            path = os.path.join(folder, fname)
            if os.path.exists(path):
                url = url_for('main.card_image', filename=fname)
                cards.append({
                    'url': url,
                    'CARD_ID': cid,
                    'status': status,
                    'CARD_CHAIN': rec.get('CARD_CHAIN'),
                    'CARD_NAME': rec.get('CARD_NAME'),
                    'CARD_THEME': rec.get('CARD_THEME'),
                    'CARD_TYPE': rec.get('CARD_TYPE'),
                    'CARD_COINS': rec.get('CARD_COINS'),
                    'USD_AMMOUNT': rec.get('USD_AMMOUNT'),
                    'PACK_ID': rec.get('PACK_ID'),
                    'CARD_DATE': rec.get('CARD_DATE'),
                })
                break
    return cards

# ROUTES

@bp.route('/')
def root():
    return redirect(url_for('main.login'))

@bp.route('/login')
def login():
    return render_template('login.html')

@bp.route('/google-login')
def google_login():
    next_page = request.args.get('next')
    if next_page:
        session['next_page'] = next_page
        if next_page == 'add_card_owner':
            session['ref_url'] = request.referrer
    return current_app.google.authorize_redirect(url_for('main.authorize', _external=True))

@bp.route('/auth/google/callback')
def authorize():
    try:
        token = current_app.google.authorize_access_token()
        user_info = token.get('userinfo', {})
        email = user_info.get('email', '').strip().lower()
        if not email:
            return redirect(url_for('main.login', _external=True))
        session['user'] = {'email': email}
        np = session.pop('next_page', None)
        if np == 'add_card_owner' and current_app.config.get('AUTH_USERS_CSV'):
            os.makedirs(os.path.dirname(current_app.config['AUTH_USERS_CSV']), exist_ok=True)
            with open(current_app.config['AUTH_USERS_CSV'], 'a', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow([email, session.pop('ref_url', '')])
            try:
                subprocess.run(
                    ['python', 'core/BACKEND/D_change_card_owner/D_run_change_card_owner.py'],
                    check=True
                )
            except subprocess.CalledProcessError:
                pass
            return redirect(url_for('main.profile', _external=True))
        if np and np in current_app.view_functions:
            return redirect(url_for(np, _external=True))
        return redirect(url_for('main.profile', _external=True))
    except:
        return redirect(url_for('main.login', _external=True))

@bp.route('/profile')
def profile():
    user = session.get('user')
    if not user:
        return redirect(url_for('main.login'))
    email = user['email']
    return render_template(
        'profile.html',
        user=user,
        is_admin=determine_user_is_admin(email),
        cards=get_user_cards(email)
    )

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))

@bp.route('/table')
def table():
    user = session.get('user')
    if not user or not determine_user_is_admin(user['email']):
        return redirect(url_for('main.profile'))
    return render_template('table.html', user=user)

@bp.route('/get_users')
def get_users():
    try:
        recs = load_records_from_csv()
        if not recs:
            return jsonify({'columns': [], 'records': []})
        return jsonify({'columns': list(recs[0].keys()), 'records': recs})
    except Exception as e:
        return jsonify({'columns': [], 'records': [], 'error': str(e)}), 500

@bp.route('/api/cards')
def api_cards():
    user = session.get('user')
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(get_user_cards(user['email']))

@bp.route('/card/<path:key>')
def serve_card_page(key):
    suffix = f'/card/{key}'
    match = next(
        (r for r in load_records_from_csv() if r.get('CARD_URL','').endswith(suffix)),
        None
    )
    if not match or match.get('CARD_OWNER') != 'SYSTEM':
        abort(404)
    cid = match.get('CARD_ID','')
    url = None
    for ext in ['.png','.jpg','.jpeg']:
        fname = f'{cid}{ext}'
        p = os.path.join(current_app.config['CARDS_FOLDER'], fname)
        if os.path.exists(p):
            url = url_for('main.card_image', filename=fname)
            break
    return render_template('add_card_owner.html', image_url=url)

@bp.route('/card_image/<filename>')
def card_image(filename):
    return send_from_directory(current_app.config['CARDS_FOLDER'], filename)

@bp.route('/run_create_cards', methods=['POST'])
def run_create_cards():
    user = session.get('user')
    if not user or not determine_user_is_admin(user['email']):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    try:
        subprocess.run(
            ['python', os.path.join('core','BACKEND','A_create_cards','A_run_create_cards.py')],
            check=True
        )
        return jsonify({'status': 'success'})
    except subprocess.CalledProcessError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.errorhandler(404)
def handle_404(e):
    return render_template('404.html'), 404

# Serve the client-side fragments

@bp.route('/card_1.html')
def card_fragment():
    fragment_dir = os.path.join(current_app.root_path, 'core', 'FRONTEND')
    return send_from_directory(fragment_dir, 'card_1.html')

@bp.route('/card_2.html')
def card2_fragment():
    fragment_dir = os.path.join(current_app.root_path, 'core', 'FRONTEND')
    return send_from_directory(fragment_dir, 'card_2.html')

@bp.route('/card_3.html')
def card3_fragment():
    fragment_dir = os.path.join(current_app.root_path, 'core', 'FRONTEND')
    return send_from_directory(fragment_dir, 'card_3.html')
