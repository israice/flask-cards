#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration section: adjust any setting here.
"""

import os
import csv
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Path to the CSV file (set in .env as SYSTEM_FULL_DB_CSV)
SYSTEM_FULL_DB_CSV = os.getenv("SYSTEM_FULL_DB_CSV", "path/to/your.csv")

# File I/O settings
FILE_ENCODING = "utf-8"

# Column indexes (0-based)
COIN_COLUMN_INDEX   = 3  # coins list is in the 4th column
TARGET_COLUMN_INDEX = 4  # insert generated values into the 5th column

# Randomization limits
MIN_VALUE = 0.02   # minimum allowed for each generated value
MAX_VALUE = 4.99   # maximum allowed for each generated value
MAX_SUM   = 10.0   # total sum must be ≤ MAX_SUM

# Processing limit: maximum number of rows to patch (read from .env NUMBER_OF_CARDS)
MAX_ROWS_TO_SERVE = int(os.getenv("NUMBER_OF_CARDS", "5"))


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
        max_for_slot = min(max_value,
                           remaining - (slots_left - 1) * min_value)
        if max_for_slot < min_value:
            max_for_slot = min_value
        val = random.uniform(min_value, max_for_slot)
        values.append(round(val, 2))
        remaining -= val
    return values


def patch_csv(path):
    """
    Read CSV, parse coin list at COIN_COLUMN_INDEX,
    generate random values and insert/fill the cell at TARGET_COLUMN_INDEX
    for up to MAX_ROWS_TO_SERVE rows.
    Returns tuple (patched_rows, patched_count).
    """
    patched_rows = []
    patched_count = 0

    with open(path, newline='', encoding=FILE_ENCODING) as infile:
        reader = csv.reader(infile)
        for row in reader:
            if (patched_count < MAX_ROWS_TO_SERVE
                    and len(row) > COIN_COLUMN_INDEX
                    and row[COIN_COLUMN_INDEX].strip()):
                coins = [c.strip() for c in row[COIN_COLUMN_INDEX].split(',') if c.strip()]
                if coins and (len(row) <= TARGET_COLUMN_INDEX or not row[TARGET_COLUMN_INDEX].strip()):
                    values = generate_random_values(len(coins))
                    values_str = ", ".join(f"{v:.2f}" for v in values)
                    if len(row) <= TARGET_COLUMN_INDEX:
                        row.insert(TARGET_COLUMN_INDEX, values_str)
                    else:
                        row[TARGET_COLUMN_INDEX] = values_str
                    patched_count += 1
            patched_rows.append(row)

    return patched_rows, patched_count


def write_csv(path, rows):
    """Write modified rows back to the CSV file."""
    with open(path, 'w', newline='', encoding=FILE_ENCODING) as outfile:
        writer = csv.writer(outfile)
        writer.writerows(rows)


def main():
    """Main entry point."""
    updated_rows, patched_count = patch_csv(SYSTEM_FULL_DB_CSV)
    write_csv(SYSTEM_FULL_DB_CSV, updated_rows)

if __name__ == "__main__":
    main()