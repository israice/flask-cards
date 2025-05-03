#!/usr/bin/env python3
import csv
import random
import os

# ==== SETTINGS ====
FILENAME = 'data/system_cards.csv'
TARGET_COLUMN_INDEX = 0       # Zero-based index (0 = first column)
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
        headers = next(reader, None)
        if headers is None or column_index >= len(headers):
            raise IndexError(f"Column index {column_index} out of range")
        for row in reader:
            if len(row) > column_index and row[column_index].strip():
                # split by comma, strip spaces
                parts = [p.strip() for p in row[column_index].split(',') if p.strip()]
                existing.update(parts)
    return existing


def ensure_header(filename, headers, dialect):
    """Create file and write header if file is missing or empty."""
    need_header = True
    if os.path.exists(filename):
        with open(filename, newline='', encoding='utf-8') as f:
            try:
                first = next(csv.reader(f, dialect))
                if first:
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
    """Insert or append new IDs into existing rows or create new rows."""
    with open(filename, newline='', encoding='utf-8') as f:
        rows = list(csv.reader(f, dialect))
    headers = rows[0]
    data = rows[1:]

    if column_index >= len(headers):
        raise IndexError(f"Column index {column_index} out of range for headers")

    for new_id in new_ids:
        placed = False
        # 1) Try to find a cell starting with comma (previous delimiter)
        for row in data:
            cell = row[column_index]
            if cell.startswith(','):
                row[column_index] = f"{cell}{new_id}"
                placed = True
                break
        if placed:
            continue
        # 2) Try to fill empty cells
        for row in data:
            if not row[column_index].strip():
                row[column_index] = new_id
                placed = True
                break
        # 3) If not placed, append new row
        if not placed:
            new_row = [''] * len(headers)
            new_row[column_index] = new_id
            data.append(new_row)

    # Write back all rows
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, dialect)
        writer.writerow(headers)
        writer.writerows(data)


def main():
    dialect = detect_dialect(FILENAME)
    headers = []
    if os.path.exists(FILENAME):
        with open(FILENAME, newline='', encoding='utf-8') as f:
            headers = next(csv.reader(f, dialect), [])
    if not headers or TARGET_COLUMN_INDEX >= len(headers):
        headers = [f"Column_{i}" for i in range(TARGET_COLUMN_INDEX + 1)]
    ensure_header(FILENAME, headers, dialect)

    try:
        existing = read_existing_ids(FILENAME, TARGET_COLUMN_INDEX, dialect)
    except IndexError as e:
        print(f"ERROR: {e}")
        return

    try:
        new_ids = generate_unique_ids(ID_PREFIX, existing, NUM_IDS_TO_ADD,
                                      ID_RANGE_START, ID_RANGE_END)
    except ValueError as e:
        print(f"ERROR: {e}")
        return

    try:
        append_ids(FILENAME, new_ids, TARGET_COLUMN_INDEX, dialect)
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == '__main__':
    main()
