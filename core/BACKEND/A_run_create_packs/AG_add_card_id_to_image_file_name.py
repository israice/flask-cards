#!/usr/bin/env python3

"""
Script to rename the first non-Card_ file in the cards folder
using the next available CARD_ID from the system_card_auth CSV.
"""

# Load environment variables and configuration
from dotenv import load_dotenv
load_dotenv()

import os
import pandas as pd

# Configuration (read from .env)
CARDS_BANK_FOLDER = os.getenv('CARDS_BANK_FOLDER')
SYSTEM_CARD_AUTH_SCV = os.getenv('SYSTEM_CARD_AUTH_SCV')

# Validate configuration
if not CARDS_BANK_FOLDER:
    print('Error: CARDS_BANK_FOLDER not set in environment variables.')
    exit(1)
if not SYSTEM_CARD_AUTH_SCV:
    print('Error: SYSTEM_CARD_AUTH_SCV not set in environment variables.')
    exit(1)

# Paths
cards_dir = CARDS_BANK_FOLDER
csv_path = SYSTEM_CARD_AUTH_SCV


def main():
    # Read CARD_ID values from CSV, skipping NaN
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV at '{csv_path}': {e}")
        exit(1)

    if 'CARD_ID' not in df.columns:
        print("Error: CSV does not contain 'CARD_ID' column.")
        exit(1)

    card_ids = df['CARD_ID'].dropna().astype(str).tolist()

    # List files in cards directory
    try:
        files = [f for f in os.listdir(cards_dir)
                 if os.path.isfile(os.path.join(cards_dir, f))]
    except Exception as e:
        print(f"Error listing directory '{cards_dir}': {e}")
        exit(1)

    # Find first file without 'Card_' prefix
    file_to_rename = next((f for f in files if not f.startswith('Card_')), None)
    if not file_to_rename:
        exit(0)

    # Determine existing base names
    existing_bases = {os.path.splitext(f)[0] for f in files}

    # Pick the first available CARD_ID
    new_id = next((cid for cid in card_ids if cid and cid not in existing_bases), None)
    if not new_id:
        print('No available CARD_ID found that is not already used.')
        exit(0)

    # Rename file
    old_path = os.path.join(cards_dir, file_to_rename)
    ext = os.path.splitext(file_to_rename)[1]
    new_name = new_id + ext
    new_path = os.path.join(cards_dir, new_name)

    try:
        os.rename(old_path, new_path)
    except Exception as e:
        print(f"Error renaming file '{file_to_rename}' to '{new_name}': {e}")


if __name__ == '__main__':
    main()
