import sys
sys.dont_write_bytecode = True  # disable writing .pyc files into **pycache**

import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
from dotenv import load_dotenv

# CONFIGURATION
load_dotenv()
APP_SECRET = os.getenv('SESSION_SECRET')
AUTH_USERS_CSV = os.getenv('AUTH_USERS')  # path to file for authenticated users logging
TEMPLATE_FOLDER = os.getenv('TEMPLATE_FOLDER')
CARDS_FOLDER = os.getenv('CARDS_BANK_FOLDER')
SYSTEM_CSV = os.getenv('SYSTEM_FULL_DB_CSV')  # path to full DB CSV

# Paths to whitelist CSVs and auth
ADMIN_DB = os.path.join('core', 'data', 'admin_db.csv')
USER_DB = os.path.join('core', 'data', 'user_db.csv')
USERS_AUTH_CSV = os.path.join('core', 'data', 'users_auth.csv')

if os.getenv('PORT') is None:
    raise SystemExit("PORT must be set in .env")
PORT = int(os.getenv('PORT'))

# Ensure required envs are set
required_envs = {
    'SESSION_SECRET': APP_SECRET,
    'TEMPLATE_FOLDER': TEMPLATE_FOLDER,
    'CARDS_BANK_FOLDER': CARDS_FOLDER,
    'AUTH_USERS': AUTH_USERS_CSV,
    'SYSTEM_FULL_DB_CSV': SYSTEM_CSV,
}
for name, val in required_envs.items():
    if not val:
        raise SystemExit(f"{name} must be set in .env")

# Silence werkzeug logs
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.CRITICAL)

# Initialize Flask
def create_app():
    app = Flask(__name__, template_folder=TEMPLATE_FOLDER)
    app.secret_key = APP_SECRET
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    app.config['PREFERRED_URL_SCHEME'] = 'https'

    # import and register routes blueprint
    from routes import bp as main_bp
    app.register_blueprint(main_bp)

    # create aliases for blueprint endpoints without prefix
    from flask import current_app
    for rule in list(app.url_map.iter_rules()):
        if rule.endpoint.startswith(f"{main_bp.name}."):
            short = rule.endpoint.split('.', 1)[1]
            app.add_url_rule(rule.rule, endpoint=short,
                             view_func=app.view_functions[rule.endpoint],
                             methods=rule.methods)

    # attach helpers to app
    app.config.update({
        'CARDS_FOLDER': CARDS_FOLDER,
        'SYSTEM_CSV': SYSTEM_CSV,
        'AUTH_USERS_CSV': AUTH_USERS_CSV,
        'ADMIN_DB': ADMIN_DB,
        'USER_DB': USER_DB,
        'USERS_AUTH_CSV': USERS_AUTH_CSV
    })
    return app

if __name__ == '__main__':
    app = create_app()
    print(f"- - https://nakama.weforks.org/")
    print(f"- - http://localhost:{PORT}/")
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)
    