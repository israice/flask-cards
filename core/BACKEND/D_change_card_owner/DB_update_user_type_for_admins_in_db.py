import pandas as pd

# Load admin whitelist from CSV and create a set of emails
admin_whitelist_df = pd.read_csv('core/data/admin_db.csv')
admin_whitelist = set(
    admin_whitelist_df['ADMIN_WHITELIST']
    .dropna()
    .str.strip()
)

# Load user whitelist from CSV and create a set of emails
user_whitelist_df = pd.read_csv('core/data/user_db.csv')
user_whitelist = set(
    user_whitelist_df['USER_WHITELIST']
    .dropna()
    .str.strip()
)

# Load the full system database
full_df = pd.read_csv('core/data/system_full_db.csv')

# Define function to update USER_TYPE based on CARD_OWNER value and whitelists
def update_user_type(row):
    owner = row.get('CARD_OWNER')
    # If owner is missing or empty, classify as SYSTEM
    if pd.isna(owner) or not str(owner).strip():
        return 'SYSTEM'
    owner_str = str(owner).strip()
    # If owner is in user whitelist, set USER
    if owner_str in user_whitelist:
        return 'USER'
    # If owner is in admin whitelist, set ADMIN
    if owner_str in admin_whitelist:
        return 'ADMIN'
    # All other cases default to SYSTEM
    return 'SYSTEM'

# Apply the update function to USER_TYPE column
full_df['USER_TYPE'] = full_df.apply(update_user_type, axis=1)

# Save the updated DataFrame back to CSV (overwrite original)
full_df.to_csv('core/data/system_full_db.csv', index=False)
