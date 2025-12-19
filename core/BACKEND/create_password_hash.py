#!/usr/bin/env python3
"""Helper script to generate password hashes for users"""
import sys
sys.dont_write_bytecode = True

from werkzeug.security import generate_password_hash

def create_hash(password):
    """Generate password hash"""
    return generate_password_hash(password, method='scrypt')

if __name__ == '__main__':
    # Create hashes for initial users
    users = [
        ('admin', 'admin123'),
        ('user1', 'user123'),
        ('user2', 'user123'),
    ]

    print("USERNAME,PASSWORD_HASH,USER_TYPE")
    for username, password in users:
        hash_val = create_hash(password)
        user_type = 'ADMIN' if username == 'admin' else 'USER'
        print(f'{username},{hash_val},{user_type}')
