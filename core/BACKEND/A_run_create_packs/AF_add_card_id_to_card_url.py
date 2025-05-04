#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import csv
from dotenv import load_dotenv

# === SETTINGS ===
load_dotenv()  # Load environment variables from .env
CARDS_CSV_PATH       = os.getenv('SYSTEM_CARDS_CSV')
AUTH_CSV_PATH        = os.getenv('SYSTEM_CARD_AUTH_SCV')
CARDS_ID_COL_INDEX   = 0  # Index of CARD_ID column in system_cards.csv (0-based)
AUTH_KEY_IN_INDEX    = 0  # Index of KEY_IN column in system_card_auth.csv (0-based)
AUTH_KEY_OUT_INDEX   = 1  # Index of KEY_OUT column in system_card_auth.csv (0-based)
AUTH_CARD_ID_INDEX   = 2  # Index of CARD_ID column in system_card_auth.csv (0-based)

# === VALIDATE ENVIRONMENT ===
if not CARDS_CSV_PATH:
    print('Error: environment variable SYSTEM_CARDS_CSV is not set.', file=sys.stderr)
    sys.exit(1)
if not AUTH_CSV_PATH:
    print('Error: environment variable SYSTEM_CARD_AUTH_SCV is not set.', file=sys.stderr)
    sys.exit(1)

def load_card_ids(cards_path):
    """Load CARD_IDs from system_cards.csv into a list using column index."""
    card_ids = []
    with open(cards_path, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, [])
        num_cols = len(header)
        if CARDS_ID_COL_INDEX >= num_cols:
            raise IndexError(f'CARDS_ID_COL_INDEX {CARDS_ID_COL_INDEX} out of range')
        for row in reader:
            # pad row if it's shorter than header
            row += [''] * (num_cols - len(row))
            cid = row[CARDS_ID_COL_INDEX].strip()
            if cid:
                card_ids.append(cid)
    return card_ids

def load_auth_rows(auth_path):
    """
    Load rows from system_card_auth.csv into a list of lists,
    preserving original header row.
    """
    with open(auth_path, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, [])
        rows = [row for row in reader]
    return header, rows

def save_auth_rows(auth_path, header, rows):
    """Write header and rows back to auth CSV safely."""
    temp_path = auth_path + '.tmp'
    with open(temp_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for row in rows:
            # pad each row to match header length
            row += [''] * (len(header) - len(row))
            writer.writerow(row)
    os.replace(temp_path, auth_path)

def fill_next_empty(cards_path, auth_path):
    """
    Find the next CARD_ID from cards file not present in auth file,
    and fill the first empty CARD_ID slot in auth file.
    """
    all_ids = load_card_ids(cards_path)
    header, auth_rows = load_auth_rows(auth_path)

    # Ensure auth rows have enough columns
    for i, row in enumerate(auth_rows):
        if len(row) < len(header):
            auth_rows[i] = row + [''] * (len(header) - len(row))

    # Collect existing CARD_IDs
    existing = {
        row[AUTH_CARD_ID_INDEX].strip()
        for row in auth_rows
        if len(row) > AUTH_CARD_ID_INDEX and row[AUTH_CARD_ID_INDEX].strip()
    }

    # Determine missing IDs
    missing = [cid for cid in all_ids if cid not in existing]
    if not missing:
        print('All CARD_IDs are already assigned.')
        return

    next_id = missing[0]
    # Fill the first empty CARD_ID slot
    for row in auth_rows:
        if row[AUTH_CARD_ID_INDEX].strip() == '':
            row[AUTH_CARD_ID_INDEX] = next_id
            break
    else:
        print('No empty CARD_ID slot found.')
        return

    save_auth_rows(auth_path, header, auth_rows)

if __name__ == '__main__':
    cards_file = sys.argv[1] if len(sys.argv) > 1 else CARDS_CSV_PATH
    auth_file  = sys.argv[2] if len(sys.argv) > 2 else AUTH_CSV_PATH
    fill_next_empty(cards_file, auth_file)
