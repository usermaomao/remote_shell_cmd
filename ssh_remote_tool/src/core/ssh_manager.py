import paramiko
import os
import json
import stat
from core.credentials_manager import CredentialsManager, load_or_generate_key

CONFIG_FILE = "connections.json"

class SSHManager:
    def __init__(self):
        self.key = load_or_generate_key()
        self.credentials_manager = CredentialsManager(self.key)
        self.connections = self.load_connections()
        self.active_clients = {}  # {conn_name: paramiko.SSHClient}

    def load_connections(self):
        if not os.path.exists(CONFIG_FILE):
            return {}
        with open(CONFIG_FILE, "r") as f:
            encrypted_conns = json.load(f)
            connections = {}
            for name, data in encrypted_conns.items():
                connections[name] = data
                if 'password' in data and data['password']:
                    connections[name]['password'] = self.credentials_manager.decrypt_password(data['password'])
            return connections

    def save_connections(self):
        encrypted_conns = {}
        for name, data in self.connections.items():
            encrypted_conns[name] = data.copy()
            if 'password' in data and data['password']:
                encrypted_conns[name]['password'] = self.credentials_manager.encrypt_password(data['password'])

        with open(CONFIG_FILE, "w") as f:
            json.dump(encrypted_conns, f, indent=4)

    def add_connection(self, conn_data):
        """conn_data should be a dictionary with connection details."""
        name = conn_data.get("name")
        if not name:
            raise ValueError("Connection name is required.")
        self.connections[name] = conn_data
        self.save_connections()

    def remove_connection(self, name):
        if name in self.connections:
            del self.connections[name]
            self.save_connections()
            if name in self.active_clients:
                self.disconnect(name)

    def get_connection(self, name):
        return self.connections.get(name)

    def get_all_connections(self):
        return self.connections

    def connect(self, name):
        if name in self.active_clients:
            return self.active_clients[name]

        conn_data = self.get_connection(name)
        if not conn_data:
            raise ValueError(f"Connection '{name}' not found.")

        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            auth_method = conn_data.get('auth_method', 'password')

            if auth_method == 'key':
                key_path = conn_data.get('key_path')
                if not key_path or not os.path.exists(key_path):
                    raise ValueError(f"SSH key not found at path: {key_path}")

                # Validate key file permissions (Unix-like systems)
                if os.name != 'nt':  # Not Windows
                    self._validate_key_permissions(key_path)

                client.connect(
                    hostname=conn_data['host'],
                    port=conn_data.get('port', 22),
                    username=conn_data['user'],
                    key_filename=key_path,
                    timeout=10
                )
            else: # Password authentication
                client.connect(
                    hostname=conn_data['host'],
                    port=conn_data.get('port', 22),
                    username=conn_data['user'],
                    password=conn_data.get('password'),
                    timeout=10
                )

            self.active_clients[name] = client
            return client
        except Exception as e:
            # In a real app, this would emit a signal to the UI
            print(f"Failed to connect to {name}: {e}")
            raise

    def disconnect(self, name):
        if name in self.active_clients:
            client = self.active_clients.pop(name)
            client.close()

    def get_client(self, name):
        return self.active_clients.get(name)

    def _validate_key_permissions(self, key_path):
        """Validate SSH key file permissions (Unix-like systems only)"""
        try:
            file_stat = os.stat(key_path)
            file_mode = stat.filemode(file_stat.st_mode)

            # Check if file is readable by owner only (600 or 400)
            permissions = file_stat.st_mode & 0o777
            if permissions not in [0o600, 0o400]:
                # Try to fix permissions
                try:
                    os.chmod(key_path, 0o600)
                    print(f"Fixed SSH key permissions for {key_path}")
                except OSError:
                    raise ValueError(
                        f"SSH key file {key_path} has insecure permissions ({oct(permissions)}). "
                        f"Please set permissions to 600 (owner read/write only)."
                    )
        except OSError as e:
            raise ValueError(f"Cannot access SSH key file {key_path}: {e}")
