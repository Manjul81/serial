import time
import re
import os
import logging
from datetime import datetime

class CommandManager:
    def __init__(self, serial_comm, logs_dir=None):
        self.serial_comm = serial_comm

        if logs_dir is None:
            # Get directory of this file (serial_comm folder)
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # Go one level up to 'serial' folder
            project_root = os.path.abspath(os.path.join(base_dir, '..'))
            # Set logs_dir to 'serial/logs'
            logs_dir = os.path.join(project_root, 'logs')

        self.logs_dir = logs_dir
        os.makedirs(self.logs_dir, exist_ok=True)
        self.logger = None


    def _setup_logger(self, command):
        """
        Sets up a logger that writes to a log file named after the command.
        The log file is appended to on each run (no timestamp in filename).
        """
        # Create a safe filename based on the full command (sanitized)
        safe_command = re.sub(r'\W+', '_', command.strip())
        log_filename = os.path.join(self.logs_dir, f"{safe_command}.log")

        # Create logger
        logger = logging.getLogger(f"CommandLogger_{safe_command}")
        logger.setLevel(logging.DEBUG)

        # Remove any existing handlers
        if logger.hasHandlers():
            logger.handlers.clear()

        # Create file handler in append mode
        fh = logging.FileHandler(log_filename, mode='a', encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        self.logger = logger
        return log_filename

    def run_command(self, command, timeout=10, output_callback=None, prompt_chars=None):
        """
        Send a command and capture its output until prompt or timeout.
        Logs all output to a file named after the command (appended).

        Args:
            command (str): The command to send.
            timeout (int): Timeout in seconds to wait for command completion.
            output_callback (callable): Optional function to receive output lines.
            prompt_chars (list or tuple): Characters indicating command prompt (default: ['$', '#', '>']).

        Returns:
            str: The full output captured from the command.
        """
        if prompt_chars is None:
            prompt_chars = ['$', '#', '>']

        log_filename = self._setup_logger(command)

        def log(msg, level=logging.INFO):
            if self.logger:
                self.logger.log(level, msg)
            if output_callback:
                output_callback(msg)

        log(f"[*] Sending command: {command}")
        try:
            self.serial_comm.write(command + '\n')
            output_lines = []
            end_time = time.time() + timeout

            while time.time() < end_time:
                line = self.serial_comm.read_line()
                if line:
                    output_lines.append(line)
                    log(line)
                    # Check if line ends with any prompt character
                    if any(line.strip().endswith(p) for p in prompt_chars):
                        break
                else:
                    time.sleep(0.1)

            #log(f"[*] Command output appended to {log_filename}")
            return '\n'.join(output_lines)
        except Exception as e:
            log(f"[Error running command '{command}']: {e}", level=logging.ERROR)
            return ''

    def save_to_file(self, filename, content, output_callback=None):
        """
        Save content (string or list of strings) to a file.

        Args:
            filename (str): Path to file.
            content (str or list): Content to save.
            output_callback (callable): Optional function to report success or errors.
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                if isinstance(content, list):
                    for line in content:
                        f.write(line + '\n')
                else:
                    f.write(content)
            if output_callback:
                output_callback(f"[*] Saved to {filename}")
        except Exception as e:
            if output_callback:
                output_callback(f"[Error saving {filename}]: {e}")

    def get_last_n_lines(self, file_path, n=10, timeout=5, output_callback=None):
        """
        Retrieve the last N lines of a file on the remote device via serial command.

        Args:
            file_path (str): Absolute path of the file on the device.
            n (int): Number of lines to retrieve from the end of the file.
            timeout (int): Timeout in seconds for the command execution.
            output_callback (callable): Optional function to receive output lines.

        Returns:
            str: Last N lines of the file as a string.
        """
        command = f"tail -n {n} {file_path}"
        output = self.run_command(command, timeout=timeout, output_callback=output_callback)

        # Prepare safe filename based on file path and number of lines
        safe_path = re.sub(r'\W+', '_', file_path.strip('/'))
        log_filename = os.path.join(self.logs_dir, f"{safe_path}_last_{n}_lines.log")

        # Save output to file
        try:
            with open(log_filename, 'w', encoding='utf-8') as f:
                f.write(output)
            if output_callback:
                output_callback(f"[*] Saved last {n} lines of '{file_path}' to {log_filename}")
        except Exception as e:
            if output_callback:
                output_callback(f"[Error saving log file]: {e}")

        return output