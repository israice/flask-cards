import os
import csv
from dotenv import load_dotenv

load_dotenv()

SOURCE_FILE = os.path.join("core", "data", "not_used", "GAME_STATS.csv")
TARGET_FILE = os.path.join("core", "data", "system_full_db.csv")
TARGET_COLUMN_INDEX = 17  # 1-based (17th column) -> Index 16 (0-based) for POWER_COMBAT

def read_source_data(file_path):
    if not os.path.exists(file_path):
        print(f"Source file {file_path} not found.")
        return []
    
    data = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if 'POWER_COMBAT' in row and row['POWER_COMBAT'].strip():
                data.append(row['POWER_COMBAT'])
    return data

def insert_into_target(data, file_path, col_index):
    if not os.path.exists(file_path):
        return

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        rows = [row for row in reader]
    
    start_row_idx = 1
    current_data_idx = 0
    
    for i in range(start_row_idx, len(rows)):
        row = rows[i]
        
        if not data:
            val = ""
        else:
            val = data[current_data_idx % len(data)]
            current_data_idx += 1
            
        if len(row) < col_index:
            row.extend([''] * (col_index - len(row)))
            
        row[col_index-1] = val

    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)

def main():
    db_data = read_source_data(SOURCE_FILE)
    insert_into_target(db_data, TARGET_FILE, TARGET_COLUMN_INDEX)

if __name__ == "__main__":
    main()
