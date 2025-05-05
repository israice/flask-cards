import os
import csv
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration: target column index (1-based)
COLUMN_INDEX = 11

# Read number of entries to pick strictly from environment variable
# Raise error if missing or not an integer
try:
    NUMBER_OF_CARDS = int(os.environ["NUMBER_OF_CARDS"])
except KeyError:
    raise RuntimeError("Environment variable NUMBER_OF_CARDS is required")
except ValueError:
    raise RuntimeError("Environment variable NUMBER_OF_CARDS must be an integer")

# List of all possible card rarity types
CARD_TYPE = [
    "Legendary",              # classic high-value tier
    "Super Legendary",        # rarer than Legendary
    "Alpha Type",             # first-print, early release
    "Mythic",                 # exceptionally scarce
    "Ultra Mythic",           # extreme scarcity
    "Masterpiece",            # premium art & materials
    "Collector's Edition",    # special limited release
    "Grail",                  # ultimate, one-of-a-kind status
    "Divine",                 # revered, almost unattainable
    "Supreme",                # pinnacle of standard rarity lines
    "Cosmic",                 # rarity from another realm
    "Eternal",                # timeless collectible prestige
    "Genesis",                # origin series, inaugural batch
    "Prototype",              # pre-production sample
    "Signature Series",       # personally signed or stamped
    "Royal",                  # reserved for tournament champions
    "Immortal",               # forever enshrined in lore
    "Celestial",              # heavenly, star-tier rarity
    "Phantom",                # rumored, rarely seen
    "Shadow",                 # secret print with dark variant
    "Zenith",                 # highest point in rarity arc
    "Apex",                   # literally “top of the top”
    "Infinity",               # conceptually limitless value
    "Primordial",             # ancient, predating main sets
    "Relic",                  # historic artifact tier
    "Vanguard",               # leading edge of special sets
    "Legacy",                 # famed for competitive heritage
    "Emperor",                # reserved for prize promos
    "Godlike",               # beyond conventional scales
    "Transcendent"            # surpassing all known tiers
]

def select_one_blockchain():
    """
    Select a single blockchain randomly from CARD_TYPE.
    """
    return random.choice(CARD_TYPE)

def insert_into_first_empty_cells(names, file_path):
    """
    Read all rows, find first empty cells in target column, and insert names there.
    """
    # Read existing data
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        rows = [row for row in reader]
    
    # Count how many non-empty entries already in the column
    existing = 0
    for row in rows:
        if len(row) >= COLUMN_INDEX and row[COLUMN_INDEX-1].strip():
            existing += 1
    
    # Insert each name into the next empty cell
    for name in names:
        idx = existing  # 0-based row index where to insert
        if idx < len(rows):
            row = rows[idx]
            # ensure row has enough columns
            if len(row) < COLUMN_INDEX:
                row.extend([''] * (COLUMN_INDEX - len(row)))
            row[COLUMN_INDEX-1] = name
        else:
            # create a new row with empty cols up to target, then name
            new_row = [''] * (COLUMN_INDEX - 1) + [name]
            rows.append(new_row)
        existing += 1

    # Write back updated data
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)

def main():
    # Path to the CSV file
    file_path = os.path.join("core", "data", "system_full_db.csv")
    
    # Prepare list with a random blockchain type for each card
    card_list = [select_one_blockchain() for _ in range(NUMBER_OF_CARDS)]
    
    # Insert into first free cells in the target column
    insert_into_first_empty_cells(card_list, file_path)

if __name__ == "__main__":
    main()
