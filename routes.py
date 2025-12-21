import os
import csv
import subprocess
from flask import (
    Blueprint, render_template, redirect, url_for, session,
    jsonify, abort, send_from_directory, request, current_app
)
from werkzeug.security import check_password_hash

bp = Blueprint('main', __name__)

from core.database import get_db, query_db

def load_records_from_db():
    return query_db('SELECT * FROM cards')

def authenticate_user(username, password):
    """Authenticate user with username and password"""
    user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
    if user and user['password'] == password:
        return {
            'username': user['username'],
            'user_type': user['role']
        }
    return None

def determine_user_is_admin(username):
    """Check if user is admin based on username"""
    user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
    if user:
        return user['role'] == 'ADMIN'
    # Fallback/Bootstrapping: if 'admin' user doesn't exist in DB yet but tries to login, handle it? 
    # For now, rely on DB.
    return False

def get_user_cards(username):
    # Depending on how exact the match needs to be. CSV was case-insensitive often.
    # Let's try exact match first, or use LIKE.
    records = query_db('SELECT * FROM cards WHERE owner = ? COLLATE NOCASE', [username])
    cards = []
    for rec in records:
        cid = rec['card_id']
        if not cid:
            continue
            
        # Image logic
        url = None
        for ext in ['.png', '.jpg', '.jpeg']:
            fname = f"{cid}{ext}"
            path = os.path.join(current_app.config['CARDS_FOLDER'], fname)
            if os.path.exists(path):
                url = url_for('main.card_image', filename=fname)
                break
        
        # If no image found, url is None. The template might handle it or we skip?
        # The original code only appended if image exists:
        if url:
            cards.append({
                'url': url,
                'CARD_ID': cid,
                'status': rec['status'] or '',
                'CARD_CHAIN': rec['chain'],
                'CARD_NAME': rec['name'],
                'CARD_THEME': rec['theme'],
                'CARD_TYPE': rec['card_type'],
                'CARD_COINS': rec['coins'],
                'USD_AMMOUNT': rec['usd_amount'],
                'PACK_ID': rec['pack_id'],
                'CARD_DATE': rec['card_date'],
            })
    return cards

# ROUTES

@bp.route('/')
def root():
    return redirect(url_for('main.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = authenticate_user(username, password)
        if user:
            session['user'] = {'username': username}
            next_page = session.pop('next_page', None)

            if next_page == 'add_card_owner' and current_app.config.get('AUTH_USERS_CSV'):
                os.makedirs(os.path.dirname(current_app.config['AUTH_USERS_CSV']), exist_ok=True)
                with open(current_app.config['AUTH_USERS_CSV'], 'a', newline='', encoding='utf-8') as f:
                    csv.writer(f).writerow([username, session.pop('ref_url', '')])
                try:
                    subprocess.run(
                        ['python', 'core/BACKEND/D_change_card_owner/D_run_change_card_owner.py'],
                        check=True
                    )
                except subprocess.CalledProcessError:
                    pass
                return redirect(url_for('main.profile'))

            if next_page and next_page in current_app.view_functions:
                return redirect(url_for(next_page))
            return redirect(url_for('main.profile'))
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@bp.route('/profile')
def profile():
    user = session.get('user')
    if not user:
        return redirect(url_for('main.login'))
    username = user['username']
    return render_template(
        'profile.html',
        user=user,
        is_admin=determine_user_is_admin(username),
        cards=get_user_cards(username)
    )

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))

@bp.route('/table')
def table():
    user = session.get('user')
    if not user or not determine_user_is_admin(user['username']):
        return redirect(url_for('main.profile'))
    return render_template('table.html', user=user)

@bp.route('/get_users')
def get_users():
    try:
        recs = load_records_from_db()
        if not recs:
            return jsonify({'columns': [], 'records': []})
        # recs is list of sqlite3.Row
        return jsonify({'columns': list(recs[0].keys()), 'records': [dict(r) for r in recs]})
    except Exception as e:
        return jsonify({'columns': [], 'records': [], 'error': str(e)}), 500

@bp.route('/api/cards')
def api_cards():
    user = session.get('user')
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(get_user_cards(user['username']))

@bp.route('/card/<path:key>')
def serve_card_page(key):
    suffix = f'/card/{key}'
    # We don't store CARD_URL in the same way potentially, or we do.
    # The CSV had CARD_URL. The DB has card_url.
    # The logic in migration was: row.get('CARD_URL', '') -> card_url
    
    # We need to find a card where card_url ends with suffix
    # SQLite LIKE can do this: '%/card/{key}'
    
    match = query_db("SELECT * FROM cards WHERE card_url LIKE ?", [f'%{suffix}'], one=True)

    if not match or match['owner'] != 'SYSTEM':
        abort(404)
    cid = match['card_id']
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
    if not user or not determine_user_is_admin(user['username']):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    try:
        subprocess.run(
            ['python', os.path.join('core','BACKEND','A_create_cards','A_run_create_cards.py')],
            check=True
        )
        return jsonify({'status': 'success'})
    except subprocess.CalledProcessError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/activate_card', methods=['POST'])
def activate_card():
    user = session.get('user')
    if not user:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    data = request.get_json()
    card_id = data.get('card_id')
    
    if not card_id:
        return jsonify({'status': 'error', 'message': 'Missing card_id'}), 400

    # Verify ownership and current status
    # We only activate if it's currently in STATUS_2 (Owned but not active)
    # Or maybe we allow it from STATUS_1 if they own it? Usually STATUS_2 implies ownership.
    # Let's check DB.
    
    row = query_db('SELECT * FROM cards WHERE card_id = ?', [card_id], one=True)
    if not row:
        return jsonify({'status': 'error', 'message': 'Card not found'}), 404
        
    if row['owner'] != user['username']:
        return jsonify({'status': 'error', 'message': 'Not your card'}), 403
        
    # Check if already active
    if row['status'] == 'STATUS_3':
        return jsonify({'status': 'success', 'message': 'Already active', 'new_status': 'STATUS_3'})
        
    # Update to STATUS_3
    # Use direct DB execution
    try:
        db = get_db()
        db.execute("UPDATE cards SET status = 'STATUS_3' WHERE card_id = ?", (card_id,))
        db.commit()
        return jsonify({'status': 'success', 'new_status': 'STATUS_3'})
    except Exception as e:
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
