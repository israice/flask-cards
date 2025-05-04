from flask import Flask, render_template, abort
import csv
import os

app = Flask(__name__, template_folder='core/FRONTEND')

# Load valid KEY_IN values from CSV at startup
CSV_FILE = os.path.join('core', 'data', 'system_card_auth.csv')
VALID_KEYS = set()

with open(CSV_FILE, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        VALID_KEYS.add(row['KEY_IN'])

@app.route('/<path:key>')
def serve_card_page(key):
    # Reconstruct the full URL path to match what's in the CSV
    full_url = f'http://localhost:5000/{key}'

    if full_url in VALID_KEYS:
        # If key is valid, render the target HTML page
        return render_template('add_card_owner.html')
    else:
        # If key not found, return 404 error
        abort(404)

# Custom 404 error handler
@app.errorhandler(404)
def page_not_found(e):
    # Render the custom 404 page
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
