#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
from dotenv import load_dotenv

# ==== SETTINGS ====
load_dotenv()  # Load environment variables from .env file
INPUT_PATH = os.getenv('SYSTEM_CARDS_CSV')  # Path to the CSV file from .env
# Configurable column indexes
PACK_COLUMN_INDEX = int(os.getenv('PACK_COLUMN_INDEX', '1'))   # Default PACK_ID column index
OWNER_COLUMN_INDEX = int(os.getenv('OWNER_COLUMN_INDEX', '2')) # Default OWNER column index
# Default owner for rows with PACK_ID but missing owner
DEFAULT_OWNER = os.getenv('DEFAULT_OWNER', 'SYSTEM')

if not INPUT_PATH:
    print("ERROR: SYSTEM_CARDS_CSV is not set in the .env file.")
    exit(1)

# Ensure the directory for the CSV exists
os.makedirs(os.path.dirname(INPUT_PATH), exist_ok=True)


def process_cards(input_path):
    """Process the CSV to adjust row output depending on PACK_ID presence and OWNER column index."""
    output_rows = []

    # Read the input file
    with open(input_path, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        header = next(reader, None)

        # Append header unchanged
        output_rows.append(header)
        # Determine the maximum index we need to ensure in each row
        max_index = max(PACK_COLUMN_INDEX, OWNER_COLUMN_INDEX)

        for row in reader:
            # Ensure row has enough columns for index lookup
            while len(row) <= max_index:
                row.append('')

            card_id = row[0].strip()
            pack_id = row[PACK_COLUMN_INDEX].strip()
            owner = row[OWNER_COLUMN_INDEX].strip()

            if not pack_id:
                # If PACK_ID is missing, output only CARD_ID
                output_rows.append([card_id])
            else:
                # If OWNER missing but PACK_ID exists, use default owner
                if not owner:
                    owner = DEFAULT_OWNER
                output_rows.append([card_id, pack_id, owner])

    # Write updated rows back to the same file
    with open(input_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        for r in output_rows:
            writer.writerow(r)


def main():
    process_cards(INPUT_PATH)


if __name__ == "__main__":
    main()
