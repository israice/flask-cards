#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import pandas as pd
from dotenv import load_dotenv

# === SETTINGS ===
ENV_FILE = '.env'
CARDS_BANK_FOLDER = os.getenv('CARDS_BANK_FOLDER')            # Folder with card files
SYSTEM_CARD_AUTH_SCV = os.getenv('SYSTEM_CARD_AUTH_SCV')      # Path to auth CSV
CARD_ID_COL_INDEX = 2                                         # Index of CARD_ID column (0-based)

# === VALIDATE CONFIGURATION ===
load_dotenv(ENV_FILE)

if not CARDS_BANK_FOLDER:
    print('Error: CARDS_BANK_FOLDER not set in environment variables.', file=sys.stderr)
    sys.exit(1)
if not SYSTEM_CARD_AUTH_SCV:
    print('Error: SYSTEM_CARD_AUTH_SCV not set in environment variables.', file=sys.stderr)
    sys.exit(1)

def main():
    """Rename first non-prefixed file to next available CARD_ID based on column index."""
    # Read CSV into DataFrame
    try:
        df = pd.read_csv(SYSTEM_CARD_AUTH_SCV, dtype=str)
    except Exception as e:
        print(f"Error reading CSV at '{SYSTEM_CARD_AUTH_SCV}': {e}", file=sys.stderr)
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

    # Find first file without 'Card_' prefix
    file_to_rename = next((f for f in files if not f.startswith('Card_')), None)
    if not file_to_rename:
        # Nothing to rename
        return

    # Determine existing base names to avoid collisions
    existing_bases = {os.path.splitext(f)[0] for f in files}

    # Pick the first available CARD_ID not already used as a filename
    new_id = next((cid for cid in card_ids if cid and cid not in existing_bases), None)
    if not new_id:
        print('No available CARD_ID found that is not already used.', file=sys.stderr)
        return

    # Perform rename
    old_path = os.path.join(CARDS_BANK_FOLDER, file_to_rename)
    ext = os.path.splitext(file_to_rename)[1]
    new_name = new_id + ext
    new_path = os.path.join(CARDS_BANK_FOLDER, new_name)

    try:
        os.rename(old_path, new_path)
    except Exception as e:
        print(f"Error renaming file '{file_to_rename}' to '{new_name}': {e}", file=sys.stderr)

if __name__ == '__main__':
    main()
