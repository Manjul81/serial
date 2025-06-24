import time
import os
import re
import string

class CommandManager:
    def __init__(self, serial_comm, logs_root='logs'):
        self.serial_comm = serial_comm
        self.logs_root = logs_root
        # Create logs root directory if it doesn't exist
        if not os.path.exists(self.logs_root):
            os.makedirs(self.logs_root, exist_ok=True)

    def _sanitize_command_name(self, command):
        # Keep only alphanumeric and underscore characters for folder name
        valid_chars = f"-_.{string.ascii_letters}{string.digits}"
        sanitized = ''.join(c if c in valid_chars else '_' for c in command.strip().split()[0])
        return sanitized

    def _create_log_folder(self, command):
        command_name = self._sanitize_command_name(command)
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        folder_path = os.path.join(self.logs_root, command_name, timestamp)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    def run_command(self, command, timeout=10, output_callback=None):
        """
        Run command, save output in timestamped folder under logs/<command_name>/.
        Returns captured output string.
        """
        def log(msg):
            if output_callback:
                output_callback(msg)
            else:
                print(msg)  # Print to console if no callback provided

        log(f"[*] Running command: {command}")
        folder_path = self._create_log_folder(command)
        output_file = os.path.join(folder_path, 'output.txt')
        try:
            self.serial_comm.write((command + '\n').encode('utf-8'))  # Ensure encoding
            output_lines = []
            end_time = time.time() + timeout
            while time.time() < end_time:
                line = self.serial_comm.read_line().decode('utf-8', errors='ignore').strip()  # Ensure decoding
                if line:
                    output_lines.append(line)
                    log(line)
                    if any(line.strip().endswith(p) for p in ['$', '#', '>']):
                        break
                else:
                    time.sleep(0.1)
            output_str = '\n'.join(output_lines)
            with open(output_file, 'w') as f:
                f.write(output_str)
            log(f"[*] Output saved to {output_file}")
            return output_str
        except Exception as e:
            log(f"[Error running command '{command}']: {e}")
            return ''

    def save_to_file(self, filename, lines, output_callback=None):
        """
        Save lines or string to a file.
        If filename is not an absolute path, saves to logs root with timestamp folder.
        """
        try:
            # If filename is absolute, save directly
            if os.path.isabs(filename):
                path = filename
            else:
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                folder_path = os.path.join(self.logs_root, 'misc', timestamp)
                os.makedirs(folder_path, exist_ok=True)
                path = os.path.join(folder_path, filename)
            with open(path, 'w') as f:
                if isinstance(lines, list):
                    for line in lines:
                        f.write(line + '\n')
                else:
                    f.write(lines)
            if output_callback:
                output_callback(f"[*] Saved to {path}")
            else:
                print(f"[*] Saved to {path}")
        except Exception as e:
            if output_callback:
                output_callback(f"[Error saving {filename}]: {e}")
            else:
                print(f"[Error saving {filename}]: {e}")

# Example usage (assuming you have a serial_comm object)
# serial_comm = ...  # Your serial communication object
# cmd_manager = CommandManager(serial_comm)
# output = cmd_manager.run_command("your_command")
# print(output)