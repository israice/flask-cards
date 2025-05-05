import sys
sys.dont_write_bytecode = True  # disable writing .pyc files into __pycache__

import os
import importlib

# List of script paths (relative or absolute)
scripts = [
    "DA_compaire_csv_files.py",
    "DB_add_user_mail_to_pack.py",
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
