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

def delete_extra_records(id_field, csv_values, session):
    """
    Permanently delete all records whose key_field value is NOT in csv_values.
    """
    existing_map, _ = fetch_existing_and_blanks(id_field, session)
    to_delete = [rec_id for val, rec_id in existing_map.items() if val not in set(csv_values)]
    if not to_delete:
        return

    # Delete in batches of 10
    for batch in chunked(to_delete, 10):
        # build query params: records[]=recId1&records[]=recId2...
        params = [('records[]', rec_id) for rec_id in batch]
        response = session.delete(ENDPOINT, params=params)
        if not response.ok:
            print(f"DELETE error: {response.status_code} {response.text}")
            sys.exit(1)

def main():
    """Sync CSV data to Airtable, deleting extras and preserving order/IDs."""
    csv_path = os.path.join('core', 'data', 'system_full_db.csv')
    with open(csv_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        headers = next(reader)  # CSV header = field names
        rows = [row for row in reader if row]

    key_field = headers[0]  # primary key field name

    # Prepare HTTP session with headers
    session = requests.Session()
    session.headers.update(HEADERS)

    # Build list of CSV key values
    csv_values = [row[0].strip() for row in rows if row[0].strip()]

    # 1) Delete all Airtable records not present in CSV
    delete_extra_records(key_field, csv_values, session)

    # 2) Fetch existing records and blank slots after deletion
    existing_map, blank_ids = fetch_existing_and_blanks(key_field, session)

    to_update = []  # blank slots to fill via PATCH
    to_create = []  # new records to POST

    # 3) For each CSV row: if exists—skip; else fill blank slot or create new
    for row in rows:
        record_value = row[0].strip()
        if not record_value or record_value in existing_map:
            continue
        fields = {headers[i]: row[i] for i in range(len(headers))}
        if blank_ids:
            # fill first blank record
            rec_id = blank_ids.pop(0)
            to_update.append({'id': rec_id, 'fields': fields})
        else:
            to_create.append({'fields': fields})

    # 4) PATCH updates for blank slots
    for batch in chunked(to_update, 10):
        response = session.patch(ENDPOINT, json={'records': batch})
        if not response.ok:
            print(f"PATCH error: {response.status_code} {response.text}")

    # 5) POST creates for truly new records
    for batch in chunked(to_create, 10):
        response = session.post(ENDPOINT, json={'records': batch})
        if not response.ok:
            print(f"POST error: {response.status_code} {response.text}")

if __name__ == '__main__':
    main()
