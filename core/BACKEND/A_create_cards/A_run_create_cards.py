import sys
sys.dont_write_bytecode = True  # disable writing .pyc files into __pycache__

import os
import importlib

# List of script paths (relative or absolute)
scripts = [
    "AA_get_top_coingecko_coins.py",
    "AD_create_CARD_ID_db.py",
    "AH_create_PACK_ID_db.py",
    "AL_create_CARD_DATE_db.py",
    "AB_create_USER_TYPE_db.py",
    "AC_create_CARD_OWNER_db.py",
    "AE_create_CARD_COINS_db.py",
    "AF_create_USD_AMMOUNT_db.py",
    "AG_create_CARD_NAME_db.py",
    "AI_create_CARD_CHAIN_db.py",
    "AJ_create_CARD_THEME_db.py",
    "AK_create_CARD_TYPE_db.py",
    "AM_create_CARD_KEYS_db.py",
    "AN_create_CARD_URL_db.py",
    "AS_create_MONSTER_POWER_db.py",
    "AT_create_POWER_COMBAT_db.py",
    "AR_create_CARD_DESCRIPTION_db.py",
    "AO_create_qr_files.py",
    "AP_create_images.py",
    "AQ_create_images_names.py",
]

for script_path in scripts:
    try:
        # Split path and filename
        dir_path = os.path.dirname(script_path)
        filename = os.path.basename(script_path)
        module_name = os.path.splitext(filename)[0] 

        # Add directory to sys.path if not already present
        abs_dir_path = os.path.abspath(dir_path)
        if abs_dir_path not in sys.path:
            sys.path.append(abs_dir_path)

        module = importlib.import_module(module_name)

        # If the script has a main() function, call it explicitly
        if hasattr(module, "main"):
            module.main()

    except ModuleNotFoundError:
        print(f"Module {module_name} not found in {abs_dir_path}.\n")
    except Exception as e:
        print(f"Error running {module_name}: {e}\n")
