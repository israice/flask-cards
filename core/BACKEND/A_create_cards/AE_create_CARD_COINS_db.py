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
TARGET_COLUMN_INDEX = 4                   # Index of the column to insert coins next to
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


def patch_csv(csv_path, symbols):
    """
    Read entire CSV, find free cells from bottom (excluding header),
    insert coin list into matching rows, and return new lines.
    """
    # Read all lines
    with open(csv_path, 'r', encoding=FILE_ENCODING) as f:
        raw_lines = [line.rstrip('\n') for line in f]

    if not raw_lines:
        return []

    # Separate header and data rows
    header, data_rows = raw_lines[0], raw_lines[1:]
    patched_count = 0

    # Prepare a mutable list for patched data
    patched_data = data_rows.copy()

    # Iterate from bottom to top over data_rows
    for idx in range(len(data_rows)-1, -1, -1):
        if patched_count >= MAX_PATCHES:
            break

        line = data_rows[idx]
        parts = line.split(CSV_SEPARATOR)

        # Check criteria: enough columns, left column non-empty, not already patched
        if (len(parts) > TARGET_COLUMN_INDEX
            and parts[TARGET_COLUMN_INDEX-1].strip()
            and QUOTE_CHAR not in line):

            # Choose random coins
            count = random.randint(MIN_COINS_COUNT, MAX_COINS_COUNT)
            coins_list = random.sample(symbols, count)
            coins_str = ", ".join(coins_list)

            # Build new line with quoted coins list right after target column
            new_line = CSV_SEPARATOR.join(
                parts[:TARGET_COLUMN_INDEX+1] + [f'{QUOTE_CHAR}{coins_str}{QUOTE_CHAR}']
            )
            # Replace in patched_data at same relative position
            patched_data[idx] = new_line

            patched_count += 1

    # Reconstruct full lines: header + patched data rows
    return [header] + patched_data


def write_csv(csv_path, lines):
    """Write patched lines back to the CSV file."""
    with open(csv_path, 'w', encoding=FILE_ENCODING) as f:
        f.write("\n".join(lines) + "\n")


def main():
    """Main entry point."""
    symbols = load_coin_symbols(COINS_DB_JSON)
    new_lines = patch_csv(SYSTEM_FULL_DB_CSV, symbols)
    write_csv(SYSTEM_FULL_DB_CSV, new_lines)


if __name__ == "__main__":
    main()
