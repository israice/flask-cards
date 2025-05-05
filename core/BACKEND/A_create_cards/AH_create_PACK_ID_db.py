#!/usr/bin/env python3
import csv
import random
import os
from dotenv import load_dotenv

# ==== LOAD ENVIRONMENT VARIABLES ====
load_dotenv()
FILENAME = os.getenv('SYSTEM_FULL_DB_CSV')
NUM_CARDS_ENV = os.getenv('NUMBER_OF_CARDS')

# ==== SETTINGS ====
TARGET_COLUMN_INDEX = 1    # Zero-based index for 'CARD_ID'
TRIGGER_RUNS = 1           # Number of different IDs (batches) to generate in one run
ID_PREFIX = 'Pack_'
ID_RANGE_START = 1
ID_RANGE_END = 999999
# ===================

# Validate required environment variables
if not FILENAME:
    print("ERROR: SYSTEM_FULL_DB_CSV is not set in the .env file.")
    exit(1)

if not NUM_CARDS_ENV:
    print("ERROR: NUMBER_OF_CARDS is not set in the .env file.")
    exit(1)

try:
    NUMBER_OF_CARDS = int(NUM_CARDS_ENV)  # Number of times to repeat each generated ID
except ValueError:
    print("ERROR: NUMBER_OF_CARDS must be an integer.")
    exit(1)


def read_existing_ids(filename, column_index, dialect):
    """Read existing IDs from the CSV at the target column index without header check."""
    existing = set()
    if not os.path.exists(filename):
        return existing
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.reader(f, dialect)
        for row in reader:
            if len(row) > column_index and row[column_index].strip():
                existing.add(row[column_index].strip())
    return existing

def generate_unique_ids(prefix, existing, count, start, end):
    """Generate a list of unique IDs not in existing set."""
    all_ids = {f"{prefix}{i:06d}" for i in range(start, end + 1)}
    available = list(all_ids - existing)
    if len(available) < count:
        raise ValueError(f"Not enough unique IDs (needed {count}, available {len(available)})")
    return random.sample(available, count)

def append_ids(filename, new_ids, column_index, dialect):
    """Insert new IDs vertically: each in its own row under the target column, preserving existing structure."""
    with open(filename, newline='', encoding='utf-8') as f:
        rows = list(csv.reader(f, dialect))
    headers = rows[0] if rows else []
    data = rows[1:] if rows else []

    for new_id in new_ids:
        for _ in range(NUMBER_OF_CARDS):  # repeat count from .env
            placed = False
            for row in data:
                if len(row) <= column_index:
                    row.extend([''] * (column_index + 1 - len(row)))
                if not row[column_index].strip():
                    row[column_index] = new_id
                    placed = True
                    break
            if not placed:
                new_row = [''] * (len(headers) if headers else column_index + 1)
                new_row[column_index] = new_id
                data.append(new_row)

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, dialect)
        if headers:
            writer.writerow(headers)
        writer.writerows(data)

def main():
    dialect = csv.get_dialect('excel')

    try:
        existing = read_existing_ids(FILENAME, TARGET_COLUMN_INDEX, dialect)
    except Exception as e:
        print(f"ERROR: {e}")
        return

    try:
        # Generate TRIGGER_RUNS unique IDs
        unique_ids = generate_unique_ids(
            ID_PREFIX, existing, TRIGGER_RUNS,
            ID_RANGE_START, ID_RANGE_END
        )
    except ValueError as e:
        print(f"ERROR: {e}")
        return

    try:
        append_ids(FILENAME, unique_ids, TARGET_COLUMN_INDEX, dialect)
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == '__main__':
    main()
