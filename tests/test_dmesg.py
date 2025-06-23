import sys
import os
import time

# Adjust path to import your modules properly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'serial_comm')))

from serial_comm.Serial_Comm import SerialComm
from serial_comm.Login_manager import LoginManager
from serial_comm.Command_manager import CommandManager  # Updated name from dmesg_manager

def main():
    serial_port = 'COM5'  # Change as needed
    baudrate = 115200
    command = 'dmesg'  # Command to run

    serial_comm = SerialComm(serial_port, baudrate=baudrate, timeout=1)
    try:
        serial_comm.open()
    except Exception as e:
        print(f"Failed to open serial port: {e}")
        sys.exit(1)

    login_manager = LoginManager(serial_comm)
    command_manager = CommandManager(serial_comm)

    # Check login status before running command
    if not login_manager.is_logged_in():
        print("Not logged in. Attempting login...")
        if not login_manager.login_sequence(output_callback=print):
            print("LOGIN FAILED")
            serial_comm.close()
            sys.exit(1)
    else:
        print("Already logged in.")

    print(f"[*] Running command: {command}")
    
    # Run command and get output and folder path
    output, folder_path = command_manager.run_command(command, timeout=15, output_callback=print)

    if not output.strip():
        print("No output received from command.")
        serial_comm.close()
        sys.exit(1)

    # Parse dmesg output
    boot_time, warnings, errors = command_manager.parse_dmesg_output(output)

    # Save boot time log
    boot_time_file = os.path.join(folder_path, 'boot_time.txt')
    try:
        with open(boot_time_file, 'w') as f:
            if boot_time:
                f.write(boot_time + '\n')
            else:
                f.write('Boot time not found.\n')
        print(f"[*] Saved boot time to {boot_time_file}")
    except Exception as e:
        print(f"[Error saving boot time]: {e}")

    # Save warnings and errors logs
    command_manager.save_to_file(os.path.join(folder_path, 'warnings.txt'), warnings, output_callback=print)
    command_manager.save_to_file(os.path.join(folder_path, 'errors.txt'), errors, output_callback=print)

    serial_comm.close()
    sys.exit(0)

if __name__ == '__main__':
    main()
