import sys
sys.dont_write_bytecode = True  # disable writing .pyc files into __pycache__

import os
import importlib

# List of script paths (relative or absolute)
scripts = [
    # "AA_create_system_card_auth_keys.py",
    # "AB_add_domain_to_system_card_url.py",

    # "AA_get_top_coingecko_coins.py",
    "AB_create_USER_TYPE_db.py",
    "AC_create_CARD_OWNER_db.py",
    "AD_create_5_new_card_ids.py",
    "AE_create_CARD_COINS_db.py",
    "AF_create_USD_AMMOUNT_db.py",
    "AG_create_CARD_NAME_db.py",

    # "AC_generate_images.py",
    # "AE_add_card_id_to_card_url.py",
    # "AF_add_card_id_to_image_file_name.py",
    # "AG_create_qr_files.py",
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
