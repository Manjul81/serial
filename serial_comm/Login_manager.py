import time
import keyring

class LoginManager:
    def __init__(self, serial_comm, service_name='serial_device'):
        self.serial_comm = serial_comm
        self.service_name = service_name
        self.login_id = None
        self.password = None
        self.logged_in = False
        self._load_credentials()

    def _load_credentials(self):
        self.login_id = keyring.get_password(self.service_name, 'login_id')
        self.password = keyring.get_password(self.service_name, 'password')

    def set_credentials(self, login_id, password):
        """Store credentials securely in keyring and update internal state."""
        keyring.set_password(self.service_name, 'login_id', login_id)
        keyring.set_password(self.service_name, 'password', password)
        self.login_id = login_id
        self.password = password

    def is_logged_in(self):
        """Return True if login was successful previously, else False."""
        return self.logged_in

    def login_sequence(self, timeout=15, output_callback=None):
        """Perform login using stored credentials, no arguments needed."""
        def log(msg):
            if output_callback:
                output_callback(msg)
            else:
                print(msg)

        if not self.login_id or not self.password:
            log("[Error] Login credentials not set in keyring.")
            self.logged_in = False
            return False

        log("[*] Starting login sequence...")
        try:
            self.serial_comm.write('\n')
            time.sleep(0.5)
            end_time = time.time() + timeout

            while time.time() < end_time:
                line = self.serial_comm.read_line()
                if line:
                    log(line)
                    if 'login:' in line.lower() or 'username:' in line.lower():
                        self.serial_comm.write(self.login_id + '\n')
                        log(f"> {self.login_id}")
                        time.sleep(0.5)
                    elif 'password:' in line.lower():
                        self.serial_comm.write(self.password + '\n')
                        log("> [password entered]")
                        time.sleep(1)
                    elif any(prompt in line for prompt in ['$', '#', '>']):
                        log("[*] Login successful!")
                        self.logged_in = True
                        return True
                else:
                    time.sleep(0.1)
            log("[!] Login timed out or failed.")
            self.logged_in = False
            return False
        except Exception as e:
            log(f"[Error during login]: {e}")
            self.logged_in = False
            return False
