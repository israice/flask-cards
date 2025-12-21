import csv
import os
import sqlite3
import sys

# Adjust path to import core.database if needed, or just connect directly
# Since this script is in core/data/, we can go up two levels.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.database import DB_PATH, init_db

SYSTEM_CSV = os.path.join(os.path.dirname(__file__), "system_full_db.csv")
USER_DB_CSV = os.path.join(os.path.dirname(__file__), "user_db.csv")
ADMIN_DB_CSV = os.path.join(os.path.dirname(__file__), "admin_db.csv")

def load_whitelist(path):
    if not os.path.exists(path):
        return set()
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        if len(rows) < 2:
            return set()
        return {r[0].strip().lower() for r in rows[1:]}

def migrate_users(conn):
    print("Migrating users...")
    c = conn.cursor()
    
    if not os.path.exists(USER_DB_CSV):
        print("No user_db.csv found.")
        return

    admin_set = load_whitelist(ADMIN_DB_CSV)
    
    with open(USER_DB_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Expected header: USER_WHITELIST, PASSWORD
        count = 0
        for row in reader:
            username = (row.get('USER_WHITELIST') or '').strip()
            password = (row.get('PASSWORD') or '').strip()
            
            if username:
                is_admin = (username.lower() in admin_set) or (username.lower() == 'admin')
                role = 'ADMIN' if is_admin else 'USER'
                
                try:
                    c.execute('''
                        INSERT OR REPLACE INTO users (username, password, role)
                        VALUES (?, ?, ?)
                    ''', (username, password, role))
                    count += 1
                except sqlite3.Error as e:
                    print(f"Error inserting user {username}: {e}")
    conn.commit()
    print(f"Migrated {count} users.")

def migrate_cards(conn):
    print("Migrating cards...")
    c = conn.cursor()
    
    if not os.path.exists(SYSTEM_CSV):
        print("No system_full_db.csv found.")
        return

    # Header map based on user feedback:
    # CARD_ID, PACK_ID, CARD_DATE, USER_TYPE, CARD_OWNER, CARD_DESCRIPTION, CARD_COINS, 
    # USD_AMMOUNT, CARD_NAME, CARD_CHAIN, CARD_THEME, CARD_TYPE, CARD_URL, CARD_KEYS, 
    # CARD_STATUS, MONSTER_POWER, POWER_COMBAT
    
    with open(SYSTEM_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            # Map CSV columns to DB columns
            # DB: card_id, pack_id, card_date, user_type, owner, description, coins, usd_amount, 
            # name, chain, theme, card_type, card_url, card_keys, status, monster_power, power_combat, image_filename
            
            card_id = row.get('CARD_ID', '').strip()
            if not card_id:
                continue
            
            # Derived image filename logic from routes.py (simplified)
            # routes.py checks .png, .jpg, .jpeg. We will store just the ID or null for now, 
            # or we can check file existence. For now let's leave image_filename NULL 
            # and rely on ID-based lookup or update logic later.
            
            try:
                c.execute('''
                    INSERT OR REPLACE INTO cards (
                        card_id, pack_id, card_date, user_type, owner, description, 
                        coins, usd_amount, name, chain, theme, card_type, 
                        card_url, card_keys, status, monster_power, power_combat
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    card_id,
                    row.get('PACK_ID', ''),
                    row.get('CARD_DATE', ''),
                    row.get('USER_TYPE', ''),
                    row.get('CARD_OWNER', ''),
                    row.get('CARD_DESCRIPTION', ''),
                    row.get('CARD_COINS', ''),
                    row.get('USD_AMMOUNT', ''),
                    row.get('CARD_NAME', ''),
                    row.get('CARD_CHAIN', ''),
                    row.get('CARD_THEME', ''),
                    row.get('CARD_TYPE', ''),
                    row.get('CARD_URL', ''),
                    row.get('CARD_KEYS', ''),
                    row.get('CARD_STATUS', ''),
                    row.get('MONSTER_POWER', ''),
                    row.get('POWER_COMBAT', '')
                ))
                count += 1
            except sqlite3.Error as e:
                print(f"Error inserting card {card_id}: {e}")
                
    conn.commit()
    print(f"Migrated {count} cards.")

def main():
    # Initialize DB (create tables)
    init_db()
    
    # Connect
    conn = sqlite3.connect(DB_PATH)
    
    migrate_users(conn)
    migrate_cards(conn)
    
    conn.close()
    print("Migration finished.")

if __name__ == "__main__":
    main()
