import csv
import requests

# ============ SETTINGS ============
API_KEY   = 'pat6OSgFQuTQdWjIr.9bbd79557c984f0b123e8f4d6f696b3ee5d2cc2b675470c63f66c38f1d7d64c4'
BASE_ID   = 'app8EMe8KlU5dSbaS'
TABLE_ID  = 'tblusP2C8jO1S2a82'
VIEW_NAME = 'viwiJ8BBei9vj2KJY'  # optional view filter

ENDPOINT = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}'
HEADERS  = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type':  'application/json'
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
    # Read CSV, skip header row
    with open(r'core\data\system_full_db.csv', 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        headers = next(reader)          # CSV header = field names
        rows = [row for row in reader if row]

    key_field = headers[0]            # primary key field name

    # Prepare HTTP session
    session = requests.Session()
    session.headers.update(HEADERS)

    # Fetch existing IDs and blank record slots
    existing_map, blank_ids = fetch_existing_and_blanks(key_field, session)

    to_update = []  # records to PATCH (first blank slot)
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

    # Execute PATCH for updated records
    for batch in chunked(to_update, 10):
        response = session.patch(ENDPOINT, json={'records': batch})
        if not response.ok:
            print(f"PATCH error: {response.status_code} {response.text}")

    # Execute POST for new records
    for batch in chunked(to_create, 10):
        response = session.post(ENDPOINT, json={'records': batch})
        if not response.ok:
            print(f"POST error: {response.status_code} {response.text}")


if __name__ == '__main__':
    main()
