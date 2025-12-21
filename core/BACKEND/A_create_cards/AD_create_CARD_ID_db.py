#!/usr/bin/env python3
import csv
import random
import os
from dotenv import load_dotenv

# ==== LOAD ENVIRONMENT VARIABLES ====
load_dotenv()
FILENAME = os.getenv('SYSTEM_FULL_DB_CSV')
TARGET_COLUMN_INDEX = 0

if not FILENAME:
    print("ERROR: SYSTEM_FULL_DB_CSV is not set in the .env file.")
    exit(1)

# ==== SETTINGS ====
NUM_IDS_TO_ADD = int(os.getenv("NUMBER_OF_CARDS", 5))
ID_PREFIX = 'Card_'
ID_RANGE_START = 1
ID_RANGE_END = 999999
# ===================

import sys
# Adjust path to import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from core.database import query_db, get_db

def read_existing_ids():
    """Read existing IDs from the DB."""
    rows = query_db("SELECT card_id FROM cards")
    return {r['card_id'] for r in rows}

def insert_ids(new_ids):
    """Insert new IDs into the DB."""
    if not new_ids:
        return
    
    db = get_db()
    for new_id in new_ids:
        # We only insert the primary key, other fields are NULL/Default
        db.execute("INSERT INTO cards (card_id) VALUES (?)", (new_id,))
    db.commit()
    print(f"Inserted {len(new_ids)} new cards.")

def generate_unique_ids(prefix, existing, count, start, end):
    """Generate a list of unique IDs not in existing set."""
    all_ids = {f"{prefix}{i:06d}" for i in range(start, end + 1)}
    available = list(all_ids - existing)
    if len(available) < count:
        raise ValueError(f"Not enough unique IDs (needed {count}, available {len(available)})")
    return random.sample(available, count)

def main():
    existing = read_existing_ids()
    try:
        new_ids = generate_unique_ids(ID_PREFIX, existing, NUM_IDS_TO_ADD, ID_RANGE_START, ID_RANGE_END)
    except ValueError as e:
        print(f"ERROR: {e}")
        return

    insert_ids(new_ids)

if __name__ == '__main__':
    main()

