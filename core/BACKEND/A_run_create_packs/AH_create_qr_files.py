import os
import re
import csv
import qrcode
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configurable parameters from environment
INPUT_FILE = os.getenv('SYSTEM_CARD_AUTH_SCV')
OUTPUT_DIR = os.getenv('QR_CODES_FOLDER')
ENCODING = 'utf-8'

# CSV column indices (0-based)
URL_COLUMN_INDEX = 0       # Column index for QR code data (KEY_IN)
FILENAME_COLUMN_INDEX = 2  # Column index for output file name key (CARD_ID)

# QR code settings
QR_VERSION = 1
ERROR_CORRECTION = qrcode.constants.ERROR_CORRECT_L
BOX_SIZE = 10
BORDER = 4
FILL_COLOR = "black"
BACK_COLOR = "white"

# File name template
FILE_NAME_TEMPLATE = '{filename}.png'  # Template for QR code file names

# Regex to strip invalid filesystem characters (Windows)
INVALID_FILENAME_CHARS = re.compile(r'[\\/*?:"<>|]')

def sanitize_filename(name):
    """Remove or replace characters not allowed in file names."""
    sanitized = INVALID_FILENAME_CHARS.sub('_', name)
    return sanitized.strip()

# Ensure output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Open the CSV file and process each row
with open(INPUT_FILE, 'r', encoding=ENCODING) as file:
    csv_reader = csv.reader(file)
    next(csv_reader)  # Skip header row

    for row in csv_reader:
        url = row[URL_COLUMN_INDEX].strip()
        raw_name = row[FILENAME_COLUMN_INDEX].strip()

        if not url:
            # Skip rows without URL data
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

