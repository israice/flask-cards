import os
import csv
from dotenv import load_dotenv

load_dotenv()

SOURCE_FILE = os.path.join("core", "data", "not_used", "GAME_STATS.csv")
TARGET_FILE = os.path.join("core", "data", "system_full_db.csv")
TARGET_COLUMN_INDEX = 16  # 1-based (16th column) -> Index 15 (0-based) for MONSTER_POWER

def read_source_data(file_path):
    if not os.path.exists(file_path):
        print(f"Source file {file_path} not found.")
        return []
    
    data = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile) # Use DictReader as header exists
        for row in reader:
            if 'MONSTER_POWER' in row and row['MONSTER_POWER'].strip():
                data.append(row['MONSTER_POWER'])
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
    powers = read_source_data(SOURCE_FILE)
    insert_into_target(powers, TARGET_FILE, TARGET_COLUMN_INDEX)

if __name__ == "__main__":
    main()
