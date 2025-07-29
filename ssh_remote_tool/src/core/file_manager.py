import os
import stat
from .ssh_manager import SSHManager

class FileManager:
    def __init__(self, ssh_manager: SSHManager):
        self.ssh_manager = ssh_manager

    def _get_sftp_client(self, connection_name):
        ssh_client = self.ssh_manager.get_client(connection_name)
        if not ssh_client:
            raise ConnectionError(f"Not connected to '{connection_name}'.")
        return ssh_client.open_sftp()

    def list_directory(self, connection_name, remote_path):
        sftp = self._get_sftp_client(connection_name)
        try:
            files_attrs = sftp.listdir_attr(remote_path)
            files = []
            for attr in files_attrs:
                is_dir = stat.S_ISDIR(attr.st_mode)
                files.append({
                    "name": attr.filename,
                    "size": attr.st_size,
                    "mtime": attr.st_mtime,
                    "permissions": stat.filemode(attr.st_mode),
                    "is_dir": is_dir,
                })
            # Sort with directories first, then by name
            files.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
            return files
        finally:
            sftp.close()

    def download_file(self, connection_name, remote_path, local_path, progress_callback=None):
        sftp = self._get_sftp_client(connection_name)
        try:
            # Simple download for now. Resume logic can be added here.
            sftp.get(remote_path, local_path, callback=progress_callback)
        finally:
            sftp.close()

    def upload_file(self, connection_name, local_path, remote_path, progress_callback=None):
        sftp = self._get_sftp_client(connection_name)
        try:
            # Simple upload for now. Resume logic can be added here.
            sftp.put(local_path, remote_path, callback=progress_callback)
        finally:
            sftp.close()

    def delete_file(self, connection_name, remote_path):
        sftp = self._get_sftp_client(connection_name)
        try:
            sftp.remove(remote_path)
        finally:
            sftp.close()

    def delete_directory(self, connection_name, remote_path):
        sftp = self._get_sftp_client(connection_name)
        try:
            # This is a simple implementation. A robust one would recursively delete contents.
            sftp.rmdir(remote_path)
        finally:
            sftp.close()

    def rename_file(self, connection_name, old_remote_path, new_remote_path):
        sftp = self._get_sftp_client(connection_name)
        try:
            sftp.rename(old_remote_path, new_remote_path)
        finally:
            sftp.close()

    def create_directory(self, connection_name, remote_path):
        sftp = self._get_sftp_client(connection_name)
        try:
            sftp.mkdir(remote_path)
        finally:
            sftp.close()
