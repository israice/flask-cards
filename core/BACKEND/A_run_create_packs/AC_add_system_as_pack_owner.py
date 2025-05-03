#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
from dotenv import load_dotenv

# ==== LOAD ENVIRONMENT VARIABLES ====
load_dotenv()
input_path = os.getenv('SYSTEM_CARDS_CSV')

if not input_path:
    print("ERROR: SYSTEM_CARDS_CSV is not set in the .env file.")
    exit(1)

# Ensure data directory exists
os.makedirs(os.path.dirname(input_path), exist_ok=True)

# Read rows from the original file, updating empty OWNER fields
rows = []
with open(input_path, 'r', newline='', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames  # e.g. ['PACK_ID','CARD_ID','OWNER']
    for row in reader:
        # If OWNER is missing or only whitespace, set to 'SYSTEM'
        if row.get('OWNER') is None or row['OWNER'].strip() == '':
            row['OWNER'] = 'SYSTEM'
        rows.append(row)

# Write updated data back to the same file
with open(input_path, 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
