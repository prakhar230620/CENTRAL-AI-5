import json
import uuid
import os
from cryptography.fernet import Fernet

AI_DATABASE_FILE = 'ai_database.json'
KEY_FILE = 'encryption_key.key'

def get_encryption_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as key_file:
            key_file.write(key)
    else:
        with open(KEY_FILE, 'rb') as key_file:
            key = key_file.read()
    return Fernet(key)

def encrypt_sensitive_data(data):
    fernet = get_encryption_key()
    return fernet.encrypt(data.encode()).decode()

def decrypt_sensitive_data(encrypted_data):
    fernet = get_encryption_key()
    return fernet.decrypt(encrypted_data.encode()).decode()

def load_ai_database():
    try:
        with open(AI_DATABASE_FILE, 'r') as f:
            database = json.load(f)
        for ai_id, ai_info in database.items():
            if 'api_key' in ai_info['details']:
                ai_info['details']['api_key'] = decrypt_sensitive_data(ai_info['details']['api_key'])
        return database
    except FileNotFoundError:
        return {}

def save_ai_database(database):
    database_copy = database.copy()
    for ai_id, ai_info in database_copy.items():
        if 'api_key' in ai_info['details']:
            ai_info['details']['api_key'] = encrypt_sensitive_data(ai_info['details']['api_key'])
    with open(AI_DATABASE_FILE, 'w') as f:
        json.dump(database_copy, f, indent=2)

def add_ai(name, ai_type, details):
    database = load_ai_database()
    ai_id = str(uuid.uuid4())
    database[ai_id] = {
        'name': name,
        'type': ai_type,
        'details': details
    }
    save_ai_database(database)
    return ai_id

def update_ai(ai_id, details):
    database = load_ai_database()
    if ai_id in database:
        database[ai_id]['details'].update(details)
        save_ai_database(database)
        return True
    return False

def remove_ai(ai_id):
    database = load_ai_database()
    if ai_id in database:
        del database[ai_id]
        save_ai_database(database)
        return True
    return False

def get_ai(ai_id):
    database = load_ai_database()
    return database.get(ai_id)

def list_ais():
    database = load_ai_database()
    return [{'id': k, **v} for k, v in database.items()]