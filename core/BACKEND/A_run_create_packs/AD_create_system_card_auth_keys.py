#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import base64
import csv
from dotenv import load_dotenv

# === SETTINGS ===
load_dotenv()  # Load variables from .env
file_path = os.getenv('SYSTEM_CARD_AUTH_SCV')
if not file_path:
    raise ValueError("Environment variable SYSTEM_CARD_AUTH_SCV not found in .env")

output_dir = os.path.dirname(file_path)
num_pairs_to_add = 5         # number of key pairs to add at once
key_size = 32                # size of each random key in bytes
KEY_IN_INDEX = 0             # Column index for KEY_IN (0-based)
KEY_OUT_INDEX = 1            # Column index for KEY_OUT (0-based)

# === PREPARE OUTPUT DIRECTORY ===
os.makedirs(output_dir, exist_ok=True)

# === CHECK IF FILE EXISTS AND READ HEADER ===
file_exists = os.path.isfile(file_path)
header = []
if file_exists:
    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        try:
            header = next(reader)
        except StopIteration:
            header = []

# Determine number of columns
if header:
    num_cols = len(header)
else:
    num_cols = max(KEY_IN_INDEX, KEY_OUT_INDEX) + 1
    # build header row if file is new
    header = [''] * num_cols
    header[KEY_IN_INDEX] = 'KEY_IN'
    header[KEY_OUT_INDEX] = 'KEY_OUT'

# === APPEND NEW KEYS ===
with open(file_path, mode='a', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    # Write header if file is new or empty
    if not file_exists or os.path.getsize(file_path) == 0:
        writer.writerow(header)

    for _ in range(num_pairs_to_add):
        key_in = base64.urlsafe_b64encode(os.urandom(key_size)).decode('utf-8')
        key_out = base64.urlsafe_b64encode(os.urandom(key_size)).decode('utf-8')
        # prepare empty row
        row = [''] * num_cols
        row[KEY_IN_INDEX] = key_in
        row[KEY_OUT_INDEX] = key_out
        writer.writerow(row)
