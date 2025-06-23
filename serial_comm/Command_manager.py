import time
import os
import re
import string

class CommandManager:
    def __init__(self, serial_comm, logs_root='logs'):
        self.serial_comm = serial_comm
        self.logs_root = logs_root

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

        log(f"[*] Running command: {command}")

        folder_path = self._create_log_folder(command)
        output_file = os.path.join(folder_path, 'output.txt')

        try:
            self.serial_comm.write(command + '\n')
            output_lines = []
            end_time = time.time() + timeout

            while time.time() < end_time:
                line = self.serial_comm.read_line()
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

    def parse_dmesg_output(self, dmesg_output):
        boot_time = None
        warnings = []
        errors = []

        boot_time_pattern = re.compile(r'^\[\s*0\.000000\].*', re.MULTILINE)
        warning_pattern = re.compile(r'warning', re.IGNORECASE)
        error_pattern = re.compile(r'error', re.IGNORECASE)

        for line in dmesg_output.splitlines():
            if boot_time is None and boot_time_pattern.match(line):
                boot_time = line.strip()
            if warning_pattern.search(line):
                warnings.append(line.strip())
            if error_pattern.search(line):
                errors.append(line.strip())

        return boot_time, warnings, errors

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
        except Exception as e:
            if output_callback:
                output_callback(f"[Error saving {filename}]: {e}")
