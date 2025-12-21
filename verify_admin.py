from run import create_app
from routes import determine_user_is_admin

app = create_app()
with app.app_context():
    print(f"Is 'admin' admin? {determine_user_is_admin('admin')}")
    print(f"Is 'user1' admin? {determine_user_is_admin('user1')}")
    print(f"Is 'user2' admin? {determine_user_is_admin('user2')}")
