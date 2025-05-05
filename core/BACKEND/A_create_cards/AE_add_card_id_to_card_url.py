#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import csv
from pathlib import Path
from dotenv import load_dotenv

# === CONFIGURATION ===
# Environment variable names
SYSTEM_CARDS_CSV_VAR = 'SYSTEM_CARDS_CSV'
SYSTEM_CARD_AUTH_SCV_VAR = 'SYSTEM_CARD_AUTH_SCV'
CARD_ASSIGN_COUNT_VAR = 'CARD_ASSIGN_COUNT'  # NEW: number of CARD_IDs to assign

# Column indices (0-based)
CARDS_ID_COL_INDEX = 0         # Index of CARD_ID in system_cards.csv
AUTH_CARD_ID_INDEX = 2         # Index of CARD_ID in system_card_auth.csv

# Default count if env var not set or invalid
DEFAULT_ASSIGN_COUNT = 5

# === ERROR HANDLING ===
def die(msg):
    """Print error and exit."""
    print(f'Error: {msg}', file=sys.stderr)
    sys.exit(1)

# === LOAD ENVIRONMENT VARIABLES ===
load_dotenv()
CARDS_CSV_PATH = Path(os.getenv(SYSTEM_CARDS_CSV_VAR, '')).resolve()
AUTH_CSV_PATH  = Path(os.getenv(SYSTEM_CARD_AUTH_SCV_VAR, '')).resolve()
try:
    ASSIGN_COUNT = int(os.getenv(CARD_ASSIGN_COUNT_VAR, DEFAULT_ASSIGN_COUNT))
    if ASSIGN_COUNT < 1:
        raise ValueError
except ValueError:
    ASSIGN_COUNT = DEFAULT_ASSIGN_COUNT

# === VALIDATION ===
if not CARDS_CSV_PATH:
    die(f'{SYSTEM_CARDS_CSV_VAR} is not set or empty')
if not AUTH_CSV_PATH:
    die(f'{SYSTEM_CARD_AUTH_SCV_VAR} is not set or empty')
if not CARDS_CSV_PATH.exists():
    die(f'Cards file not found: {CARDS_CSV_PATH}')
if not AUTH_CSV_PATH.exists():
    die(f'Auth file not found: {AUTH_CSV_PATH}')

def load_card_ids(path: Path):
    """Load CARD_IDs from cards CSV."""
    ids = []
    with path.open('r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None or CARDS_ID_COL_INDEX >= len(header):
            die('Invalid cards CSV header or index out of range')
        for row in reader:
            row += [''] * (len(header) - len(row))
            cid = row[CARDS_ID_COL_INDEX].strip()
            if cid:
                ids.append(cid)
    return ids

def load_auth_rows(path: Path):
    """Load auth CSV header and rows."""
    with path.open('r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None or AUTH_CARD_ID_INDEX >= len(header):
            die('Invalid auth CSV header or index out of range')
        rows = [row for row in reader]
    return header, rows

def save_auth_rows(path: Path, header, rows):
    """Save auth CSV atomically, trimming trailing empty cells."""
    temp = path.with_suffix(path.suffix + '.tmp')
    with temp.open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for row in rows:
            # Determine last non-empty cell index; ensure at least 2 columns
            last = max(1, max((i for i, cell in enumerate(row) if cell.strip()), default=1))
            writer.writerow(row[:last+1])
    temp.replace(path)

def fill_next_empty(cards_path: Path, auth_path: Path, count: int):
    """Find next unassigned CARD_IDs and fill the first empty slots."""
    all_ids = load_card_ids(cards_path)
    header, auth_rows = load_auth_rows(auth_path)
    # Normalize rows length
    for i, row in enumerate(auth_rows):
        if len(row) < len(header):
            auth_rows[i] = row + [''] * (len(header) - len(row))
    # Existing IDs set
    existing = {r[AUTH_CARD_ID_INDEX].strip() for r in auth_rows if r[AUTH_CARD_ID_INDEX].strip()}
    missing = [cid for cid in all_ids if cid not in existing]
    if not missing:
        print('No missing CARD_IDs to assign.')
        return
    # Assign up to 'count' IDs to empty rows
    assigned = 0
    for next_id in missing:
        for row in auth_rows:
            if not row[AUTH_CARD_ID_INDEX].strip():
                row[AUTH_CARD_ID_INDEX] = next_id
                assigned += 1
                break
        if assigned >= count:
            break
    save_auth_rows(auth_path, header, auth_rows)

# Execute on import or run
fill_next_empty(CARDS_CSV_PATH, AUTH_CSV_PATH, ASSIGN_COUNT)

print("CARD new URL owner")
