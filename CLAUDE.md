# NAKAMA Flask Cards - AI Assistant Guide

## Project Overview

**NAKAMA** is a Flask-based web application for managing collectible cards with cryptocurrency surprise boxes. The application allows users to authenticate via Google OAuth, view their card collections, and provides admin capabilities for card creation and pack management.

**Key Features:**
- Google OAuth authentication
- User card collection management
- Admin dashboard for card/pack creation
- QR code generation for cards
- Card image generation
- CSV-based data storage
- Docker deployment support

**Live URLs:**
- Production: https://nakama.weforks.org/
- Local: http://localhost:5001/

## Technology Stack

### Backend
- **Python 3.12+**
- **Flask 2.3+** - Web framework
- **Authlib 1.3+** - OAuth integration
- **python-dotenv** - Environment variable management
- **Werkzeug 3.0+** - WSGI utilities

### Data & Processing
- **pandas 2.2+** - CSV data manipulation
- **requests 2.31+** - HTTP requests (CoinGecko API)

### Image Generation
- **qrcode 7.4+** - QR code generation
- **Pillow 10.2+** - Image processing

### Deployment
- **Docker** - Container deployment
- **docker-compose** - Multi-container orchestration

## Project Structure

```
flask-cards/
├── run.py                          # Application entry point
├── routes.py                       # Flask route definitions (Blueprint)
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker image definition
├── docker-compose.yml              # Docker orchestration
├── .env                           # Environment variables (NOT in git)
├── .gitignore                     # Git ignore rules
├── README.md                      # User documentation
├── CLAUDE.md                      # This file - AI assistant guide
│
├── core/
│   ├── BACKEND/                   # Backend processing modules
│   │   ├── A_create_cards/        # Card creation pipeline
│   │   │   ├── A_run_create_cards.py      # Main orchestrator
│   │   │   ├── AA_get_top_coingecko_coins.py
│   │   │   ├── AB_create_USER_TYPE_db.py
│   │   │   ├── AC_create_CARD_OWNER_db.py
│   │   │   ├── AD_create_CARD_ID_db.py
│   │   │   ├── AE_create_CARD_COINS_db.py
│   │   │   ├── AF_create_USD_AMMOUNT_db.py
│   │   │   ├── AG_create_CARD_NAME_db.py
│   │   │   ├── AH_create_PACK_ID_db.py
│   │   │   ├── AI_create_CARD_CHAIN_db.py
│   │   │   ├── AJ_create_CARD_THEME_db.py
│   │   │   ├── AK_create_CARD_TYPE_db.py
│   │   │   ├── AL_create_CARD_DATE_db.py
│   │   │   ├── AM_create_CARD_KEYS_db.py
│   │   │   ├── AN_create_CARD_URL_db.py
│   │   │   ├── AO_create_qr_files.py
│   │   │   ├── AP_create_images.py
│   │   │   └── AQ_create_images_names.py
│   │   ├── B_create_pack/         # Pack creation module
│   │   │   └── B_run_create_pack.py
│   │   ├── C_send_packs_to_store/ # Store integration
│   │   │   └── C_run_send_packs_to_store.py
│   │   └── D_change_card_owner/   # Ownership transfer
│   │       ├── D_run_change_card_owner.py
│   │       ├── DA_move_auth_user_to_db.py
│   │       └── DB_update_user_type_for_admins_in_db.py
│   │
│   ├── FRONTEND/                  # HTML templates
│   │   ├── login.html             # Main login page
│   │   ├── profile.html           # User profile/cards view
│   │   ├── table.html             # Admin dashboard
│   │   ├── add_card_owner.html    # Card ownership claim page
│   │   ├── card_1.html            # Card detail fragment
│   │   ├── card_2.html            # Card detail fragment
│   │   ├── card_3.html            # Card detail fragment
│   │   ├── 404.html               # Error page
│   │   └── img/                   # Static images
│   │       └── coin.gif
│   │
│   └── data/                      # Data storage
│       ├── system_full_db.csv     # Main database (all card data)
│       ├── admin_db.csv           # Admin email whitelist
│       ├── user_db.csv            # User email registry
│       ├── auth_cards.csv         # Card authentication log
│       ├── coins_db.json          # Cryptocurrency data
│       ├── cards_bank/            # Generated card images
│       │   └── Card_*.png
│       └── qr_codes/              # Generated QR codes
│           └── Card_*.png
│
└── readme/                        # Documentation images
    ├── main_login.png
    ├── card_login.png
    ├── user_profile_page.png
    ├── admin_profile_page.png
    └── admin_page.png
```

## Key Components

### 1. Application Entry (run.py)

**Purpose:** Initialize and configure the Flask application

**Key Responsibilities:**
- Load environment variables from `.env`
- Configure Flask app with template folder and secret key
- Initialize OAuth with Google
- Register routes blueprint
- Create URL aliases for cleaner endpoints
- Validate required environment variables
- Start development server

**Important Configuration:**
- ProxyFix middleware for HTTPS headers
- Werkzeug logging disabled (set to CRITICAL)
- `dont_write_bytecode = True` to prevent .pyc files

**Required .env Variables:**
- `SESSION_SECRET` - Flask session encryption key
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth secret
- `PORT` - Server port (default: 5001)
- `TEMPLATE_FOLDER` - Path to templates (core/FRONTEND)
- `CARDS_BANK_FOLDER` - Path to card images
- `AUTH_USERS` - Path to auth_cards.csv
- `SYSTEM_FULL_DB_CSV` - Path to main database

### 2. Routes (routes.py)

**Architecture:** Flask Blueprint pattern

**Route Groups:**

#### Authentication Routes
- `GET /` → Redirect to login
- `GET /login` → Display login page
- `GET /google-login` → Initiate Google OAuth
- `GET /auth/google/callback` → Handle OAuth callback
- `GET /logout` → Clear session

#### User Routes
- `GET /profile` → User profile and card collection
- `GET /api/cards` → JSON API for user cards

#### Admin Routes (require admin email in admin_db.csv)
- `GET /table` → Admin dashboard
- `GET /get_users` → JSON API for all records
- `POST /run_create_cards` → Trigger card creation pipeline

#### Card Routes
- `GET /card/<key>` → Public card claim page
- `GET /card_image/<filename>` → Serve card images
- `GET /card_1.html` → Card detail fragment 1
- `GET /card_2.html` → Card detail fragment 2
- `GET /card_3.html` → Card detail fragment 3

#### Error Handlers
- `404` → Custom 404 page

**Helper Functions:**
- `load_records_from_csv()` - Load all records from system_full_db.csv
- `load_whitelist(path)` - Load email whitelist from CSV
- `determine_user_is_admin(email)` - Check admin status
- `get_user_cards(email)` - Get cards owned by user

### 3. Backend Module System

**Convention:** Alphabetically ordered modules with prefix naming

**Module Naming Pattern:**
- **Prefix A** = Card creation pipeline
- **Prefix B** = Pack creation
- **Prefix C** = Store integration
- **Prefix D** = Ownership transfer

**Script Naming Convention:**
- `A_run_*.py` - Main orchestrator for module
- `AA_*, AB_*, AC_*...` - Individual tasks in execution order

**Orchestrator Pattern:**
Each module has a main runner (e.g., `A_run_create_cards.py`) that:
1. Defines a list of script paths in execution order
2. Dynamically imports each script
3. Calls the `main()` function if it exists
4. Handles errors gracefully with try/except

**Common Script Pattern:**
```python
#!/usr/bin/env python3
import csv
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
FILENAME = os.getenv('SYSTEM_FULL_DB_CSV')

# Script-specific settings
TARGET_COLUMN_INDEX = 0  # Which CSV column to modify

def main():
    # Read CSV
    # Process data
    # Write CSV
    pass

if __name__ == '__main__':
    main()
```

**CSV Column Pattern:**
Scripts operate on specific columns of `system_full_db.csv`:
- Column 0: CARD_ID
- Column 1: USER_TYPE
- Column 2: CARD_OWNER
- Column 3: CARD_COINS
- Column 4: USD_AMMOUNT
- Column 5: CARD_NAME
- Column 6: PACK_ID
- Column 7: CARD_CHAIN
- Column 8: CARD_THEME
- Column 9: CARD_TYPE
- Column 10: CARD_DATE
- Column 11: CARD_KEYS
- Column 12: CARD_URL

### 4. Frontend Templates

**Template Engine:** Jinja2

**Template Hierarchy:**
- Base templates: `login.html`, `profile.html`, `table.html`
- Fragment templates: `card_1.html`, `card_2.html`, `card_3.html`
- Error templates: `404.html`

**Data Flow:**
1. Routes pass data to templates via render_template()
2. Templates use Jinja2 syntax for dynamic content
3. AJAX calls to `/api/cards` and `/get_users` for dynamic updates
4. Card fragments loaded dynamically on profile page

**Static Assets:**
- Card images: Served from `CARDS_FOLDER` via `/card_image/<filename>`
- GIFs/icons: Stored in `core/FRONTEND/img/`

### 5. Data Management

**Primary Database:** `core/data/system_full_db.csv`
- CSV-based storage (not SQL)
- Header row defines column names
- Each row represents one card
- Modified by backend scripts using pandas

**Whitelist Files:**
- `admin_db.csv` - Admin emails (column 0)
- `user_db.csv` - All user emails (auto-populated)
- `auth_cards.csv` - Card authentication log

**JSON Data:**
- `coins_db.json` - Cryptocurrency data from CoinGecko API

**Generated Assets:**
- `cards_bank/Card_*.png` - Card images
- `qr_codes/Card_*.png` - QR codes

### 6. Authentication & Authorization

**OAuth Provider:** Google OAuth 2.0

**User Types:**
1. **Anonymous** - Not logged in
2. **User** - Logged in, email in user_db.csv
3. **Admin** - Logged in, email in admin_db.csv

**Access Control:**
- `/profile` - Requires authentication
- `/table` - Requires admin status
- `/run_create_cards` - Requires admin status
- `/card/<key>` - Public (for card claiming)

**Session Management:**
- Session stored in Flask secure cookies
- `session['user']` contains `{'email': 'user@example.com'}`
- `session.clear()` on logout

**Card Ownership Flow:**
1. User scans QR code → `/card/<key>`
2. User clicks "Add to Collection"
3. Redirects to Google login with `?next=add_card_owner`
4. After auth, email logged to `auth_cards.csv`
5. Triggers `D_run_change_card_owner.py` via subprocess
6. Card ownership transferred in database

## Development Workflow

### Local Development

1. **Setup Environment:**
   ```bash
   # Create .env file with required variables
   cp .env_EXAMPLE .env
   # Edit .env with your credentials
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Application:**
   ```bash
   python run.py
   ```

4. **Access Application:**
   - Local: http://localhost:5001/
   - Production: https://nakama.weforks.org/

### Docker Deployment

1. **Build Image:**
   ```bash
   docker build .
   ```

2. **Start Container:**
   ```bash
   docker-compose up -d
   ```

3. **Stop Container:**
   ```bash
   docker-compose down
   ```

4. **Quick Restart:**
   ```bash
   docker-compose down; docker-compose up -d
   ```

### Git Workflow

**Current Branch:** `claude/claude-md-mjd0fq2heyedcerk-z9OJq`

**Common Git Commands:**
```bash
# Update from remote
git fetch origin
git reset --hard origin/master
git clean -fd

# Quick commit
git add .
git commit -m "descriptive message"
git push -u origin <branch-name>
```

**Branch Naming Convention:**
- Feature branches: `claude/<description>-<session-id>`
- Must start with `claude/` and end with matching session ID

## Conventions & Patterns

### Python Code Conventions

1. **Bytecode Prevention:**
   ```python
   import sys
   sys.dont_write_bytecode = True  # First lines of every script
   ```

2. **Environment Loading:**
   ```python
   from dotenv import load_dotenv
   load_dotenv()  # Load before accessing os.getenv()
   ```

3. **CSV Dialect Detection:**
   ```python
   def detect_dialect(filename, sample_size=2048):
       with open(filename, newline='', encoding='utf-8') as f:
           sample = f.read(sample_size)
           return csv.Sniffer().sniff(sample)
   ```

4. **Main Function Pattern:**
   ```python
   def main():
       # Script logic here
       pass

   if __name__ == '__main__':
       main()
   ```

5. **Path Handling:**
   - Always use `os.path.join()` for cross-platform compatibility
   - Use `os.getenv()` for configurable paths
   - Use absolute paths from project root

### File Organization

1. **Backend Scripts:**
   - One task per script
   - Alphabetical prefix for execution order
   - Import via orchestrator, not direct execution

2. **Frontend Templates:**
   - HTML files in `core/FRONTEND/`
   - Use Jinja2 templating
   - Keep static assets in `img/` subdirectory

3. **Data Files:**
   - CSV files use UTF-8 encoding
   - JSON files for structured data
   - Images in dedicated subdirectories

### Error Handling

1. **Environment Variables:**
   ```python
   if not FILENAME:
       print("ERROR: VAR_NAME is not set in .env")
       exit(1)
   ```

2. **CSV Operations:**
   ```python
   try:
       # CSV operation
   except IndexError as e:
       print(f"ERROR: {e}")
       return
   ```

3. **Subprocess Calls:**
   ```python
   try:
       subprocess.run(['python', 'script.py'], check=True)
   except subprocess.CalledProcessError:
       pass  # Handle gracefully
   ```

### Logging & Debugging

1. **Werkzeug Logs:** Disabled (CRITICAL level only)
2. **Print Statements:** Used for script output
3. **Error Messages:** Prefixed with "ERROR:"

## Common Tasks

### Creating New Cards

**Trigger:** Admin clicks "NEW PACK" button in `/table`

**Process:**
1. POST to `/run_create_cards`
2. Executes `core/BACKEND/A_create_cards/A_run_create_cards.py`
3. Runs 17 scripts in sequence:
   - AA: Fetch coin data from CoinGecko
   - AB-AM: Generate card attributes
   - AN: Create card URLs
   - AO: Generate QR codes
   - AP: Generate card images
   - AQ: Set image filenames

**Result:** New cards added to `system_full_db.csv` with CARD_OWNER='SYSTEM'

### Transferring Card Ownership

**Trigger:** User authenticates via `/card/<key>`

**Process:**
1. User email logged to `auth_cards.csv`
2. Subprocess executes `D_run_change_card_owner.py`
3. Script updates CARD_OWNER in `system_full_db.csv`
4. User redirected to `/profile` to see new card

### Adding New Admin

**Manual Process:**
1. Open `core/data/admin_db.csv`
2. Add email address to new row
3. Save file
4. User will have admin access on next login

### Modifying Card Attributes

**To modify existing cards:**
1. Create new script in `core/BACKEND/A_create_cards/`
2. Follow naming convention: `AX_create_ATTRIBUTE_db.py`
3. Use TARGET_COLUMN_INDEX for CSV column
4. Add script to orchestrator list in `A_run_create_cards.py`

## Important Notes for AI Assistants

### When Making Changes

1. **Always Read First:**
   - Read files before editing
   - Understand context before suggesting changes
   - Check .env requirements

2. **Preserve Patterns:**
   - Maintain alphabetical script ordering
   - Keep bytecode prevention
   - Use existing error handling patterns
   - Follow column index conventions

3. **Test Paths:**
   - Verify file paths exist
   - Check .env variable names
   - Ensure CSV column indices are correct

4. **Security Considerations:**
   - Never commit `.env` file
   - Validate user input in routes
   - Check admin status before privileged operations
   - Use session['user'] for authentication

5. **Data Integrity:**
   - Always use CSV dialect detection
   - Preserve UTF-8 encoding
   - Handle missing columns gracefully
   - Don't remove existing data without explicit request

### Common Pitfalls

1. **Path Issues:**
   - Paths are relative to project root, not script location
   - Use `os.path.join()` not string concatenation
   - Template folder is `core/FRONTEND/` not `templates/`

2. **CSV Column Indices:**
   - Indices start at 0
   - Header row is row 0
   - Some scripts skip header with `next(reader, None)`

3. **Environment Variables:**
   - Must load dotenv before accessing
   - Check for None/empty values
   - Fail fast if required vars missing

4. **OAuth Configuration:**
   - Requires HTTPS in production
   - Callback URL must match Google Console
   - Session secret must be secure random string

5. **Docker Context:**
   - `.env` file must exist in Docker context
   - Volumes mounted at `/app`
   - Port 5001 exposed and mapped

### File Modification Guidelines

**DO:**
- Edit existing files when possible
- Maintain existing code style
- Add error handling
- Use environment variables for paths
- Follow alphabetical ordering

**DON'T:**
- Create new files without explicit request
- Remove error handling
- Hardcode paths or credentials
- Skip environment variable validation
- Change execution order without testing

### Testing Changes

**Before Committing:**
1. Verify .env has required variables
2. Test routes in browser
3. Check CSV files aren't corrupted
4. Verify images generate correctly
5. Test both user and admin flows

**Docker Testing:**
1. Build image: `docker build .`
2. Run container: `docker-compose up -d`
3. Check logs: `docker-compose logs -f`
4. Test in browser
5. Stop: `docker-compose down`

## Version History

**Current Version:** v1.008

**Major Milestones:**
- v0.1.0 - Initial working version
- v1.0 - First production release
- v1.003 - Docker support added
- v1.004 - Airtable integration (later removed)
- v1.006 - Card detail pages added
- v1.008 - Localhost domain support

## Contact & Resources

- **Repository:** https://github.com/israice/flask-cards.git
- **Production URL:** https://nakama.weforks.org/
- **Local Development:** http://localhost:5001/

## Future Plans (v999)

- Add stats to each card
- Fix domain configuration for multiple environments
- Deploy to Linux production server

---

**Last Updated:** 2025-12-19
**Document Version:** 1.0
**Target Audience:** AI assistants (Claude, GPT, etc.) working on this codebase
