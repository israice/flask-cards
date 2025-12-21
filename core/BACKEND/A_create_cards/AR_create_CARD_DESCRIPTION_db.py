import os
import csv
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
SOURCE_FILE = os.path.join("core", "data", "not_used", "CARD_DESCRIPTION.csv")
TARGET_FILE = os.path.join("core", "data", "system_full_db.csv")
TARGET_COLUMN_INDEX = 6  # 1-based index (6th column)

def read_source_data(file_path):
    """Read data from source CSV."""
    if not os.path.exists(file_path):
        print(f"Source file {file_path} not found.")
        return []
    
    data = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        # Skip header
        next(reader, None)
        for row in reader:
            if row:
                data.append(row[0]) # Assume first column
    return data

def insert_into_target(data, file_path, col_index):
    """Insert data into target CSV file at specified column index."""
    if not os.path.exists(file_path):
        print(f"Target file {file_path} not found.")
        return

    # Read existing data
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        rows = [row for row in reader]
    
    # Insert data
    # We should skip header row for insertion target? usually row 0 is header.
    # Existing scripts like AG insert into *rows where col is empty*.
    # Let's assume we fill from row 1 onwards.
    
    current_data_idx = 0
    start_row_idx = 1 # Skip header
    
    # Calculate how many rows need filling
    # But wait, we should only fill if the row exists? Or extend?
    # AG extends rows.
    
    for i in range(start_row_idx, len(rows)):
        row = rows[i]
        
        # Check if we have data to insert
        if current_data_idx >= len(data):
            # No more data to insert, maybe fill with empty or stop?
            # Let's cycle or stop? Typically we might cycle or just leave empty.
            # AG generates data. Here we have a limited list.
            # Let's verify requirement. "some users from list".
            # The user request for CARD_DESCRIPTION implies we should use the descriptions provided.
            # If we run out, maybe cycle? 
            # Description seems unique?
            # For now, let's Cycle if we run out, to ensure all cards have description.
            val = data[current_data_idx % len(data)]
            # Increment only if we didn't cycle? Or always increment. 
            # If cycle, we just use logical index.
        else:
            val = data[current_data_idx]
            
        current_data_idx += 1

        # Ensure row is long enough
        if len(row) < col_index:
            row.extend([''] * (col_index - len(row)))
            
        # Insert/Overwrite
        row[col_index-1] = val

    # Write back
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)

def main():
    descriptions = read_source_data(SOURCE_FILE)
    if not descriptions:
        print("No descriptions found.")
        return

    insert_into_target(descriptions, TARGET_FILE, TARGET_COLUMN_INDEX)

if __name__ == "__main__":
    main()
