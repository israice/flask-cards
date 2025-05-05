import os
import csv
from datetime import date
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration: target column index (1-based)
COLUMN_INDEX = 3

# Read number of entries to pick strictly from environment variable
# Raise error if missing or not an integer
try:
    NUMBER_OF_CARDS = int(os.environ["NUMBER_OF_CARDS"])
except KeyError:
    raise RuntimeError("Environment variable NUMBER_OF_CARDS is required")
except ValueError:
    raise RuntimeError("Environment variable NUMBER_OF_CARDS must be an integer")

# Read CSV path from environment variable
try:
    FILE_PATH = os.environ["SYSTEM_FULL_DB_CSV"]
except KeyError:
    raise RuntimeError("Environment variable SYSTEM_FULL_DB_CSV is required")

def select_today_date():
    """
    Return today's date in YYYY-MM-DD format.
    """
    return date.today().isoformat()

def insert_into_first_empty_cells(values, file_path):
    """
    Read all rows, find first empty cells in target column, and insert values there.
    """
    # Read existing data
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        rows = [row for row in reader]
    
    # Count how many non-empty entries already in the column
    existing = 0
    for row in rows:
        if len(row) >= COLUMN_INDEX and row[COLUMN_INDEX-1].strip():
            existing += 1
    
    # Insert each value into the next empty cell
    for value in values:
        idx = existing  # 0-based row index where to insert
        if idx < len(rows):
            row = rows[idx]
            # ensure row has enough columns
            if len(row) < COLUMN_INDEX:
                row.extend([''] * (COLUMN_INDEX - len(row)))
            row[COLUMN_INDEX-1] = value
        else:
            # create a new row with empty cols up to target, then value
            new_row = [''] * (COLUMN_INDEX - 1) + [value]
            rows.append(new_row)
        existing += 1

    # Write back updated data
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)

def main():
    # Path to the CSV file from .env
    file_path = FILE_PATH
    
    # Prepare list with today's date for each card
    today = select_today_date()
    values_list = [today for _ in range(NUMBER_OF_CARDS)]
    
    # Insert into first free cells in the target column
    insert_into_first_empty_cells(values_list, file_path)

if __name__ == "__main__":
    main()
