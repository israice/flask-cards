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

# Hardcoded list of 10 most popular blockchains
BLOCKCHAINS = [
    "Ethereum",
    "Binance Smart Chain",
    "Cardano",
    "Solana",
    "XRP Ledger",
    "Polkadot",
    "Avalanche",
    "Tron",
    "Polygon"
]

def select_one_blockchain():
    """
    Select a single blockchain randomly from BLOCKCHAINS.
    """
    return random.choice(BLOCKCHAINS)

import sys
# Adjust path to import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from core.database import query_db, update_card

def update_chain(chain_name, count_needed):
    """
    Update empty chain with selected chain_name.
    """
    rows = query_db("SELECT card_id FROM cards WHERE chain IS NULL OR chain = ''")
    
    count = 0
    for i, row in enumerate(rows):
        if count >= count_needed:
            break
        
        update_card(row['card_id'], 'chain', chain_name)
        count += 1
    
    print(f"Updated {count} cards with chain {chain_name}.")

def main():
    # Select one random blockchain
    chosen = select_one_blockchain()
    update_chain(chosen, NUMBER_OF_CARDS)

if __name__ == "__main__":
    main()
