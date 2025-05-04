#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
from urllib.parse import urlparse
from dotenv import load_dotenv

# === SETTINGS ===
ENV_FILE = '.env'
ENV_GOOGLE_CALLBACK_URL = 'GOOGLE_CALLBACK_URL'
ENV_SYSTEM_CARD_CSV = 'SYSTEM_CARD_AUTH_SCV'
URL_COLUMN_INDEX = 0          # index of the column containing the URLs (0-based)
PREFIX_SEGMENT = 'card'       # the path segment to enforce in the URL prefix

# === LOAD ENVIRONMENT VARIABLES ===
load_dotenv(ENV_FILE)

# === RETRIEVE SETTINGS ===
callback_url = os.getenv(ENV_GOOGLE_CALLBACK_URL)
if not callback_url:
    raise ValueError(f"{ENV_GOOGLE_CALLBACK_URL} not found in {ENV_FILE}")

csv_file_path = os.getenv(ENV_SYSTEM_CARD_CSV)
if not csv_file_path:
    raise ValueError(f"{ENV_SYSTEM_CARD_CSV} not found in {ENV_FILE}")

# === PARSE NEW PREFIX ===
parsed_callback = urlparse(callback_url)
new_prefix = f"{parsed_callback.scheme}://{parsed_callback.netloc}/{PREFIX_SEGMENT}/"

# === READ CSV DATA ===
with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
    reader = list(csv.reader(csvfile))
    header = reader[0]
    rows = reader[1:]  # skip header

# === DETECT EXISTING PREFIX ===
existing_prefix = ''
for row in rows:
    if len(row) > URL_COLUMN_INDEX:
        val = row[URL_COLUMN_INDEX]
        if val.startswith('http://') or val.startswith('https://'):
            parsed = urlparse(val)
            path_parts = parsed.path.strip('/').split('/')
            if path_parts and path_parts[0] == PREFIX_SEGMENT:
                existing_prefix = f"{parsed.scheme}://{parsed.netloc}/{PREFIX_SEGMENT}/"
            else:
                existing_prefix = f"{parsed.scheme}://{parsed.netloc}/"
            break  # stop after finding first valid URL

# === PROCESS ROWS AND APPLY NEW PREFIX ===
for row in rows:
    if len(row) > URL_COLUMN_INDEX:
        value = row[URL_COLUMN_INDEX]
        # Remove existing prefix if present
        if existing_prefix and value.startswith(existing_prefix):
            value = value[len(existing_prefix):]
        # Apply new prefix
        row[URL_COLUMN_INDEX] = new_prefix + value

# === WRITE BACK CSV ===
with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(header)
    writer.writerows(rows)
