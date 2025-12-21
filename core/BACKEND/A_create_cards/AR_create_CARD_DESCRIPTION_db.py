import os
import csv
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import sys
# Adjust path to import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from core.database import query_db, update_card

# Configuration
SOURCE_FILE = os.path.join("core", "data", "not_used", "CARD_DESCRIPTION.csv")

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

def update_descriptions(descriptions):
    """
    Update empty descriptions with values from source, cycling if needed.
    """
    if not descriptions:
        return

    # Get cards with empty descriptions
    rows = query_db("SELECT card_id FROM cards WHERE description IS NULL OR description = ''")
    
    count = 0
    for i, row in enumerate(rows):
        cid = row['card_id']
        desc = descriptions[i % len(descriptions)]
        
        update_card(cid, 'description', desc)
        count += 1
        
    print(f"Updated {count} cards with descriptions.")

def main():
    descriptions = read_source_data(SOURCE_FILE)
    if not descriptions:
        print("No descriptions found.")
        return

    update_descriptions(descriptions)

if __name__ == "__main__":
    main()
