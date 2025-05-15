import os
import csv
from dotenv import load_dotenv

def main():
    # Load environment variables from .env file
    load_dotenv()
    SYSTEM_CSV = os.getenv('SYSTEM_FULL_DB_CSV')  # path to full DB CSV
    AUTH_CSV = os.getenv('AUTH_USERS')            # path to auth users CSV

    # Ensure required environment variables are set
    if not SYSTEM_CSV or not AUTH_CSV:
        raise RuntimeError("Missing SYSTEM_FULL_DB_CSV or AUTH_USERS in environment")

    # Read master CSV (system records)
    with open(SYSTEM_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        system_records = list(reader)
        system_fieldnames = reader.fieldnames

    # Read auth users CSV
    with open(AUTH_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        auth_rows = list(reader)
        auth_fieldnames = reader.fieldnames

    processed_urls = set()

    # Update master records based on auth users entries
    for row in auth_rows:
        card_url = row.get('AUTH_URLS')
        owner_email = row.get('AUTH_MAILS')
        if not card_url or not owner_email:
            continue  # skip incomplete rows

        for rec in system_records:
            if rec.get('CARD_URL') == card_url:
                # Set the CARD_OWNER field to the new owner email
                rec['CARD_OWNER'] = owner_email
                processed_urls.add(card_url)
                break

    # Write updated master CSV back to disk
    with open(SYSTEM_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=system_fieldnames)
        writer.writeheader()
        writer.writerows(system_records)

    # Rewrite auth users CSV without processed entries
    remaining = [r for r in auth_rows if r.get('AUTH_URLS') not in processed_urls]
    with open(AUTH_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=auth_fieldnames)
        writer.writeheader()
        writer.writerows(remaining)

if __name__ == '__main__':
    main()
