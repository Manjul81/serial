import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from serial_comm.Serial_Comm import SerialComm
from serial_comm.Command_manager import CommandManager

def main():
    serial_comm = SerialComm()
    serial_comm.open()

    cmd_mgr = CommandManager(serial_comm)

    try:
        while True:
            command = input("Enter command to send (or 'exit' to quit): ").strip()
            if command.lower() == 'exit':
                print("Exiting.")
                break
            if not command:
                continue  # skip empty input

            output = cmd_mgr.run_command(command, timeout=10)
            print(f"Output:\n{output}\n")

    finally:
        serial_comm.close()

if __name__ == "__main__":
    main()
