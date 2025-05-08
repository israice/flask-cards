import os
import re
import csv
import sys
import qrcode
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configurable parameters from environment
INPUT_FILE = os.getenv('SYSTEM_FULL_DB_CSV')
OUTPUT_DIR = os.getenv('QR_CODES_FOLDER')
ENCODING = 'utf-8'

# Validate environment variables
if not INPUT_FILE:
    raise ValueError("Environment variable (input CSV path) is not set.")
if not OUTPUT_DIR:
    raise ValueError("Environment variable QR_CODES_FOLDER (output directory) is not set.")

# CSV column indices (0-based)
URL_COLUMN_INDEX = 12       # Column index for QR code data (KEY_IN)
FILENAME_COLUMN_INDEX = 0  # Column index for output file name key (CARD_ID)
MAX_INDEX = max(URL_COLUMN_INDEX, FILENAME_COLUMN_INDEX)

# QR code settings
QR_VERSION = 1
ERROR_CORRECTION = qrcode.constants.ERROR_CORRECT_L
BOX_SIZE = 10
BORDER = 4
FILL_COLOR = "black"
BACK_COLOR = "white"

# File name template
FILE_NAME_TEMPLATE = '{filename}.png'

# Regex to strip invalid filesystem characters (Windows)
INVALID_FILENAME_CHARS = re.compile(r'[\\/*?:"<>|]')

def sanitize_filename(name):
    """Remove or replace characters not allowed in file names."""
    sanitized = INVALID_FILENAME_CHARS.sub('_', name)
    return sanitized.strip()

# Ensure output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Process CSV file and generate QR codes
with open(INPUT_FILE, 'r', encoding=ENCODING) as file:
    csv_reader = csv.reader(file)
    header = next(csv_reader, None)  # Skip header row if present

    for row_num, row in enumerate(csv_reader, start=2):  # start=2 accounts for header line
        # Skip empty or malformed rows
        if not row or len(row) <= MAX_INDEX:
            continue

        url = row[URL_COLUMN_INDEX].strip()
        raw_name = row[FILENAME_COLUMN_INDEX].strip()

        if not url:
            # Skip rows without URL data
            print(f"Skipping row {row_num}, empty URL.")
            continue

        # Sanitize the base filename (CARD_ID)
        safe_name = sanitize_filename(raw_name)
        output_filename = FILE_NAME_TEMPLATE.format(filename=safe_name)
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        if os.path.exists(output_path):
            # Skip generation if file already exists
            continue

        # Create QR code object
        qr = qrcode.QRCode(
            version=QR_VERSION,
            error_correction=ERROR_CORRECTION,
            box_size=BOX_SIZE,
            border=BORDER,
        )
        qr.add_data(url)
        qr.make(fit=True)

        # Generate image and save to file
        qr_image = qr.make_image(fill_color=FILL_COLOR, back_color=BACK_COLOR)
        qr_image.save(output_path)



