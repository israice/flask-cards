# ================= SETTINGS =================
mails_file = 'data/auth_users.csv'  # Path to auth_users.csv
collection_file = 'data/system_db.csv'  # Path to system_db.csv
email_field_name = 'email'  # Name of the email column
encoding = 'utf-8'  # File encoding
# ============================================

import csv

# Read emails from auth_users.csv
with open(mails_file, newline='', encoding=encoding) as f:
    reader = csv.DictReader(f)
    mails_emails = {row[email_field_name] for row in reader}

# Read emails from system_db.csv
with open(collection_file, newline='', encoding=encoding) as f:
    reader = csv.DictReader(f)
    collection_rows = list(reader)
    collection_emails = {row[email_field_name] for row in collection_rows}

# Find emails to add
emails_to_add = mails_emails - collection_emails

# If there are emails to add, append them
if emails_to_add:
    # Get fieldnames (headers) from the existing collection file
    fieldnames = collection_rows[0].keys() if collection_rows else [email_field_name]

    with open(collection_file, 'a', newline='', encoding=encoding) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        # Check if file was empty: if yes, write header
        if not collection_rows:
            writer.writeheader()
        for email in emails_to_add:
            # Write row with email; fill other fields with empty string
            row = {field: '' for field in fieldnames}
            row[email_field_name] = email
            writer.writerow(row)
