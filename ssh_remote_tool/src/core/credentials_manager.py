import os
import json
from cryptography.fernet import Fernet

# WARNING: In a real application, this key should be stored securely,
# for example, in the system's keychain, not hardcoded.
# For this project, we'll generate it if it doesn't exist.
KEY_FILE = "secret.key"

def load_or_generate_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        return key

class CredentialsManager:
    def __init__(self, key):
        self.fernet = Fernet(key)

    def encrypt_password(self, password):
        if not password:
            return None
        return self.fernet.encrypt(password.encode()).decode()

    def decrypt_password(self, encrypted_password):
        if not encrypted_password:
            return None
        return self.fernet.decrypt(encrypted_password.encode()).decode()
