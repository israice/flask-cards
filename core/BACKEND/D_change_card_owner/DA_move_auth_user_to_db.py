import os
import csv
import requests
from dotenv import load_dotenv

def main():
    # Load environment variables from .env file
    load_dotenv()
    AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
    AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
    AIRTABLE_TABLE_ID = os.getenv('AIRTABLE_TABLE_ID')
    AIRTABLE_VIEW_NAME = os.getenv('AIRTABLE_VIEW_NAME')  # optional

    if not all([AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID]):
        raise RuntimeError("Missing one of AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID in environment")

    # Airtable base URL for REST API
    base_url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    # Path to auth_users.csv
    auth_csv = os.path.join('core', 'data', 'auth_users.csv')

    # Read auth_users.csv rows
    with open(auth_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames  # preserve original column order

    processed_urls = set()
    errors = []

    # Process each row: update Airtable and mark for removal if successful
    for row in rows:
        card_url = row.get('AUTH_URLS')
        owner_email = row.get('AUTH_MAILS')
        if not card_url or not owner_email:
            continue  # skip rows with missing data

        # Build filterByFormula to locate the record by CARD_URL
        params = {
            "filterByFormula": f"{{CARD_URL}} = '{card_url}'"
        }
        if AIRTABLE_VIEW_NAME:
            params["view"] = AIRTABLE_VIEW_NAME

        # GET request to find matching record
        response = requests.get(base_url, headers=headers, params=params)
        if response.status_code != 200:
            errors.append(f"Fetch failed for {card_url}: {response.status_code}")
            continue  # skip deletion for this URL

        data = response.json()
        records = data.get('records', [])
        if not records:
            errors.append(f"No Airtable record with CARD_URL = {card_url}")
            continue

        record_id = records[0]['id']
        payload = {"fields": {"CARD_OWNER": owner_email}}

        # PATCH request to update the record
        update_url = f"{base_url}/{record_id}"
        update_resp = requests.patch(update_url, headers=headers, json=payload)
        if update_resp.status_code not in (200, 201):
            errors.append(f"Update failed for record {record_id}: {update_resp.status_code}")
            continue

        # Mark this URL as processed
        processed_urls.add(card_url)

    # Rewrite auth_users.csv without processed rows
    remaining = [r for r in rows if r.get('AUTH_URLS') not in processed_urls]
    with open(auth_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(remaining)

    # If any errors occurred, raise aggregated exception
    if errors:
        error_msg = "\n".join(errors)
        raise RuntimeError(f"Some records failed:\n{error_msg}")

if __name__ == '__main__':
    main()
