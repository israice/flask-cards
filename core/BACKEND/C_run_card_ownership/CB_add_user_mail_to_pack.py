#!/usr/bin/env python3
import csv
import os
import sys

# ==== SETTINGS ====  
DB_FILENAME    = 'data/system_db.csv'         # Source CSV for cutting the value  
CARDS_FILENAME = 'data/system_cards.csv'      # Target CSV to update  
READ_COL_NAME  = 'email'                      # Column name in DB_FILENAME to read & remove  
WRITE_COL_NAME = 'OWNER'                      # Column name in CARDS_FILENAME to write  
FILL_COUNT     = 5                            # How many rows to fill in target  
# ===================

def cut_first_db_value(filename, col_name):
    """
    Read and remove the first data-row value from column `col_name` in a comma-separated CSV.
    Returns the stripped value, or None if missing/empty.
    Writes the file back without that row, preserving header order.
    """
    if not os.path.exists(filename):
        print(f"Error: DB file '{filename}' not found.", file=sys.stderr)
        return None

    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',', quotechar='"')
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    if not rows:
        return None

    first = rows.pop(0)
    raw = first.get(col_name)
    if raw is None or not raw.strip():
        print(f"Error: Column '{col_name}' missing or empty in first row of DB.", file=sys.stderr)
        return None
    value = raw.strip()

    # Write back DB without the first data row
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)

    return value


def fill_column_with_value(filename, value, col_name, count):
    """
    Replace up to `count` occurrences of "SYSTEM" in column `col_name` of the target CSV with `value`.
    After filling, report any empty cells in that column as errors.
    """
    if not os.path.exists(filename):
        print(f"Error: Cards file '{filename}' not found.", file=sys.stderr)
        return

    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',', quotechar='"')
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    # If target column not in header, add it at the end and initialize
    if col_name not in fieldnames:
        fieldnames.append(col_name)
        for row in rows:
            row[col_name] = ''

    filled = 0
    # Fill only cells that equal "SYSTEM"
    for row in rows:
        cell = row.get(col_name, '')
        if isinstance(cell, str) and cell.strip() == "SYSTEM":
            row[col_name] = value
            filled += 1
            if filled >= count:
                break

    # Write back updated target file
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)

    # After writing, scan for any empty OWNER cells
    errors_found = False
    for idx, row in enumerate(rows, start=2):  # start=2 to account for header line
        cell = row.get(col_name, '')
        if not isinstance(cell, str) or not cell.strip():
            print(f"Error: Empty '{col_name}' at line {idx} in '{filename}'.", file=sys.stderr)
            errors_found = True

    if filled < count:
        print(f"Warning: Only {filled} of {count} 'SYSTEM' entries were replaced (found fewer in file).", file=sys.stderr)

    if errors_found:
        print("Process completed with errors. Please fill missing OWNER values.", file=sys.stderr)


def main():
    # 1) Cut the first email from system_db.csv
    email = cut_first_db_value(DB_FILENAME, READ_COL_NAME)
    if not email:
        sys.exit(1)

    # 2) Fill OWNER into up to FILL_COUNT "SYSTEM" rows of system_cards.csv
    fill_column_with_value(CARDS_FILENAME, email, WRITE_COL_NAME, FILL_COUNT)


if __name__ == '__main__':
    main()
