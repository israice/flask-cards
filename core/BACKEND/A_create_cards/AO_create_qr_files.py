import os
import re
import csv
import sys
import qrcode
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import sys
import qrcode
# Adjust path to import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from core.database import query_db

# Configurable parameters from environment
OUTPUT_DIR = os.getenv('QR_CODES_FOLDER')
ENCODING = 'utf-8'

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

def generate_qr_codes():
    if not OUTPUT_DIR:
        print("QR_CODES_FOLDER env var not set.")
        return

    # Ensure output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    rows = query_db("SELECT card_id, card_url FROM cards")
    
    count = 0
    skipped = 0
    
    for row in rows:
        cid = row['card_id']
        url = row['card_url']
        
        if not cid or not url:
            continue
            
        safe_name = sanitize_filename(cid)
        output_filename = FILE_NAME_TEMPLATE.format(filename=safe_name)
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        if os.path.exists(output_path):
            skipped += 1
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
        count += 1
        
    print(f"Generated {count} QR codes, skipped {skipped}.")

def main():
    generate_qr_codes()

if __name__ == "__main__":
    main()



