import os
import csv
from dotenv import load_dotenv

# --- Settings ---
COLUMN_INDEX = 1  # Index of the column to update (changeable)
ENV_FILE = '.env'  # Path to .env file
CSV_ENV_KEY = 'SYSTEM_FULL_DB_CSV'  # Key in .env file for CSV file path
COUNT_ENV_KEY = 'NUMBER_OF_CARDS'  # Key in .env file for number of rows
WORD_TO_INSERT = 'SYSTEM'  # Word to insert

# --- Load environment ---
load_dotenv(ENV_FILE)
csv_path = os.getenv(CSV_ENV_KEY)
num_rows_str = os.getenv(COUNT_ENV_KEY)

if not csv_path:
    raise ValueError(f"Environment variable '{CSV_ENV_KEY}' not found in {ENV_FILE}")
if not num_rows_str or not num_rows_str.isdigit():
    raise ValueError(f"Environment variable '{COUNT_ENV_KEY}' not found or invalid in {ENV_FILE}")

num_rows_to_add = int(num_rows_str)

# --- Read existing rows ---
with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
    reader = list(csv.reader(csvfile))
    existing_rows = reader

# --- Prepare rows to update ---
updated_rows = []
added_count = 0

for row in existing_rows:
    # Ensure row is long enough
    while len(row) <= COLUMN_INDEX:
        row.append('')

    # Logic: if COLUMN_INDEX == 0 → always write if empty; if >0 → check left cell
    should_insert = False
    if COLUMN_INDEX == 0:
        if not row[COLUMN_INDEX].strip():
            should_insert = True
    else:
        if row[COLUMN_INDEX - 1].strip() and not row[COLUMN_INDEX].strip():
            should_insert = True

    if should_insert and added_count < num_rows_to_add:
        row[COLUMN_INDEX] = WORD_TO_INSERT
        added_count += 1

    # Strip trailing empty cells
    while row and row[-1] == '':
        row.pop()

    updated_rows.append(row)

# --- Add new rows if needed ---
while added_count < num_rows_to_add:
    new_row = ['' for _ in range(COLUMN_INDEX + 1)]
    new_row[COLUMN_INDEX] = WORD_TO_INSERT

    # Strip trailing empty cells
    while new_row and new_row[-1] == '':
        new_row.pop()

    updated_rows.append(new_row)
    added_count += 1

# --- Write updated rows back ---
with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(updated_rows)

