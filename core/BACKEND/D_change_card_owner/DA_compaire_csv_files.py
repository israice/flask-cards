#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import csv
from dotenv import load_dotenv

# === SETTINGS ===
load_dotenv()  # Load variables from .env
MAILS_FILE          = os.getenv('AUTH_USERS')       # Path to auth_users.csv
COLLECTION_FILE      = os.getenv('SYSTEM_DB_CSV')    # Path to system_db.csv
MAILS_EMAIL_COL_INDEX = 0   # Column index for email in auth_users.csv (0-based)
COLL_EMAIL_COL_INDEX  = 0   # Column index for email in system_db.csv (0-based)
ENCODING             = 'utf-8'  # File encoding

# === VALIDATE ENVIRONMENT ===
if not MAILS_FILE:
    print('Error: environment variable AUTH_USERS is not set.', file=sys.stderr)
    sys.exit(1)
if not COLLECTION_FILE:
    print('Error: environment variable SYSTEM_DB_CSV is not set.', file=sys.stderr)
    sys.exit(1)

# === READ emails from auth_users.csv ===
with open(MAILS_FILE, newline='', encoding=ENCODING) as f:
    reader = csv.reader(f)
    rows = list(reader)
# Skip header row if present
data_rows = rows[1:] if len(rows) > 1 else []
# Collect emails by index
mails_emails = {
    row[MAILS_EMAIL_COL_INDEX].strip()
    for row in data_rows
    if len(row) > MAILS_EMAIL_COL_INDEX and row[MAILS_EMAIL_COL_INDEX].strip()
}

# === READ existing emails from system_db.csv ===
collection_emails = set()
num_cols = COLL_EMAIL_COL_INDEX + 1  # default number of columns
if os.path.isfile(COLLECTION_FILE):
    with open(COLLECTION_FILE, newline='', encoding=ENCODING) as f:
        reader = csv.reader(f)
        all_rows = list(reader)
        if all_rows:
            # determine columns from first row
            num_cols = len(all_rows[0])
            # data rows skip header
            coll_data = all_rows[1:]
            collection_emails = {
                row[COLL_EMAIL_COL_INDEX].strip()
                for row in coll_data
                if len(row) > COLL_EMAIL_COL_INDEX and row[COLL_EMAIL_COL_INDEX].strip()
            }

# === Determine emails to add ===
emails_to_add = mails_emails - collection_emails

# === Append new emails if any ===
if emails_to_add:
    with open(COLLECTION_FILE, 'a', newline='', encoding=ENCODING) as f:
        writer = csv.writer(f)
        for email in emails_to_add:
            # prepare row with appropriate length
            row = [''] * num_cols
            row[COLL_EMAIL_COL_INDEX] = email
            writer.writerow(row)

print("- - move user email to main database")