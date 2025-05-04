#!/usr/bin/env python3

import os
import sys
import csv
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve CSV paths from environment
CARDS_CSV_PATH = os.getenv('SYSTEM_CARDS_CSV')
AUTH_CSV_PATH  = os.getenv('SYSTEM_CARD_AUTH_SCV')

# Exit with error if paths are not provided
if not CARDS_CSV_PATH:
    print('Error: environment variable SYSTEM_CARDS_CSV is not set.', file=sys.stderr)
    sys.exit(1)
if not AUTH_CSV_PATH:
    print('Error: environment variable SYSTEM_CARD_AUTH_SCV is not set.', file=sys.stderr)
    sys.exit(1)

def load_card_ids(cards_path):
    """
    Load CARD_IDs from system_cards.csv into a list.
    """
    card_ids = []
    with open(cards_path, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cid = row.get('CARD_ID')
            if cid:
                card_ids.append(cid)
    return card_ids

def load_auth_rows(auth_path):
    """
    Load rows from system_card_auth.csv into a list of dicts,
    and capture original header order.
    """
    with open(auth_path, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    return rows, fieldnames

def save_auth_rows(auth_path, rows, fieldnames):
    """
    Write updated rows back to system_card_auth.csv safely,
    writing only 2 columns for rows without CARD_ID.
    """
    temp_path = auth_path + '.tmp'
    with open(temp_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Write header as-is
        writer.writerow(fieldnames)
        # Write each row: 3 fields if CARD_ID exists, else 2 fields
        for row in rows:
            key_in  = row.get('KEY_IN', '')
            key_out = row.get('KEY_OUT', '')
            card    = row.get('CARD_ID')
            if card:
                # write three columns
                writer.writerow([key_in, key_out, card])
            else:
                # write only two columns (no trailing comma)
                writer.writerow([key_in, key_out])
    os.replace(temp_path, auth_path)

def fill_next_empty(cards_path, auth_path):
    """
    Find the next CARD_ID from cards file not present in auth file,
    and fill the first empty CARD_ID slot in auth file.
    """
    all_ids = load_card_ids(cards_path)
    auth_rows, fieldnames = load_auth_rows(auth_path)
    existing = {row['CARD_ID'] for row in auth_rows if row.get('CARD_ID')}

    missing = [cid for cid in all_ids if cid not in existing]
    if not missing:
        return

    next_id = missing[0]
    for row in auth_rows:
        if not row.get('CARD_ID'):
            row['CARD_ID'] = next_id
            break
    else:
        print('No empty CARD_ID slot found.')
        return

    save_auth_rows(auth_path, auth_rows, fieldnames)

if __name__ == '__main__':
    cards_file = sys.argv[1] if len(sys.argv) > 1 else CARDS_CSV_PATH
    auth_file  = sys.argv[2] if len(sys.argv) > 2 else AUTH_CSV_PATH
    fill_next_empty(cards_file, auth_file)
