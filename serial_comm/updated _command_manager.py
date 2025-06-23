import time
import re
import os
import logging
from datetime import datetime

class CommandManager:
    def __init__(self, serial_comm, logs_dir='logs'):
        self.serial_comm = serial_comm
        self.logs_dir = logs_dir
        os.makedirs(self.logs_dir, exist_ok=True)
        self.logger = None

    def _setup_logger(self, command):
        """
        Sets up a logger that writes to a timestamped log file per command.
        """
        # Create a safe filename based on command and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_command = "".join(c if c.isalnum() else "_" for c in command.strip().split()[0])
        log_filename = os.path.join(self.logs_dir, f"{safe_command}_{timestamp}.log")

        # Create logger
        logger = logging.getLogger(f"CommandLogger_{timestamp}")
        logger.setLevel(logging.DEBUG)

        # Remove any existing handlers
        if logger.hasHandlers():
            logger.handlers.clear()

        # Create file handler
        fh = logging.FileHandler(log_filename, mode='w', encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        self.logger = logger
        return log_filename

    def run_command(self, command, timeout=10, output_callback=None, prompt_chars=None):
        """
        Send a command and capture its output until prompt or timeout.
        Logs all output to a timestamped file in logs_dir.

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

            log(f"[*] Command output saved to {log_filename}")
            return '\n'.join(output_lines)
        except Exception as e:
            log(f"[Error running command '{command}']: {e}", level=logging.ERROR)
            return ''

    def parse_output(self, output, patterns=None):
        """
        Generic parser to find lines matching given patterns.

        Args:
            output (str): The command output to parse.
            patterns (dict): Optional dictionary where keys are labels and values are regex patterns (compiled or strings).

        Returns:
            dict: Dictionary with labels as keys and lists of matching lines as values.
        """
        if not patterns:
            return {}

        results = {label: [] for label in patterns}

        for line in output.splitlines():
            for label, pattern in patterns.items():
                # Compile pattern if needed
                if isinstance(pattern, str):
                    regex = re.compile(pattern, re.IGNORECASE)
                else:
                    regex = pattern

                if regex.search(line):
                    results[label].append(line.strip())

        return results

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
