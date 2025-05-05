import os
import csv
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration: target column index (1-based)
COLUMN_INDEX = 8  # e.g. 6 means the sixth column

# Read number of cards to generate from environment variable
# Default to 5 if not set or invalid
NUMBER_OF_CARDS = int(os.getenv("NUMBER_OF_CARDS"))

# Expanded list of crypto-themed epic adjectives
ADJECTIVES = [
    "Genesis", "Quantum", "Decentralized", "Atomic", "Hyper",
    "Satoshi's", "Bullish", "Bearish", "Digital", "Immutable",
    "Tokenized", "Algorithmic", "Lightning", "Infinite", "Smart",
    "Permissionless", "Cryptic", "Yield", "Staked", "Wrapped",
    "Governed", "Onchain", "Layered", "Cold", "Hashpower",
    "Peer", "Liquid", "Frozen", "Oracle-linked", "Meta"
]

# Expanded list of crypto-themed powerful nouns
NOUNS = [
    "Block", "Chain", "Node", "Vault", "Oracle",
    "Fork", "Whale", "Moon", "Lambo", "Satoshi",
    "Hashrate", "Token", "DApp", "Trezor", "Ledger",
    "Miner", "Shark", "HODL", "FOMO", "FUD",
    "DEX", "CEX", "Bridge", "Protocol", "GenesisBlock",
    "Gas", "Liquidity", "Staker", "Explorer", "Governance"
]

# Templates tuned for crypto-legends
TEMPLATES = [
    "{adj} {noun}",
    "The {adj} {noun}",
    "{noun} of the {adj} {noun2}",
    "{adj} {noun} of {noun2}",
    "{noun} Protocol of {adj}",
    "Genesis {noun}",
    "The {noun} on {adj} Chain",
    "{adj} {noun} Network",
    "Shroud of the {adj} {noun}",
    "Heart of {noun}",
    "Soul of the {adj} {noun2}",
    "Eye of {adj} {noun}",
    "{adj} {noun} Bridge",
    "{noun} of Eternal {noun2}",
    "{adj} {noun} at Dawn",
    "Twilight {noun} of {adj}",
    "{adj} {noun} Governance",
    "{adj} {noun} Yield",
    "{noun} and {noun2} United",
    "{adj} {noun} Union"
]

def generate_legendary_names(count):
    """
    Generate a list of 'count' legendary crypto-themed names using random templates.
    """
    names = []
    for _ in range(count):
        template = random.choice(TEMPLATES)
        name = template.format(
            adj=random.choice(ADJECTIVES),
            noun=random.choice(NOUNS),
            noun2=random.choice(NOUNS)
        )
        names.append(name)
    return names

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
    
    # Generate legendary names based on env var
    legendary_names = generate_legendary_names(NUMBER_OF_CARDS)
    
    # Insert into first free cells in the target column
    insert_into_first_empty_cells(legendary_names, file_path)

if __name__ == "__main__":
    main()
