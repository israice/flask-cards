import os
from dotenv import load_dotenv
import csv
from urllib.parse import urlparse

# ======================== CONFIGURATION ========================
ENV_FILE = '.env'
ENV_GOOGLE_CALLBACK_URL = 'GOOGLE_CALLBACK_URL'
ENV_SYSTEM_CARD_CSV = 'SYSTEM_CARD_AUTH_SCV'
# ===============================================================

# Load environment variables
load_dotenv(ENV_FILE)

# Get the GOOGLE_CALLBACK_URL value
callback_url = os.getenv(ENV_GOOGLE_CALLBACK_URL)
if not callback_url:
    raise ValueError(f"{ENV_GOOGLE_CALLBACK_URL} not found in {ENV_FILE}")

# Parse URL to extract scheme + netloc (domain + port)
parsed_url = urlparse(callback_url)
new_prefix = f"{parsed_url.scheme}://{parsed_url.netloc}/"

# Get the CSV file path
csv_file_path = os.getenv(ENV_SYSTEM_CARD_CSV)
if not csv_file_path:
    raise ValueError(f"{ENV_SYSTEM_CARD_CSV} not found in {ENV_FILE}")

# Read the CSV data
with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
    reader = list(csv.reader(csvfile))
    header = reader[0]
    rows = reader[1:]  # skip header

# Identify existing prefix (if any) from the first row
existing_prefix = ''
for row in rows:
    if row and (row[0].startswith('http://') or row[0].startswith('https://')):
        parsed = urlparse(row[0])
        existing_prefix = f"{parsed.scheme}://{parsed.netloc}/"
        break  # found an existing prefixed row

# Process all rows' first column
for row in rows:
    if row:
        value = row[0]
        # Remove existing prefix if present
        if existing_prefix and value.startswith(existing_prefix):
            value = value[len(existing_prefix):]
        # Apply new prefix
        row[0] = new_prefix + value

# Write the updated data back to the CSV
with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(header)  # write header
    writer.writerows(rows)   # write data rows

# Note: This script replaces any old prefix with the new one across all rows
