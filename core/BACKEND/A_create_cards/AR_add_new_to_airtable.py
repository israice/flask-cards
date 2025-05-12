#!/usr/bin/env python3
from dotenv import load_dotenv
import os
import sys
import csv
import requests

# Load environment variables from .env file
load_dotenv()

# Retrieve Airtable configuration from environment
API_KEY = os.getenv('AIRTABLE_API_KEY')
BASE_ID = os.getenv('AIRTABLE_BASE_ID')
TABLE_ID = os.getenv('AIRTABLE_TABLE_ID')
VIEW_NAME = os.getenv('AIRTABLE_VIEW_NAME')

# Validate required environment variables
if not API_KEY:
    sys.exit("Error: AIRTABLE_API_KEY is not set in environment.")
if not BASE_ID:
    sys.exit("Error: AIRTABLE_BASE_ID is not set in environment.")
if not TABLE_ID:
    sys.exit("Error: AIRTABLE_TABLE_ID is not set in environment.")
if not VIEW_NAME:
    sys.exit("Error: AIRTABLE_VIEW_NAME is not set in environment.")

# Airtable API endpoint and headers
ENDPOINT = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}'
HEADERS = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}


def chunked(lst, size):
    """Yield successive chunks from list of given size."""
    for i in range(0, len(lst), size):
        yield lst[i:i+size]


def fetch_existing_and_blanks(id_field, session):
    """
    Retrieve existing records:
      - existing_map: {value_of_id_field: record_id}
      - blank_ids: list of record IDs missing the id_field
    """
    existing_map = {}
    blank_ids = []
    params = {'view': VIEW_NAME, 'pageSize': 100}

    while True:
        resp = session.get(ENDPOINT, params=params)
        resp.raise_for_status()
        data = resp.json()

        for rec in data.get('records', []):
            rec_id = rec['id']
            val = rec.get('fields', {}).get(id_field)
            if val:
                existing_map[str(val)] = rec_id
            else:
                blank_ids.append(rec_id)

        offset = data.get('offset')
        if not offset:
            break
        params['offset'] = offset

    return existing_map, blank_ids


def main():
    """Sync CSV data to Airtable: fill first blank record, then add new ones."""
    # Read CSV file, skip header row
    csv_path = r'core\data\system_full_db.csv'
    with open(csv_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        headers = next(reader)  # CSV header = field names
        rows = [row for row in reader if row]

    key_field = headers[0]  # primary key field name

    # Prepare HTTP session with headers
    session = requests.Session()
    session.headers.update(HEADERS)

    # Fetch existing IDs and blank record slots
    existing_map, blank_ids = fetch_existing_and_blanks(key_field, session)

    to_update = []  # records to PATCH (first blank slots)
    to_create = []  # records to POST (new entries)

    for idx, row in enumerate(rows):
        record_value = row[0].strip()
        # skip if no value or already exists
        if not record_value or record_value in existing_map:
            continue

        # Map all columns dynamically by header
        fields = {headers[i]: row[i] for i in range(len(headers))}

        # First data row fills first blank record via PATCH
        if idx == 0 and blank_ids:
            to_update.append({'id': blank_ids.pop(0), 'fields': fields})
        else:
            to_create.append({'fields': fields})

    # Execute PATCH for updated records in batches of 10
    for batch in chunked(to_update, 10):
        response = session.patch(ENDPOINT, json={'records': batch})
        if not response.ok:
            print(f"PATCH error: {response.status_code} {response.text}")

    # Execute POST for new records in batches of 10
    for batch in chunked(to_create, 10):
        response = session.post(ENDPOINT, json={'records': batch})
        if not response.ok:
            print(f"POST error: {response.status_code} {response.text}")


if __name__ == '__main__':
    main()
