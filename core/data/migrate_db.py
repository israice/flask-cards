import csv
import os

DB_PATH = os.path.join("core", "data", "system_full_db.csv")

def migrate():
    if not os.path.exists(DB_PATH):
        print("DB not found")
        return

    with open(DB_PATH, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        return

    header = rows[0]
    
    # Check if already migrated
    if "CARD_DESCRIPTION" in header:
        print("Already migrated")
        return

    # New Header
    # Current: ID, PACK, DATE, TYPE, OWNER, COINS, USD, NAME...
    # New: ID, PACK, DATE, TYPE, OWNER, DESC, COINS, USD, NAME...
    
    # Insert DESC at 5
    header.insert(5, "CARD_DESCRIPTION")
    # Append Stats
    header.extend(["MONSTER_POWER", "POWER_COMBAT"])
    
    new_rows = [header]
    
    for row in rows[1:]:
        # Insert empty at 5
        if len(row) >= 5:
            row.insert(5, "")
        else:
            # Handle short rows?
            while len(row) < 5:
                row.append("")
            row.append("") # Insert at 5 implies it becomes 5? No if len < 5, insert at 5 is append.
            
        # Append empty stats
        row.extend(["", ""])
        new_rows.append(row)

    with open(DB_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(new_rows)
    
    print("Migration complete")

if __name__ == "__main__":
    migrate()
