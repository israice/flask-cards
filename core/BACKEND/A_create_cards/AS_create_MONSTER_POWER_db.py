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
        reader = csv.DictReader(csvfile) # Use DictReader as header exists
        for row in reader:
            if 'MONSTER_POWER' in row and row['MONSTER_POWER'].strip():
                data.append(row['MONSTER_POWER'])
    return data

def update_monster_power(data):
    if not data:
        return

    rows = query_db("SELECT card_id FROM cards WHERE monster_power IS NULL OR monster_power = ''")
    
    count = 0
    for i, row in enumerate(rows):
        cid = row['card_id']
        val = data[i % len(data)]
        update_card(cid, 'monster_power', val)
        count += 1
            
    print(f"Updated {count} cards with monster_power.")

def main():
    powers = read_source_data(SOURCE_FILE)
    update_monster_power(powers)

if __name__ == "__main__":
    main()
