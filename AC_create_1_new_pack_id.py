#!/usr/bin/env python3
import csv
import random
import os

# ==== SETTINGS ====
FILENAME = 'data/system_cards.csv'
HEADERS = ['PACK_ID', 'CARD_ID']  # Define expected headers
TARGET_COLUMN_INDEX = 1          # Zero-based index for 'CARD_ID'
NUM_IDS_TO_ADD = 1               # number of unique IDs to generate
ID_REPEAT_COUNT = 5              # number of times to repeat each generated ID vertically
ID_PREFIX = 'Pack_'
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
        headers = next(reader, None)
        if headers is None or column_index >= len(headers):
            raise IndexError(f"Column index {column_index} out of range")
        for row in reader:
            if len(row) > column_index and row[column_index].strip():
                existing.add(row[column_index].strip())
    return existing


def ensure_header(filename, headers, dialect):
    """Create file and write header if file is missing or empty or mismatched."""
    need_header = True
    if os.path.exists(filename):
        with open(filename, newline='', encoding='utf-8') as f:
            try:
                existing = next(csv.reader(f, dialect))
                if existing == headers:
                    need_header = False
            except StopIteration:
                need_header = True
    if need_header:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, dialect)
            writer.writerow(headers)


def generate_unique_ids(prefix, existing, count, start, end):
    """Generate a list of unique IDs not in existing set."""
    all_ids = {f"{prefix}{i:06d}" for i in range(start, end + 1)}
    available = list(all_ids - existing)
    if len(available) < count:
        raise ValueError(f"Not enough unique IDs (needed {count}, available {len(available)})")
    return random.sample(available, count)


def append_ids(filename, new_ids, column_index, dialect):
    """Insert new IDs vertically: each in its own row under the target column."""
    with open(filename, newline='', encoding='utf-8') as f:
        rows = list(csv.reader(f, dialect))
    headers = rows[0]
    data = rows[1:]

    for new_id in new_ids:
        for _ in range(ID_REPEAT_COUNT):
            placed = False
            # Fill first available empty cell
            for row in data:
                if len(row) <= column_index:
                    # extend row if shorter
                    row.extend([''] * (column_index + 1 - len(row)))
                if not row[column_index].strip():
                    row[column_index] = new_id
                    placed = True
                    break
            # Append new row if none empty
            if not placed:
                new_row = [''] * len(headers)
                new_row[column_index] = new_id
                data.append(new_row)

    # Write back
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, dialect)
        writer.writerow(headers)
        writer.writerows(data)


def main():
    dialect = csv.get_dialect('excel')
    # Ensure proper header
    ensure_header(FILENAME, HEADERS, dialect)

    try:
        existing = read_existing_ids(FILENAME, TARGET_COLUMN_INDEX, dialect)
    except IndexError as e:
        print(f"ERROR: {e}")
        return

    try:
        unique_ids = generate_unique_ids(
            ID_PREFIX, existing, NUM_IDS_TO_ADD,
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