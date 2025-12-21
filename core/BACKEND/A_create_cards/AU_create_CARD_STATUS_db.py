import os
import sys
# Adjust path to import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from core.database import query_db, update_card

def update_status():
    """
    Set default status 'STATUS_1' (Created) for cards with empty status.
    """
    rows = query_db("SELECT card_id FROM cards WHERE status IS NULL OR status = ''")
    
    count = 0
    for row in rows:
        cid = row['card_id']
        update_card(cid, 'status', 'STATUS_1')
        count += 1
            
    print(f"Updated {count} cards with status 'STATUS_1'.")

def main():
    update_status()

if __name__ == "__main__":
    main()
