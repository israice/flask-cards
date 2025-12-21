import os
import csv
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration: target column index (1-based)
COLUMN_INDEX = 11  # e.g. 6 means the sixth column

# Read number of entries to pick strictly from environment variable
# Raise error if missing or not an integer
try:
    NUMBER_OF_CARDS = int(os.environ["NUMBER_OF_CARDS"])
except KeyError:
    raise RuntimeError("Environment variable NUMBER_OF_CARDS is required")
except ValueError:
    raise RuntimeError("Environment variable NUMBER_OF_CARDS must be an integer")


THEMES = [
    "Games",
    "Design",
    "Tech innovations",
    "Film",
    "Music",
    "Publishing",
    "Art",
    "Charity",
    "Tourism"  
]

def select_one_blockchain():
    """
    Select a single blockchain randomly from THEMES.
    """
    return random.choice(THEMES)

import sys
# Adjust path to import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from core.database import query_db, update_card

def update_theme(theme_name, count_needed):
    """
    Update empty theme with selected theme_name.
    """
    rows = query_db("SELECT card_id FROM cards WHERE theme IS NULL OR theme = ''")
    
    count = 0
    for i, row in enumerate(rows):
        if count >= count_needed:
            break
        
        update_card(row['card_id'], 'theme', theme_name)
        count += 1
    
    print(f"Updated {count} cards with theme {theme_name}.")

def main():
    # Select one random blockchain
    chosen = select_one_blockchain()
    update_theme(chosen, NUMBER_OF_CARDS)

if __name__ == "__main__":
    main()
