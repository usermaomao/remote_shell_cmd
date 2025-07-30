import os
import stat
import time
import threading
from core.ssh_manager import SSHManager

class FileManager:
    def __init__(self, ssh_manager: SSHManager):
        self.ssh_manager = ssh_manager
        self._sftp_cache = {}  # Cache SFTP connections
        self._cache_lock = threading.Lock()
        self._cache_timeout = 300  # 5 minutes timeout

    def _get_sftp_client(self, connection_name):
        """Get SFTP client with caching for better performance"""
        with self._cache_lock:
            # Check if we have a cached SFTP client
            if connection_name in self._sftp_cache:
                sftp_info = self._sftp_cache[connection_name]
                # Check if cache is still valid
                if time.time() - sftp_info['timestamp'] < self._cache_timeout:
                    try:
                        # Test if connection is still alive
                        sftp_info['client'].listdir('.')
                        return sftp_info['client']
                    except:
                        # Connection is dead, remove from cache
                        try:
                            sftp_info['client'].close()
                        except:
                            pass
                        del self._sftp_cache[connection_name]
                else:
                    # Cache expired, remove it
                    try:
                        sftp_info['client'].close()
                    except:
                        pass
                    del self._sftp_cache[connection_name]

            # Create new SFTP client
            ssh_client = self.ssh_manager.get_client(connection_name)
            if not ssh_client:
                raise ConnectionError(f"Not connected to '{connection_name}'.")

            sftp_client = ssh_client.open_sftp()
            # Cache the new client
            self._sftp_cache[connection_name] = {
                'client': sftp_client,
                'timestamp': time.time()
            }
            return sftp_client

    def _close_cached_sftp(self, connection_name):
        """Close and remove cached SFTP client"""
        with self._cache_lock:
            if connection_name in self._sftp_cache:
                try:
                    self._sftp_cache[connection_name]['client'].close()
                except:
                    pass
                del self._sftp_cache[connection_name]

    def list_directory(self, connection_name, remote_path):
        """List directory contents with performance optimization"""
        sftp = self._get_sftp_client(connection_name)

        # Use cached SFTP connection, don't close it
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

    def download_file(self, connection_name, remote_path, local_path, progress_callback=None):
        """Download file with optimized connection handling and resume support"""
        sftp = self._get_sftp_client(connection_name)

        # Check if partial file exists for resume
        if os.path.exists(local_path + '.part'):
            # Get remote file size
            remote_stat = sftp.stat(remote_path)
            remote_size = remote_stat.st_size

            # Get local partial file size
            local_size = os.path.getsize(local_path + '.part')

            if local_size < remote_size:
                # Resume download
                with open(local_path + '.part', 'ab') as local_file:
                    with sftp.open(remote_path, 'rb') as remote_file:
                        remote_file.seek(local_size)
                        chunk_size = 32768  # 32KB chunks for better performance
                        bytes_transferred = local_size

                        while bytes_transferred < remote_size:
                            chunk = remote_file.read(chunk_size)
                            if not chunk:
                                break
                            local_file.write(chunk)
                            bytes_transferred += len(chunk)

                            if progress_callback:
                                progress_callback(bytes_transferred, remote_size)

                # Rename completed file
                os.rename(local_path + '.part', local_path)
                return

        # Regular download with progress tracking
        try:
            # Get file size for progress calculation
            remote_stat = sftp.stat(remote_path)
            file_size = remote_stat.st_size

            # Use temporary file for atomic operation
            temp_path = local_path + '.part'

            def enhanced_progress_callback(transferred, total):
                if progress_callback:
                    progress_callback(transferred, file_size)

            sftp.get(remote_path, temp_path, callback=enhanced_progress_callback)

            # Rename to final name when complete
            os.rename(temp_path, local_path)

        except Exception as e:
            # Clean up partial file on error
            if os.path.exists(local_path + '.part'):
                os.remove(local_path + '.part')
            raise e

    def upload_file(self, connection_name, local_path, remote_path, progress_callback=None):
        """Upload file with optimized connection handling and resume support"""
        sftp = self._get_sftp_client(connection_name)

        # Get local file size
        local_size = os.path.getsize(local_path)

        # Check if partial remote file exists for resume
        temp_remote_path = remote_path + '.part'
        remote_size = 0

        try:
            remote_stat = sftp.stat(temp_remote_path)
            remote_size = remote_stat.st_size
        except FileNotFoundError:
            remote_size = 0

        if remote_size > 0 and remote_size < local_size:
            # Resume upload
            with open(local_path, 'rb') as local_file:
                with sftp.open(temp_remote_path, 'ab') as remote_file:
                    local_file.seek(remote_size)
                    chunk_size = 32768  # 32KB chunks
                    bytes_transferred = remote_size

                    while bytes_transferred < local_size:
                        chunk = local_file.read(chunk_size)
                        if not chunk:
                            break
                        remote_file.write(chunk)
                        bytes_transferred += len(chunk)

                        if progress_callback:
                            progress_callback(bytes_transferred, local_size)

            # Rename completed file
            sftp.rename(temp_remote_path, remote_path)
            return

        # Regular upload with progress tracking
        try:
            def enhanced_progress_callback(transferred, total):
                if progress_callback:
                    progress_callback(transferred, local_size)

            sftp.put(local_path, temp_remote_path, callback=enhanced_progress_callback)

            # Rename to final name when complete
            sftp.rename(temp_remote_path, remote_path)

        except Exception as e:
            # Clean up partial file on error
            try:
                sftp.remove(temp_remote_path)
            except:
                pass
            raise e

    def delete_file(self, connection_name, remote_path):
        """Delete file with optimized connection handling"""
        sftp = self._get_sftp_client(connection_name)
        sftp.remove(remote_path)

    def delete_directory(self, connection_name, remote_path):
        """Delete directory with optimized connection handling"""
        sftp = self._get_sftp_client(connection_name)
        # This is a simple implementation. A robust one would recursively delete contents.
        sftp.rmdir(remote_path)

    def rename_file(self, connection_name, old_remote_path, new_remote_path):
        """Rename file with optimized connection handling"""
        sftp = self._get_sftp_client(connection_name)
        sftp.rename(old_remote_path, new_remote_path)

    def create_directory(self, connection_name, remote_path):
        """Create directory with optimized connection handling"""
        sftp = self._get_sftp_client(connection_name)
        sftp.mkdir(remote_path)

    def cleanup_connections(self):
        """Clean up all cached SFTP connections"""
        with self._cache_lock:
            for connection_name in list(self._sftp_cache.keys()):
                try:
                    self._sftp_cache[connection_name]['client'].close()
                except:
                    pass
            self._sftp_cache.clear()
