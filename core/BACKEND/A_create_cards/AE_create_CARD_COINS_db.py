#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration section: adjust any setting here.
"""

import os
import json
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# File paths (from .env or defaults)
COINS_DB_JSON       = os.getenv("COINS_DB_JSON")
SYSTEM_FULL_DB_CSV  = os.getenv("SYSTEM_FULL_DB_CSV")

# Encoding for file I/O
FILE_ENCODING       = "utf-8"

# CSV processing settings
CSV_SEPARATOR       = ","                 # Field separator in CSV
TARGET_COLUMN_INDEX = 5                   # Index of the column to insert coins next to
QUOTE_CHAR          = '"'                 # Quote character to wrap coin list

# Randomization settings
MIN_COINS_COUNT     = 2                   # Minimum number of coins to pick
MAX_COINS_COUNT     = 7                   # Maximum number of coins to pick

# Patching settings (loaded from .env)
MAX_PATCHES         = int(os.getenv("NUMBER_OF_CARDS", "5"))  # Default to 5 if not set

"""
Main script: reading data, patching CSV, writing result.
"""

def load_coin_symbols(json_path):
    """Load coin symbols from JSON database."""
    with open(json_path, 'r', encoding=FILE_ENCODING) as f:
        data = json.load(f)
    # Ensure symbols are uppercase strings
    return [item['symbol'].upper() for item in data]


import sys
# Adjust path to import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from core.database import query_db, update_card

def update_coins(symbols, limit):
    """
    Find cards with description but empty coins, and insert random coins.
    """
    # Logic: if description exists and coins empty.
    rows = query_db("SELECT card_id FROM cards WHERE (coins IS NULL OR coins = '') AND (description IS NOT NULL AND description != '')")
    
    count = 0
    for row in rows:
        if count >= limit:
            break
            
        card_id = row['card_id']
        
        # Choose random coins
        num_coins = random.randint(MIN_COINS_COUNT, MAX_COINS_COUNT)
        coins_list = random.sample(symbols, num_coins)
        coins_str = ", ".join(coins_list)
        
        update_card(card_id, 'coins', coins_str)
        count += 1
        
    print(f"Updated {count} cards with coins.")

def main():
    """Main entry point."""
    symbols = load_coin_symbols(COINS_DB_JSON)
    limit = MAX_PATCHES
    update_coins(symbols, limit)


if __name__ == "__main__":
    main()
