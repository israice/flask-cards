#!/usr/bin/env python3
import csv
import os

# ==== SETTINGS ====  
DB_FILENAME    = 'data/system_db.csv'         # Source CSV for cutting the value  
CARDS_FILENAME = 'data/system_cards.csv'      # Target CSV to update  
READ_COL_NAME  = 'email'                      # Column name in DB_FILENAME to read & remove  
WRITE_COL_NAME = 'USER_ID'                    # Column name in CARDS_FILENAME to write  
FILL_COUNT     = 5                            # How many rows to fill in target  
# ===================

def cut_first_db_value(filename, col_name):
    """
    Read and remove the first data-row value from column `col_name` in a comma-separated CSV.
    Returns the stripped value, or None if missing/empty.
    Writes the file back without that row, preserving header order.
    """
    if not os.path.exists(filename):
        return None

    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',', quotechar='"')
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    if not rows:
        return None  # no data rows

    first = rows.pop(0)
    raw = first.get(col_name)
    if raw is None:
        # Column missing or no value
        return None
    value = raw.strip()
    if not value:
        return None

    # Write back DB without the first data row
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)

    return value


def fill_column_with_value(filename, value, col_name, count):
    """
    Fill `value` into column `col_name` of the first `count` empty cells
    in the target CSV, using comma as delimiter and proper quoting.
    """
    if not os.path.exists(filename):
        return

    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',', quotechar='"')
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    # If target column not in header, add it at the end
    if col_name not in fieldnames:
        fieldnames.append(col_name)
        # Ensure all rows have the new key
        for row in rows:
            row[col_name] = ''

    filled = 0
    for row in rows:
        raw_cell = row.get(col_name)
        cell = raw_cell.strip() if isinstance(raw_cell, str) else ''
        # Only fill if cell empty
        if not cell:
            row[col_name] = value
            filled += 1
            if filled >= count:
                break

    # Write back the updated target file
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)


def main():
    # 1) Cut the first email from system_db.csv
    email = cut_first_db_value(DB_FILENAME, READ_COL_NAME)
    if not email:
        return  # nothing to process

    # 2) Fill user_id into the first FILL_COUNT empty rows of system_cards.csv
    fill_column_with_value(CARDS_FILENAME, email, WRITE_COL_NAME, FILL_COUNT)

if __name__ == '__main__':
    main()