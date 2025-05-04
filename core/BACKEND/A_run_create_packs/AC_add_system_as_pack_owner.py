#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
from dotenv import load_dotenv

# ==== SETTINGS ====
load_dotenv()  # Load environment variables from .env file
INPUT_PATH = os.getenv('SYSTEM_CARDS_CSV')  # Path to the CSV file from .env
OWNER_COLUMN_INDEX = 2  # Index of the column to treat as owner (0-based)
DEFAULT_OWNER = 'SYSTEM'  # Default owner value for empty fields

if not INPUT_PATH:
    print("ERROR: SYSTEM_CARDS_CSV is not set in the .env file.")
    exit(1)

# Ensure the directory for the CSV exists
os.makedirs(os.path.dirname(INPUT_PATH), exist_ok=True)


def main():
    """Main processing function."""
    rows = []

    # Read and process the CSV
    with open(INPUT_PATH, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames or []
        # Validate index
        if OWNER_COLUMN_INDEX < 0 or OWNER_COLUMN_INDEX >= len(fieldnames):
            print(f"ERROR: OWNER_COLUMN_INDEX {OWNER_COLUMN_INDEX} is out of range.")
            exit(1)

        owner_col = fieldnames[OWNER_COLUMN_INDEX]

        for row in reader:
            # If the owner field is missing or empty, set to default
            if row.get(owner_col) is None or row[owner_col].strip() == '':
                row[owner_col] = DEFAULT_OWNER
            rows.append(row)

    # Write updated rows back to the same file
    with open(INPUT_PATH, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
