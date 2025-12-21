#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration section: adjust any setting here.
"""

import os
import csv
import random
from dotenv import load_dotenv

# Load environment variables from .env file (optional)
load_dotenv()

# Path to the CSV file (set in .env as SYSTEM_FULL_DB_CSV or hardcode here)
SYSTEM_FULL_DB_CSV = os.getenv("SYSTEM_FULL_DB_CSV")

# File I/O settings
FILE_ENCODING = "utf-8"

# Column indexes (0-based)
COIN_COLUMN_INDEX   = 6  # coins list is in the 4th column (index 3)
TARGET_COLUMN_INDEX = 7  # insert generated values into the 5th column (index 4)

# Randomization limits
MIN_VALUE = 0.02   # minimum allowed for each generated value
MAX_VALUE = 4.99   # maximum allowed for each generated value
MAX_SUM   = 10.0   # total sum must be ≤ MAX_SUM

# Processing limits (read from .env or adjust here)
MAX_ROWS_TO_SERVE = int(os.getenv("NUMBER_OF_CARDS", "5"))
SKIP_HEADER_ROWS  = int(os.getenv("SKIP_HEADER_ROWS", "1"))  # number of header rows to skip

"""
Main script: reading data, patching CSV, writing result.
"""

def generate_random_values(count,
                           min_value=MIN_VALUE,
                           max_value=MAX_VALUE,
                           max_sum=MAX_SUM):
    """
    Generate `count` random floats rounded to 2 decimals,
    each between min_value and max_value, and total sum ≤ max_sum.
    """
    remaining = max_sum
    values = []
    for i in range(count):
        slots_left = count - i
        max_for_slot = min(
            max_value,
            remaining - (slots_left - 1) * min_value
        )
        if max_for_slot < min_value:
            max_for_slot = min_value
        val = random.uniform(min_value, max_for_slot)
        values.append(round(val, 2))
        remaining -= val
    return values


import sys
# Adjust path to import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from core.database import query_db, update_card

def update_usd_amounts(limit):
    """
    Find cards with coins but empty USD amount, and generate values.
    """
    # Fetch cards that need update
    # Logic from original: if coins exist and usd_amount empty.
    rows = query_db("SELECT card_id, coins FROM cards WHERE (usd_amount IS NULL OR usd_amount = '') AND (coins IS NOT NULL AND coins != '')")
    
    count = 0
    for row in rows:
        if count >= limit:
            break
            
        coins_str = row['coins']
        if not coins_str.strip():
            continue
            
        coins = [c.strip() for c in coins_str.split(',') if c.strip()]
        if not coins:
            continue
            
        values = generate_random_values(len(coins))
        values_str = ", ".join(f"{v:.2f}" for v in values)
        
        update_card(row['card_id'], 'usd_amount', values_str)
        count += 1
        
    print(f"Updated {count} cards with USD amounts.")

def main():
    """Main entry point."""
    limit = MAX_ROWS_TO_SERVE
    update_usd_amounts(limit)

if __name__ == "__main__":
    main()
