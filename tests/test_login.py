import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from serial_comm.Serial_Comm import SerialComm
from serial_comm.Login_manager import LoginManager

def main():
    serial_comm = SerialComm()
    serial_comm.open()

    login_manager = LoginManager(serial_comm)

    # Optionally set credentials if not set already
    # login_manager.set_credentials('your_username', 'your_password')

    if login_manager.login_sequence():
        print("Logged in successfully!")
    else:
        print("Login failed.")

    serial_comm.close()

if __name__ == "__main__":
    main()
