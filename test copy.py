import csv
import requests

# Replace these with your actual Airtable credentials
API_KEY = 'pat6OSgFQuTQdWjIr.9bbd79557c984f0b123e8f4d6f696b3ee5d2cc2b675470c63f66c38f1d7d64c4'
BASE_ID = 'tblusP2C8jO1S2a82'
TABLE_NAME = 'CARDS'

# Base URL for Airtable API
ENDPOINT = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}'

# HTTP headers for authentication
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

def main():
    # Open the CSV file for reading
    with open(r'core\data\system_full_db.csv', mode='r', encoding='utf-8', newline='') as csvfile:
        reader = csv.reader(csvfile)
        # Read the header row
        headers_row = next(reader)
        # First column is record ID
        id_header = headers_row[0]
        # Remaining columns are field names
        field_names = headers_row[1:]

        # Process each subsequent row
        for row in reader:
            record_id = row[0].strip()
            # Prepare the fields dict from CSV columns
            fields = { field_names[i]: row[i+1] for i in range(len(field_names)) }

            if record_id:
                # Update existing record by record ID
                url = f"{ENDPOINT}/{record_id}"
                data = {'fields': fields}
                response = requests.patch(url, json=data, headers=headers)
                if response.ok:
                    print(f"Updated record {record_id}")
                else:
                    print(f"Failed to update record {record_id}: {response.status_code} {response.text}")
            else:
                # Create new record if no record_id provided
                url = ENDPOINT
                data = {'fields': fields}
                response = requests.post(url, json=data, headers=headers)
                if response.ok:
                    new_id = response.json().get('id')
                    print(f"Created new record {new_id}")
                else:
                    print(f"Failed to create record: {response.status_code} {response.text}")

if __name__ == "__main__":
    main()
