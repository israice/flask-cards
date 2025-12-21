import sqlite3
import os
from flask import g, has_app_context

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'nakama.db')
_standalone_db = None

def get_db():
    global _standalone_db
    if has_app_context():
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(DB_PATH)
            db.row_factory = sqlite3.Row
        return db
    else:
        if _standalone_db is None:
            _standalone_db = sqlite3.connect(DB_PATH)
            _standalone_db.row_factory = sqlite3.Row
        return _standalone_db

def close_db(e=None):
    if has_app_context():
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()
    else:
        pass # Standalone db is kept open or closed manually if needed

def init_db():
    """Initialize the database with the schema."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'USER'
        )
    ''')
    
    # Cards table
    # Columns based on CSV: ID, PACK, DATE, TYPE, OWNER, DESC, COINS, USD, NAME, THEME, CHAIN, STATUS, MONSTER_POWER, POWER_COMBAT
    # Plus internal columns if needed.
    c.execute('''
        CREATE TABLE IF NOT EXISTS cards (
            card_id TEXT PRIMARY KEY,
            pack_id TEXT,
            card_date TEXT,
            user_type TEXT,
            owner TEXT,
            description TEXT,
            coins TEXT,
            usd_amount TEXT,
            name TEXT,
            chain TEXT,
            theme TEXT,
            card_type TEXT,
            card_url TEXT,
            card_keys TEXT,
            status TEXT,
            monster_power TEXT,
            power_combat TEXT,
            image_filename TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def update_card(card_id, field, value):
    """Update a specific field for a card."""
    db = get_db()
    # Check if column exists or ensure it's safe? 
    # For now, we assume field is a valid column name.
    # We cannot parametrize column names in sqlite3, so we must be careful.
    # However, these scripts are internal.
    query = f"UPDATE cards SET {field} = ? WHERE card_id = ?"
    db.execute(query, (value, card_id))
    db.commit()

def get_all_card_ids():
    """Return list of all card IDs."""
    rows = query_db("SELECT card_id FROM cards")
    return [r['card_id'] for r in rows]

