import os
import csv
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration: target column index (1-based)
COLUMN_INDEX = 12

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

import sys
# Adjust path to import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from core.database import query_db, update_card

def update_empty_cells(names):
    """
    Find cards with empty card_type and update them.
    """
    rows = query_db("SELECT card_id FROM cards WHERE card_type IS NULL OR card_type = ''")
    
    count = 0
    for i, name in enumerate(names):
        if i >= len(rows):
            break
        card_id = rows[i]['card_id']
        update_card(card_id, 'card_type', name)
        count += 1
    
    print(f"Updated {count} cards with new card_type.")

def main():
    # Prepare list with a random blockchain type for each card
    card_list = [select_one_blockchain() for _ in range(NUMBER_OF_CARDS)]
    
    update_empty_cells(card_list)

if __name__ == "__main__":
    main()
