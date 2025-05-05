import os
import csv
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration: target column index (1-based)
COLUMN_INDEX = 10  # e.g. 6 means the sixth column

# Read number of entries to pick strictly from environment variable
# Raise error if missing or not an integer
try:
    NUMBER_OF_CARDS = int(os.environ["NUMBER_OF_CARDS"])
except KeyError:
    raise RuntimeError("Environment variable NUMBER_OF_CARDS is required")
except ValueError:
    raise RuntimeError("Environment variable NUMBER_OF_CARDS must be an integer")


THEMES = [
    "Games",
    "Design",
    "Tech innovations",
    "Film",
    "Music",
    "Publishing",
    "Art",
    "Charity",
    "Tourism"  
]

def select_one_blockchain():
    """
    Select a single blockchain randomly from THEMES.
    """
    return random.choice(THEMES)

def insert_into_first_empty_cells(names, file_path):
    """
    Read all rows, find first empty cells in target column, and insert names there.
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
    
    # Insert each name into the next empty cell
    for name in names:
        idx = existing  # 0-based row index where to insert
        if idx < len(rows):
            row = rows[idx]
            # ensure row has enough columns
            if len(row) < COLUMN_INDEX:
                row.extend([''] * (COLUMN_INDEX - len(row)))
            row[COLUMN_INDEX-1] = name
        else:
            # create a new row with empty cols up to target, then name
            new_row = [''] * (COLUMN_INDEX - 1) + [name]
            rows.append(new_row)
        existing += 1

    # Write back updated data
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)

def main():
    # Path to the CSV file
    file_path = os.path.join("core", "data", "system_full_db.csv")
    
    # Select one random blockchain
    chosen = select_one_blockchain()
    # Prepare list with the same blockchain repeated NUMBER_OF_CARDS times
    THEMES = [chosen] * NUMBER_OF_CARDS
    
    # Insert into first free cells in the target column
    insert_into_first_empty_cells(THEMES, file_path)

if __name__ == "__main__":
    main()
