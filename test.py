import csv
import requests
from itertools import islice

# ============ Настройки ============
API_KEY    = 'pat6OSgFQuTQdWjIr.9bbd79557c984f0b123e8f4d6f696b3ee5d2cc2b675470c63f66c38f1d7d64c4'
BASE_ID    = 'app8EMe8KlU5dSbaS'       # app…
TABLE_ID   = 'tblusP2C8jO1S2a82'       # tbl…
VIEW_NAME  = 'viwiJ8BBei9vj2KJY'       # ваш view (опционально)

ENDPOINT = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}'
HEADERS  = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type':  'application/json'
}

def chunked(iterable, size):
    """Yield successive chunks from iterable of given size."""
    it = iter(iterable)
    while True:
        batch = list(islice(it, size))
        if not batch:
            break
        yield batch

def fetch_existing(id_field):
    """
    Fetch all records, return:
      - existing_map: { value_of_id_field: record_id }
      - blank_ids: list of record_id where that field is missing/empty
    """
    existing_map = {}
    blank_ids    = []
    params = {'view': VIEW_NAME, 'pageSize': 100}
    while True:
        resp = requests.get(ENDPOINT, headers=HEADERS, params=params)
        resp.raise_for_status()
        data = resp.json()
        for rec in data.get('records', []):
            rid = rec['id']
            v   = rec.get('fields', {}).get(id_field)
            if v:
                existing_map[str(v)] = rid
            else:
                blank_ids.append(rid)
        offset = data.get('offset')
        if not offset:
            break
        params['offset'] = offset
    return existing_map, blank_ids

def main():
    # 1. Читаем CSV: пропускаем первую строку (заголовок)
    with open(r'core\data\system_full_db.csv', 'r', encoding='utf-8', newline='') as f:
        reader      = csv.reader(f)
        headers_row = next(reader)                     # имена полей
        rows        = [row for row in reader if row]   # только данные

    key_field = headers_row[0]  # имя поля-ключа (первый столбец)

    # 2. Получаем существующие записи и список пустых
    existing_map, blank_ids = fetch_existing(key_field)

    # 3. Разбираем первую строку CSV отдельно для PATCH, остальные — для POST
    to_update = []  # для первой "пустой" записи
    to_add    = []  # для создания новых записей

    for idx, row in enumerate(rows):
        csv_id = row[0].strip()
        # мапим все колонки по именам из headers_row
        fields = { headers_row[i]: row[i] for i in range(len(headers_row)) }

        # если уже есть запись с таким ID — пропускаем
        if csv_id in existing_map:
            continue

        if idx == 0 and blank_ids:
            # первая строка CSV → обновляем первую пустую запись Airtable
            rec_id = blank_ids.pop(0)
            to_update.append({'id': rec_id, 'fields': fields})
        else:
            # остальные строки → просто добавляем
            to_add.append({'fields': fields})

    # 4a. PATCH – обновляем первую пустую запись
    if to_update:
        for batch in chunked(to_update, 10):
            r = requests.patch(ENDPOINT, headers=HEADERS, json={'records': batch})
            if not r.ok:
                print(f"PATCH Error: {r.status_code} {r.text}")

    # 4b. POST – создаём остальные
    if to_add:
        for batch in chunked(to_add, 10):
            r = requests.post(ENDPOINT, headers=HEADERS, json={'records': batch})
            if not r.ok:
                print(f"POST Error: {r.status_code} {r.text}")

if __name__ == '__main__':
    main()
