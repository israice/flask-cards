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

# Get CSV file path from environment variable
file_path = os.getenv("SYSTEM_FULL_DB_CSV")
if not file_path:
    raise ValueError("Environment variable SYSTEM_FULL_DB_CSV not found in .env")

# Define target column indexes (0-based)
CARD_URL_INDEX = 11     # CARD_URL column
CARD_KEYS_INDEX = 12    # CARD_KEYS column

# Define size of each key in bytes
KEY_SIZE = 32

# Read the CSV file into memory
with open(file_path, mode="r", newline="", encoding="utf-8") as f:
    rows = list(csv.reader(f))

if len(rows) < 2:
    raise ValueError("CSV must contain a header row and at least one data row")

header = rows[0]
data_rows = rows[1:]

# Process each data row
for row in data_rows:
    # Ensure the row has enough columns for CARD_URL and CARD_KEYS
    missing_columns = (CARD_KEYS_INDEX + 1) - len(row)
    if missing_columns > 0:
        row.extend([''] * missing_columns)

    # Fill CARD_URL if it is empty
    if not row[CARD_URL_INDEX].strip():
        generated_url_key = base64.urlsafe_b64encode(os.urandom(KEY_SIZE)).decode("utf-8")
        row[CARD_URL_INDEX] = generated_url_key

    # Fill CARD_KEYS if it is empty
    if not row[CARD_KEYS_INDEX].strip():
        generated_keys_key = base64.urlsafe_b64encode(os.urandom(KEY_SIZE)).decode("utf-8")
        row[CARD_KEYS_INDEX] = generated_keys_key

# Write all rows back to the CSV, preserving existing data
with open(file_path, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(header)
    writer.writerows(data_rows)

