import os
import csv
from dotenv import load_dotenv

# --- Settings ---
COLUMN_INDEX = 3  # Index of the column to update (changeable)
ENV_FILE = '.env'  # Path to .env file
CSV_ENV_KEY = 'SYSTEM_FULL_DB_CSV'  # Key in .env file for CSV file path
COUNT_ENV_KEY = 'NUMBER_OF_CARDS'  # Key in .env file for number of rows
WORD_TO_INSERT = 'SYSTEM'  # Word to insert

# --- Load environment ---
load_dotenv(ENV_FILE)
csv_path = os.getenv(CSV_ENV_KEY)
num_rows_str = os.getenv(COUNT_ENV_KEY)

if not csv_path:
    raise ValueError(f"Environment variable '{CSV_ENV_KEY}' not found in {ENV_FILE}")
if not num_rows_str or not num_rows_str.isdigit():
    raise ValueError(f"Environment variable '{COUNT_ENV_KEY}' not found or invalid in {ENV_FILE}")

num_rows_to_add = int(num_rows_str)

import sys
# Adjust path to import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from core.database import query_db, update_card

def update_user_type(count_needed):
    """
    Update empty user_type with 'SYSTEM'.
    """
    rows = query_db("SELECT card_id FROM cards WHERE user_type IS NULL OR user_type = ''")
    
    count = 0
    for i, row in enumerate(rows):
        if count >= count_needed:
            break
        
        update_card(row['card_id'], 'user_type', WORD_TO_INSERT)
        count += 1
    
    print(f"Updated {count} cards with user_type.")

def main():
    if not num_rows_str or not num_rows_str.isdigit():
        print(f"Invalid NUMBER_OF_CARDS: {num_rows_str}")
        return

    update_user_type(int(num_rows_str))

if __name__ == "__main__":
    main()

