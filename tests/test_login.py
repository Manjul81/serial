import sys
import os
import time

# Adjust path to import your modules properly
#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'serial_comm')))

#from serial_comm.Serial_Comm import SerialComm
import SerialComm
from serial_comm.Login_manager import LoginManager

def main():
    serial_port = 'COM5'  # Change as needed
    baudrate = 115200

    serial_comm = SerialComm(serial_port, baudrate=baudrate, timeout=1)
    try:
        serial_comm.open()
    except Exception as e:
        print(f"Failed to open serial port: {e}")
        sys.exit(1)

    login_manager = LoginManager(serial_comm)

    # Check if already logged in
    if login_manager.is_logged_in():
        print("Already logged in.")
        success = True
    else:
        print("Not logged in. Attempting login...")
        success = login_manager.login_sequence(output_callback=print)

    if success:
        print("LOGIN SUCCESS")
        exit_code = 0
    else:
        print("LOGIN FAILED")
        exit_code = 1

    serial_comm.close()
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
