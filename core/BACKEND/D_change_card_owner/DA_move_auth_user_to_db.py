import csv
import os

def main():
    # Define paths to CSV files
    base_dir = os.path.join('core', 'data')
    auth_path = os.path.join(base_dir, 'auth_users.csv')
    db_path = os.path.join(base_dir, 'system_full_db.csv')

    # Read auth_users.csv into a mapping of URL -> mail
    auth_map = {}
    with open(auth_path, newline='', encoding='utf-8') as auth_file:
        reader = csv.DictReader(auth_file)
        for row in reader:
            url = row.get('AUTH_URLS')
            mail = row.get('AUTH_MAILS')
            if url:
                auth_map[url] = mail

    # Read system_full_db.csv rows
    with open(db_path, newline='', encoding='utf-8') as db_file:
        reader = csv.DictReader(db_file)
        fieldnames = reader.fieldnames  # Preserve original columns
        rows = list(reader)

    # Update CARD_OWNER for matching CARD_URLs
    for row in rows:
        card_url = row.get('CARD_URL')
        if card_url in auth_map:
            row['CARD_OWNER'] = auth_map[card_url]

    # Write updated rows back to system_full_db.csv
    with open(db_path, 'w', newline='', encoding='utf-8') as db_file:
        writer = csv.DictWriter(db_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Truncate auth_users.csv to header only
    with open(auth_path, 'w', newline='', encoding='utf-8') as auth_file:
        writer = csv.writer(auth_file)
        writer.writerow(['AUTH_MAILS', 'AUTH_URLS'])

if __name__ == '__main__':
    main()
