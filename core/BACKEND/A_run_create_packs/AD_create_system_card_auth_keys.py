#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import base64
import csv
from dotenv import load_dotenv

# === SETTINGS ===
load_dotenv()  # Load environment variables from .env
file_path = os.getenv('SYSTEM_CARD_AUTH_SCV')
if not file_path:
    raise ValueError("Environment variable SYSTEM_CARD_AUTH_SCV not found in .env")

# Specify into which columns to write KEY_IN and KEY_OUT (0-based)
KEY_IN_INDEX = 0    # example: write KEY_IN into 3rd column
KEY_OUT_INDEX = 1   # example: write KEY_OUT into 6th column

num_pairs_to_add = 5  # number of key pairs to add at once
key_size = 32         # size of each random key in bytes

# Calculate total number of columns for each row
num_cols = max(KEY_IN_INDEX, KEY_OUT_INDEX) + 1

# Ensure output directory exists
output_dir = os.path.dirname(file_path)
os.makedirs(output_dir, exist_ok=True)

# Append new key pairs
with open(file_path, mode='a', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    for _ in range(num_pairs_to_add):
        # generate URL-safe base64 encoded random keys
        key_in = base64.urlsafe_b64encode(os.urandom(key_size)).decode('utf-8')
        key_out = base64.urlsafe_b64encode(os.urandom(key_size)).decode('utf-8')
        # prepare row with empty strings for all columns
        row = [''] * num_cols
        row[KEY_IN_INDEX] = key_in
        row[KEY_OUT_INDEX] = key_out
        writer.writerow(row)
