#!/usr/bin/env python3
import csv
import random
import os
from dotenv import load_dotenv

# ==== LOAD ENVIRONMENT VARIABLES ====
load_dotenv()
FILENAME = os.getenv('SYSTEM_FULL_DB_CSV')
NUM_CARDS_ENV = os.getenv('NUMBER_OF_CARDS')

# ==== SETTINGS ====
TARGET_COLUMN_INDEX = 1    # Zero-based index for 'CARD_ID'
TRIGGER_RUNS = 1           # Number of different IDs (batches) to generate in one run
ID_PREFIX = 'Pack_'
ID_RANGE_START = 1
ID_RANGE_END = 999999
# ===================

# Validate required environment variables
if not FILENAME:
    print("ERROR: SYSTEM_FULL_DB_CSV is not set in the .env file.")
    exit(1)

if not NUM_CARDS_ENV:
    print("ERROR: NUMBER_OF_CARDS is not set in the .env file.")
    exit(1)

try:
    NUMBER_OF_CARDS = int(NUM_CARDS_ENV)  # Number of times to repeat each generated ID
except ValueError:
    print("ERROR: NUMBER_OF_CARDS must be an integer.")
    exit(1)


import sys
# Adjust path to import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from core.database import query_db, update_card

def read_existing_pack_ids():
    rows = query_db("SELECT pack_id FROM cards WHERE pack_id IS NOT NULL AND pack_id != ''")
    return {r['pack_id'] for r in rows}

def update_pack_ids(new_ids, repeat_count):
    """
    Assign each new_id to 'repeat_count' cards that define have empty pack_id.
    """
    # Total needed
    total_needed = len(new_ids) * repeat_count
    
    # Get cards to update
    rows = query_db("SELECT card_id FROM cards WHERE pack_id IS NULL OR pack_id = ''")
    
    current_row_idx = 0
    updated_count = 0
    
    for pid in new_ids:
        for _ in range(repeat_count):
            if current_row_idx >= len(rows):
                break
            
            card_id = rows[current_row_idx]['card_id']
            update_card(card_id, 'pack_id', pid)
            updated_count += 1
            current_row_idx += 1
            
    print(f"Updated {updated_count} cards with pack_id.")

def generate_unique_ids(prefix, existing, count, start, end):
    """Generate a list of unique IDs not in existing set."""
    all_ids = {f"{prefix}{i:06d}" for i in range(start, end + 1)}
    available = list(all_ids - existing)
    if len(available) < count:
        raise ValueError(f"Not enough unique IDs (needed {count}, available {len(available)})")
    return random.sample(available, count)

def main():
    try:
        existing = read_existing_pack_ids()
    except Exception as e:
        print(f"ERROR: {e}")
        return

    try:
        # Generate TRIGGER_RUNS unique IDs
        unique_ids = generate_unique_ids(
            ID_PREFIX, existing, TRIGGER_RUNS,
            ID_RANGE_START, ID_RANGE_END
        )
    except ValueError as e:
        print(f"ERROR: {e}")
        return

    update_pack_ids(unique_ids, NUMBER_OF_CARDS)

if __name__ == '__main__':
    main()
