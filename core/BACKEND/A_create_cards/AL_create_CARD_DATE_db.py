import os
import csv
from datetime import date
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration: target column index (1-based)
COLUMN_INDEX = 3

# Read number of entries to pick strictly from environment variable
# Raise error if missing or not an integer
try:
    NUMBER_OF_CARDS = int(os.environ["NUMBER_OF_CARDS"])
except KeyError:
    raise RuntimeError("Environment variable NUMBER_OF_CARDS is required")
except ValueError:
    raise RuntimeError("Environment variable NUMBER_OF_CARDS must be an integer")

# Read CSV path from environment variable
try:
    FILE_PATH = os.environ["SYSTEM_FULL_DB_CSV"]
except KeyError:
    raise RuntimeError("Environment variable SYSTEM_FULL_DB_CSV is required")

def select_today_date():
    """
    Return today's date in YYYY-MM-DD format.
    """
    return date.today().isoformat()

import sys
# Adjust path to import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from core.database import query_db, update_card

def update_dates(today, count_needed):
    rows = query_db("SELECT card_id FROM cards WHERE card_date IS NULL OR card_date = ''")
    
    count = 0
    for i, row in enumerate(rows):
        if count >= count_needed:
            break
        
        update_card(row['card_id'], 'card_date', today)
        count += 1
    
    print(f"Updated {count} cards with card_date.")

def main():
    today = select_today_date()
    update_dates(today, NUMBER_OF_CARDS)

if __name__ == "__main__":
    main()
