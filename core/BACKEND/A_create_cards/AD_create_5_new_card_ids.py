#!/usr/bin/env python3
import csv
import random
import os
from dotenv import load_dotenv

# ==== LOAD ENVIRONMENT VARIABLES ====
load_dotenv()
FILENAME = os.getenv('SYSTEM_FULL_DB_CSV')
TARGET_COLUMN_INDEX = 2

if not FILENAME:
    print("ERROR: SYSTEM_FULL_DB_CSV is not set in the .env file.")
    exit(1)

# ==== SETTINGS ====
NUM_IDS_TO_ADD = 5
ID_PREFIX = 'Card_'
ID_RANGE_START = 1
ID_RANGE_END = 999999
# ===================

def detect_dialect(filename, sample_size=2048):
    """Detect the CSV dialect from a sample of the file."""
    with open(filename, newline='', encoding='utf-8') as f:
        sample = f.read(sample_size)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample)
        except csv.Error:
            dialect = csv.get_dialect('excel')
    return dialect

def read_existing_ids(filename, column_index, dialect):
    """Read existing IDs from the CSV at the target column index."""
    existing = set()
    if not os.path.exists(filename):
        return existing
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.reader(f, dialect)
        next(reader, None)  # Skip first row if it's header or data
        for row in reader:
            if len(row) > column_index and row[column_index].strip():
                parts = [p.strip() for p in row[column_index].split(',') if p.strip()]
                existing.update(parts)
    return existing

def generate_unique_ids(prefix, existing, count, start, end):
    """Generate a list of unique IDs not in existing set."""
    all_ids = {f"{prefix}{i:06d}" for i in range(start, end + 1)}
    available = list(all_ids - existing)
    if len(available) < count:
        raise ValueError(f"Not enough unique IDs (needed {count}, available {len(available)})")
    return random.sample(available, count)

def append_ids(filename, new_ids, column_index, dialect):
    """Insert or append new IDs into existing rows or create new rows without extra commas."""
    # Read all existing rows
    if os.path.exists(filename):
        with open(filename, newline='', encoding='utf-8') as f:
            rows = list(csv.reader(f, dialect))
    else:
        rows = []

    # Append or insert new IDs
    for new_id in new_ids:
        placed = False
        # Try to append to comma-starting cell
        for row in rows:
            if len(row) > column_index and row[column_index].startswith(','):
                row[column_index] = f"{row[column_index]}{new_id}"
                placed = True
                break
        if placed:
            continue
        # Try to fill empty cell
        for row in rows:
            if len(row) <= column_index:
                # Extend row to needed length
                row.extend([''] * (column_index + 1 - len(row)))
            if not row[column_index].strip():
                row[column_index] = new_id
                placed = True
                break
        if placed:
            continue
        # Append new row
        new_row = [''] * (column_index + 1)
        new_row[column_index] = new_id
        rows.append(new_row)

    # Write rows back without creating extra columns
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, dialect)
        writer.writerows(rows)

def main():
    dialect = detect_dialect(FILENAME)

    try:
        existing = read_existing_ids(FILENAME, TARGET_COLUMN_INDEX, dialect)
    except IndexError as e:
        print(f"ERROR: {e}")
        return

    try:
        new_ids = generate_unique_ids(ID_PREFIX, existing, NUM_IDS_TO_ADD, ID_RANGE_START, ID_RANGE_END)
    except ValueError as e:
        print(f"ERROR: {e}")
        return

    try:
        append_ids(FILENAME, new_ids, TARGET_COLUMN_INDEX, dialect)
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == '__main__':
    main()

