import os
import csv
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration: target column index (1-based)
COLUMN_INDEX = 9  # e.g. 6 means the sixth column

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

import sys
# Adjust path to import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from core.database import query_db, update_card

def update_empty_cells(names):
    """
    Find cards with empty names and update them.
    """
    # Find cards with empty name
    rows = query_db("SELECT card_id FROM cards WHERE name IS NULL OR name = ''")
    
    # We only have as many names as generated
    # If we have more empty slots than names, we fill what we can.
    # If we have more names than slots, we stop when full.
    
    count = 0
    for i, name in enumerate(names):
        if i >= len(rows):
            break
        card_id = rows[i]['card_id']
        update_card(card_id, 'name', name)
        count += 1
    
    print(f"Updated {count} cards with new names.")

def main():
    # Generate legendary names based on env var
    # Ensure env var is loaded? original script did load_dotenv
    # But current_app might not be available if run standalone.
    # We should keep load_dotenv if needed, but core.database handles DB path.
    
    legendary_names = generate_legendary_names(NUMBER_OF_CARDS)
    
    update_empty_cells(legendary_names)

if __name__ == "__main__":
    main()
