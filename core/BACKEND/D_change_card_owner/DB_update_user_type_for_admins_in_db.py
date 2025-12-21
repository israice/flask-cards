import os
import sys

# Adjust path to import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from core.database import get_db

def main():
    db = get_db()
    
    # 1. Default all to SYSTEM if owner is missing
    db.execute("UPDATE cards SET user_type = 'SYSTEM' WHERE owner IS NULL OR owner = ''")
    
    # 2. Update based on known users (ADMIN or USER)
    # SQLite supports correlated subquery updates
    db.execute("""
        UPDATE cards 
        SET user_type = (SELECT role FROM users WHERE users.username = cards.owner)
        WHERE owner IN (SELECT username FROM users)
    """)
    
    # 3. Any remaining non-system that didn't match a user?
    # Original logic: "All other cases default to SYSTEM".
    # So if owner is set but NOT in users table, it becomes SYSTEM.
    db.execute("""
        UPDATE cards 
        SET user_type = 'SYSTEM'
        WHERE owner IS NOT NULL AND owner != '' AND owner NOT IN (SELECT username FROM users)
    """)
    
    db.commit()
    print("Updated user_type for all cards.")

if __name__ == '__main__':
    main()
