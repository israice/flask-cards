#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import csv
from dotenv import load_dotenv

# === SETTINGS ===
load_dotenv()  # Load environment variables from .env
DB_FILENAME        = os.getenv('SYSTEM_DB_CSV')      # Source CSV from .env
CARDS_FILENAME     = os.getenv('SYSTEM_CARDS_CSV')   # Target CSV from .env
READ_COL_INDEX     = 0   # Column index to read and remove from DB file (0-based)
WRITE_COL_INDEX    = 2   # Column index to write into target cards file (0-based)
FILL_COUNT         = 5   # How many rows to fill in target
ENCODING           = 'utf-8'

# === VALIDATE ENVIRONMENT ===
if not DB_FILENAME:
    print(f"Error: environment variable SYSTEM_DB_CSV is not set.", file=sys.stderr)
    sys.exit(1)
if not CARDS_FILENAME:
    print(f"Error: environment variable SYSTEM_CARDS_CSV is not set.", file=sys.stderr)
    sys.exit(1)


def cut_first_db_value(filename, col_index):
    """
    Read and remove the first data-row value from column at col_index in a CSV.
    Returns the stripped value, or None if missing/empty.
    Writes the file back without that data row, preserving header.
    """
    if not os.path.exists(filename):
        print(f"Error: DB file '{filename}' not found.", file=sys.stderr)
        return None

    # Read all rows
    with open(filename, newline='', encoding=ENCODING) as f:
        reader = csv.reader(f)
        all_rows = list(reader)

    if len(all_rows) < 2:
        print(f"Error: No data rows in '{filename}'.", file=sys.stderr)
        return None

    header = all_rows[0]
    data_rows = all_rows[1:]

    # Validate col_index
    if col_index < 0 or col_index >= len(header):
        print(f"Error: READ_COL_INDEX {col_index} out of range.", file=sys.stderr)
        return None

    # Pop first data row and extract value
    first_row = data_rows.pop(0)
    # Pad row if too short
    if len(first_row) < len(header):
        first_row += [''] * (len(header) - len(first_row))
    raw = first_row[col_index]
    if not raw or not raw.strip():
        print(f"Error: Column at index {col_index} missing or empty in first data row of DB.", file=sys.stderr)
        return None
    value = raw.strip()

    # Write back without the popped row
    with open(filename, 'w', newline='', encoding=ENCODING) as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data_rows)

    return value


def fill_column_with_value(filename, value, col_index, count):
    """
    Replace up to `count` occurrences of "SYSTEM" in column at col_index of the target CSV with `value`.
    Report empty cells and warnings.
    """
    if not os.path.exists(filename):
        print(f"Error: Cards file '{filename}' not found.", file=sys.stderr)
        return

    with open(filename, newline='', encoding=ENCODING) as f:
        reader = csv.reader(f)
        all_rows = list(reader)

    if not all_rows:
        print(f"Error: '{filename}' is empty.", file=sys.stderr)
        return

    header = all_rows[0]
    rows = all_rows[1:]
    num_cols = max(len(header), col_index + 1)

    # Ensure header length covers col_index
    if len(header) < num_cols:
        header += [''] * (num_cols - len(header))

    # Pad data rows
    for i, row in enumerate(rows):
        if len(row) < num_cols:
            rows[i] = row + [''] * (num_cols - len(row))

    # Fill values
    filled = 0
    for row in rows:
        if row[col_index].strip() == 'SYSTEM':
            row[col_index] = value
            filled += 1
            if filled >= count:
                break

    # Write back updated file
    with open(filename, 'w', newline='', encoding=ENCODING) as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    # Report errors
    errors = False
    for idx, row in enumerate(rows, start=2):
        cell = row[col_index].strip()
        if not cell:
            print(f"Error: Empty cell at line {idx} in column index {col_index} of '{filename}'.", file=sys.stderr)
            errors = True
    if filled < count:
        print(f"Warning: Only {filled} of {count} 'SYSTEM' entries were replaced.", file=sys.stderr)
    if errors:
        print("Process completed with errors. Please fill missing values.", file=sys.stderr)


def main():
    # 1) Cut first value from DB file
    val = cut_first_db_value(DB_FILENAME, READ_COL_INDEX)
    if not val:
        sys.exit(1)

    # 2) Fill that value into CARD rows
    fill_column_with_value(CARDS_FILENAME, val, WRITE_COL_INDEX, FILL_COUNT)


if __name__ == '__main__':
    main()
