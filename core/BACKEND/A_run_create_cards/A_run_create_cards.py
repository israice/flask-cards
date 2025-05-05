import sys
sys.dont_write_bytecode = True  # disable writing .pyc files into __pycache__

import os
import importlib

# List of script paths (relative or absolute)
scripts = [

    "AE_create_system_card_auth_keys.py",
    "AF_add_domain_to_system_card_url.py",
    "AA_generate_images.py",
    "AB_create_5_new_card_ids.py",
    "AG_add_card_id_to_card_url.py",
    "AH_add_card_id_to_image_file_name.py",
    "AI_create_qr_files.py",
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
