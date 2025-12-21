#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
from urllib.parse import urlparse
from dotenv import load_dotenv

# === SETTINGS ===
ENV_FILE = '.env'
ENV_GOOGLE_CALLBACK_URL = 'GOOGLE_CALLBACK_URL'
ENV_SYSTEM_CARD_CSV = 'SYSTEM_FULL_DB_CSV'
URL_COLUMN_INDEX = 12          # index of the column containing the URLs (0-based)
PREFIX_SEGMENT = 'card'       # the path segment to enforce in the URL prefix

# === LOAD ENVIRONMENT VARIABLES ===
load_dotenv(ENV_FILE)

# === RETRIEVE SETTINGS ===
import sys
from urllib.parse import urlparse
# Adjust path to import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from core.database import query_db, update_card

# === SETTINGS ===
ENV_GOOGLE_CALLBACK_URL = 'GOOGLE_CALLBACK_URL'
PREFIX_SEGMENT = 'card'

def update_urls(new_prefix):
    rows = query_db("SELECT card_id, card_url FROM cards")
    count = 0
    
    for row in rows:
        cid = row['card_id']
        current_val = row['card_url']
        
        if not current_val:
            continue
            
        # Determine suffix
        # If it starts with http, parse it
        if current_val.startswith('http://') or current_val.startswith('https://'):
            # It's a full URL, we want to maybe change prefix?
            # Or assume the last part is the key.
            # But wait, AM generates just a key `base64...`.
            # So if it comes from AM, it looks like `XyZ...`.
            # If it comes from old CSV, it might be `http://domain/card/XyZ...`.
            
            # Let's extract the key segment.
            # Assuming format .../card/<key> or just <key>
            
            # We can just check if it starts with new_prefix.
            if current_val.startswith(new_prefix):
                continue
                
            # If it has a different prefix, replace it?
            # Or if it's just raw key?
            
            # Safe bet: assume last segment is key if it looks like URL
            parsed = urlparse(current_val)
            path_parts = parsed.path.strip('/').split('/')
            key = path_parts[-1] if path_parts else current_val
        else:
            # Assume it is just the key
            key = current_val
            
        new_url = f"{new_prefix}{key}"
        
        if new_url != current_val:
            update_card(cid, 'card_url', new_url)
            count += 1

    print(f"Updated {count} card URLs.")

def main():
    callback_url = os.getenv(ENV_GOOGLE_CALLBACK_URL)
    if not callback_url:
        callback_url = "https://nakama.weforks.org"
        print(f"WARNING: using default: {callback_url}")
        
    parsed_callback = urlparse(callback_url)
    new_prefix = f"{parsed_callback.scheme}://{parsed_callback.netloc}/{PREFIX_SEGMENT}/"
    
    update_urls(new_prefix)

if __name__ == "__main__":
    main()


