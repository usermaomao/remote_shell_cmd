import threading
from .ssh_manager import SSHManager

class ScriptExecutor:
    def __init__(self, ssh_manager: SSHManager):
        self.ssh_manager = ssh_manager
        self.active_channels = {}  # {connection_name: channel}

    def execute_script(self, connection_name, script_content, exec_dir=".", params="", output_callback=None):
        client = self.ssh_manager.get_client(connection_name)
        if not client:
            raise ConnectionError(f"Not connected to '{connection_name}'.")

        # Construct the full command
        command = f"cd {exec_dir} && {script_content} {params}\n"

        # Open a new channel for the execution
        channel = client.invoke_shell()
        self.active_channels[connection_name] = channel

        # Function to read from the channel
        def read_output():
            try:
                while not channel.closed:
                    if channel.recv_ready():
                        stdout = channel.recv(4096).decode('utf-8', errors='ignore')
                        if output_callback:
                            output_callback(stdout, 'stdout')
                    if channel.recv_stderr_ready():
                        stderr = channel.recv_stderr(4096).decode('utf-8', errors='ignore')
                        if output_callback:
                            output_callback(stderr, 'stderr')
                    if channel.exit_status_ready():
                        break
                if output_callback:
                    output_callback("\n--- Script finished ---", 'info')
            except Exception as e:
                if output_callback:
                    output_callback(f"\n--- ERROR: {e} ---", 'stderr')
            finally:
                self.terminate(connection_name)

        # Start reading output in a separate thread
        thread = threading.Thread(target=read_output, daemon=True)
        thread.start()

        # Send the command to be executed
        channel.sendall(command)

    def terminate(self, connection_name):
        if connection_name in self.active_channels:
            channel = self.active_channels.pop(connection_name)
            if not channel.closed:
                channel.close()
