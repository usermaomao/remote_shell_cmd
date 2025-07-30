import paramiko
import os
import json
import stat
import time
import threading
from core.credentials_manager import CredentialsManager, load_or_generate_key

CONFIG_FILE = "connections.json"

class SSHManager:
    def __init__(self):
        self.key = load_or_generate_key()
        self.credentials_manager = CredentialsManager(self.key)
        self.connections = self.load_connections()
        self.active_clients = {}  # {conn_name: paramiko.SSHClient}
        self.client_timestamps = {}  # Track connection times for cleanup
        self.connection_lock = threading.Lock()  # Thread safety
        self.connection_timeout = 300  # 5 minutes timeout for idle connections

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

    def connect(self, name, max_retries=3, timeout=5):
        """Connect with performance optimizations and retry logic"""
        with self.connection_lock:
            # Check if we have an active connection
            if name in self.active_clients:
                client = self.active_clients[name]
                # Test if connection is still alive
                try:
                    transport = client.get_transport()
                    if transport and transport.is_active():
                        # Update timestamp
                        self.client_timestamps[name] = time.time()
                        return client
                    else:
                        # Connection is dead, remove it
                        self._cleanup_connection(name)
                except:
                    self._cleanup_connection(name)

            conn_data = self.get_connection(name)
            if not conn_data:
                raise ValueError(f"Connection '{name}' not found.")

            # Retry connection with exponential backoff
            last_exception = None
            for attempt in range(max_retries):
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
                            timeout=timeout,  # Connection timeout
                            key_filename=key_path
                        )
                    else: # Password authentication
                        client.connect(
                            hostname=conn_data['host'],
                            port=conn_data.get('port', 22),
                            username=conn_data['user'],
                            password=conn_data.get('password'),
                            timeout=timeout  # Connection timeout
                        )

                    # Connection successful
                    self.active_clients[name] = client
                    self.client_timestamps[name] = time.time()
                    return client

                except Exception as e:
                    last_exception = e
                    client.close()

                    # Exponential backoff for retries
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 0.5  # 0.5, 1, 2 seconds
                        time.sleep(wait_time)

            # All retries failed
            raise last_exception or Exception(f"Failed to connect to {name} after {max_retries} attempts")

    def _cleanup_connection(self, name):
        """Clean up a dead connection"""
        if name in self.active_clients:
            try:
                self.active_clients[name].close()
            except:
                pass
            del self.active_clients[name]

        if name in self.client_timestamps:
            del self.client_timestamps[name]

    def cleanup_idle_connections(self):
        """Clean up idle connections to free resources"""
        current_time = time.time()
        idle_connections = []

        with self.connection_lock:
            for name, timestamp in self.client_timestamps.items():
                if current_time - timestamp > self.connection_timeout:
                    idle_connections.append(name)

            for name in idle_connections:
                self._cleanup_connection(name)

    def disconnect(self, name):
        """Disconnect with proper cleanup"""
        with self.connection_lock:
            self._cleanup_connection(name)

    def get_client(self, name):
        """Get client with connection health check"""
        with self.connection_lock:
            if name in self.active_clients:
                client = self.active_clients[name]
                try:
                    transport = client.get_transport()
                    if transport and transport.is_active():
                        # Update timestamp for active use
                        self.client_timestamps[name] = time.time()
                        return client
                    else:
                        # Connection is dead, clean it up
                        self._cleanup_connection(name)
                        return None
                except:
                    self._cleanup_connection(name)
                    return None
            return None

    def disconnect_all(self):
        """Disconnect all active connections"""
        with self.connection_lock:
            for name in list(self.active_clients.keys()):
                self._cleanup_connection(name)

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
