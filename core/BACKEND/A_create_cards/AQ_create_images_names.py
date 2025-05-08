#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import pandas as pd
from dotenv import load_dotenv

# === LOAD ENVIRONMENT VARIABLES ===
ENV_FILE = '.env'
load_dotenv(ENV_FILE)  # Load variables from .env before calling getenv

# === SETTINGS ===
CARDS_BANK_FOLDER = os.getenv('CARDS_BANK_FOLDER')            # Folder with card files
SYSTEM_FULL_DB_CSV = os.getenv('SYSTEM_FULL_DB_CSV')      # Path to auth CSV
CARD_ID_COL_INDEX = 0                                         # Index of CARD_ID column (0-based)
PREFIX = 'Card_'                                              # Files with this prefix are skipped

# === VALIDATE CONFIGURATION ===
if not CARDS_BANK_FOLDER:
    print('Error: CARDS_BANK_FOLDER not set in environment variables.', file=sys.stderr)
    sys.exit(1)
if not SYSTEM_FULL_DB_CSV:
    print('Error: SYSTEM_FULL_DB_CSV not set in environment variables.', file=sys.stderr)
    sys.exit(1)

def main():
    """Rename all non-prefixed files to next available CARD_IDs based on column index."""
    # Read CSV into DataFrame
    try:
        df = pd.read_csv(SYSTEM_FULL_DB_CSV, dtype=str)
    except Exception as e:
        print(f"Error reading CSV at '{SYSTEM_FULL_DB_CSV}': {e}", file=sys.stderr)
        sys.exit(1)

    # Validate index
    cols = list(df.columns)
    if CARD_ID_COL_INDEX < 0 or CARD_ID_COL_INDEX >= len(cols):
        print(f"Error: CARD_ID_COL_INDEX {CARD_ID_COL_INDEX} is out of range (0–{len(cols)-1}).", file=sys.stderr)
        sys.exit(1)

    # Determine column name for CARD_ID
    card_id_col = cols[CARD_ID_COL_INDEX]

    # Extract existing CARD_IDs (non-null, non-empty)
    card_ids = df[card_id_col].dropna().astype(str).str.strip().tolist()

    # List files in cards directory
    try:
        files = [f for f in os.listdir(CARDS_BANK_FOLDER)
                 if os.path.isfile(os.path.join(CARDS_BANK_FOLDER, f))]
    except Exception as e:
        print(f"Error listing directory '{CARDS_BANK_FOLDER}': {e}", file=sys.stderr)
        sys.exit(1)

    # Track base names already in use to avoid collisions
    existing_bases = {os.path.splitext(f)[0] for f in files}

    # Iterate through all files without the prefix
    for filename in sorted(files):
        if filename.startswith(PREFIX):
            continue

        # Determine next available CARD_ID not already used
        new_id = next((cid for cid in card_ids if cid and cid not in existing_bases), None)
        if not new_id:
            break  # Or continue to try other files? here we stop since no IDs remain

        # Prepare new file name
        old_path = os.path.join(CARDS_BANK_FOLDER, filename)
        ext = os.path.splitext(filename)[1]
        new_name = new_id + ext
        new_path = os.path.join(CARDS_BANK_FOLDER, new_name)

        # Perform rename
        try:
            os.rename(old_path, new_path)
            # Mark this ID/base as used
            existing_bases.add(new_id)
        except Exception as e:
            print(f"Error renaming '{filename}' to '{new_name}': {e}", file=sys.stderr)

if __name__ == '__main__':
    main()



