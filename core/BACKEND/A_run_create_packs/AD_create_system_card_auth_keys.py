import os
import base64
import csv
from dotenv import load_dotenv

# === LOAD ENVIRONMENT VARIABLES ===
load_dotenv()  # load variables from .env

# === SETTINGS ===
file_path = os.getenv('SYSTEM_CARD_AUTH_SCV')
if not file_path:
    raise ValueError("Environment variable SYSTEM_CARD_AUTH_SCV not found in .env")

output_dir = os.path.dirname(file_path)
num_pairs_to_add = 5  # number of key pairs to add at once
key_size = 32  # size of the random key in bytes

# === PREPARE OUTPUT DIRECTORY ===
os.makedirs(output_dir, exist_ok=True)

# === CHECK IF FILE EXISTS ===
file_exists = os.path.isfile(file_path)

# === OPEN FILE AND WRITE KEYS ===
with open(file_path, mode='a', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    if not file_exists:
        writer.writerow(['KEY_IN', 'KEY_OUT'])  # write header if file is new

    for _ in range(num_pairs_to_add):
        key_in = base64.urlsafe_b64encode(os.urandom(key_size)).decode('utf-8')
        key_out = base64.urlsafe_b64encode(os.urandom(key_size)).decode('utf-8')
        writer.writerow([key_in, key_out])
