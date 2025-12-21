#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import base64
import csv
from dotenv import load_dotenv, find_dotenv

# Load .env file
dotenv_path = find_dotenv()
if not dotenv_path:
    raise FileNotFoundError(".env file not found")
load_dotenv(dotenv_path)

import sys
import base64
# Adjust path to import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from core.database import query_db, update_card

# Define size of each key in bytes
KEY_SIZE = 32

def update_keys():
    """
    Check for cards with empty card_url or card_keys and fill them.
    In this DB schema, card_url is just the random key part perhaps? 
    The original script generated: `generated_url_key`.
    AN script adds prefix later.
    """
    rows = query_db("SELECT card_id, card_url, card_keys FROM cards")
    
    count_url = 0
    count_keys = 0
    
    for row in rows:
        cid = row['card_id']
        url = row['card_url']
        keys = row['card_keys']
        
        updated = False
        
        if not url or not url.strip():
            new_url_key = base64.urlsafe_b64encode(os.urandom(KEY_SIZE)).decode("utf-8")
            update_card(cid, 'card_url', new_url_key)
            count_url += 1
            
        if not keys or not keys.strip():
            new_keys_key = base64.urlsafe_b64encode(os.urandom(KEY_SIZE)).decode("utf-8")
            update_card(cid, 'card_keys', new_keys_key)
            count_keys += 1

    print(f"Updated {count_url} cards with url, {count_keys} cards with keys.")

def main():
    update_keys()

if __name__ == "__main__":
    main()

