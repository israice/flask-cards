import os
import csv
from dotenv import load_dotenv

load_dotenv()

SOURCE_FILE = os.path.join("core", "data", "not_used", "GAME_STATS.csv")
import sys
# Adjust path to import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from core.database import query_db, update_card

SOURCE_FILE = os.path.join("core", "data", "not_used", "GAME_STATS.csv")

def read_source_data(file_path):
    if not os.path.exists(file_path):
        print(f"Source file {file_path} not found.")
        return []
    
    data = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if 'POWER_COMBAT' in row and row['POWER_COMBAT'].strip():
                data.append(row['POWER_COMBAT'])
    return data

def update_power_combat(data):
    if not data:
        return

    rows = query_db("SELECT card_id FROM cards WHERE power_combat IS NULL OR power_combat = ''")
    
    count = 0
    for i, row in enumerate(rows):
        cid = row['card_id']
        val = data[i % len(data)]
        update_card(cid, 'power_combat', val)
        count += 1
            
    print(f"Updated {count} cards with power_combat.")

def main():
    db_data = read_source_data(SOURCE_FILE)
    update_power_combat(db_data)

if __name__ == "__main__":
    main()
