import os
import csv
import sys
from dotenv import load_dotenv

# Adjust path to import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from core.database import query_db, update_card, get_db

def main():
    load_dotenv()
    AUTH_CSV = os.getenv('AUTH_USERS_CSV') or os.getenv('AUTH_USERS')
    # fallback if env var name varies
    if not AUTH_CSV:
         # Try default path based on observed file context
         default_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'users_auth.csv')
         if os.path.exists(default_path):
             AUTH_CSV = default_path
         else:
             print("ERROR: AUTH_USERS_CSV not set and default not found.")
             return

    if not os.path.exists(AUTH_CSV):
        print("No auth users file found.")
        return

    # Read pending changes
    with open(AUTH_CSV, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        # Check if header exists? routes.py writes [username, ref_url]. 
        # If file started empty, it has no header.
        # If it has header, DictReader is better.
        # Let's peek.
        f.seek(0)
        first_line = f.readline()
        f.seek(0)
        
        has_header = "AUTH_MAILS" in first_line or "username" in first_line.lower()
        
        rows = []
        if has_header:
            dict_reader = csv.DictReader(f)
            # Map known headers to standard keys
            for r in dict_reader:
                # Support multiple possible header names
                u = r.get('AUTH_MAILS') or r.get('username') or r.get('USERNAME')
                l = r.get('AUTH_URLS') or r.get('ref_url') or r.get('REF_URL')
                if u and l:
                    rows.append({'username': u, 'url': l})
        else:
            # Assume no header: col 0 = username, col 1 = url
            csv_reader = csv.reader(f)
            for r in csv_reader:
                if len(r) >= 2:
                    rows.append({'username': r[0], 'url': r[1]})

    if not rows:
        return

    processed_indices = set()
    db = get_db()
    
    count = 0
    for i, row in enumerate(rows):
        username = row['username']
        ref_url = row['url']
        
        # We need to find the card. 
        # ref_url might be full url "http.../card/key" or just key?
        # In routes.py: `session.pop('ref_url', '')`
        # In `serve_card_page(key)` it seems `request.url` or similar is stored?
        # Let's assume ref_url MATCHES card_url in DB or suffix.
        # Try exact match first, then suffix match.
        
        sql = "SELECT card_id FROM cards WHERE card_url = ? OR card_url LIKE ?"
        # Try both exact and suffix (note: suffix needs %)
        # But SQLite LIKE is case insensitive usually.
        
        # If ref_url is just the key, we search for `.../card/<key>`
        # If ref_url is full url, we search exact.
        
        match = query_db(sql, (ref_url, f'%{ref_url}'), one=True)
        
        if match:
            cid = match['card_id']
            # Update Owner and Status
            # Use direct execute for atomicity if possible, or helper
            db.execute("UPDATE cards SET owner = ?, status = 'STATUS_2' WHERE card_id = ?", (username, cid))
            processed_indices.add(i)
            count += 1
        else:
            print(f"Card not found for URL: {ref_url}")

    db.commit()
    print(f"Updated {count} cards to STATUS_2 (Owned by {username}).")

    # Rewriting CSV (removing processed)
    # We should preserve header if it existed.
    if processed_indices:
        remaining_rows = [row for i, row in enumerate(rows) if i not in processed_indices]
        
        with open(AUTH_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # If we want to keep a header? logic becomes complex if we guessed.
            # Easiest: If we detected header, write it back? 
            # Or just write rows. `routes.py` appends without header checks.
            # If we switch to always no header (or consistent header), it's better.
            # For now, just write what remains.
            for r in remaining_rows:
                writer.writerow([r['username'], r['url']])

if __name__ == '__main__':
    main()
