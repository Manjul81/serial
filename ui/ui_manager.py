import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
import threading
import time

from serial_comm.Serial_Comm import SerialComm
from serial_comm.Login_manager import LoginManager
from serial_comm.Command_manager import CommandManager  # Updated class name

class SerialUI(tk.Tk):
    def __init__(self, serial_comm):
        super().__init__()
        self.title("Serial Communication UI")
        self.geometry("700x500")
        self.serial_comm = serial_comm

        self.login_manager = LoginManager(serial_comm)
        self.command_manager = CommandManager(serial_comm)  # Updated instance name

        self.text_area = scrolledtext.ScrolledText(self, state='disabled', wrap='word')
        self.text_area.pack(expand=True, fill='both', padx=5, pady=5)

        self.entry = tk.Entry(self)
        self.entry.pack(fill='x', padx=5)
        self.entry.bind('<Return>', self.send_command)

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(fill='x', padx=5, pady=5)

        self.send_button = tk.Button(self.button_frame, text="Send Command", command=self.send_command)
        self.send_button.pack(side='left', padx=5)

        self.login_button = tk.Button(self.button_frame, text="Login", command=self.threaded_login)
        self.login_button.pack(side='left', padx=5)

        self.dmesg_button = tk.Button(self.button_frame, text="Run dmesg", command=self.threaded_run_dmesg, state='disabled')
        self.dmesg_button.pack(side='left', padx=5)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.running = True

        self.read_thread = threading.Thread(target=self.read_from_serial, daemon=True)
        self.read_thread.start()

        self.logged_in = False

    def append_text(self, text):
        self.text_area.configure(state='normal')
        self.text_area.insert(tk.END, text + '\n')
        self.text_area.configure(state='disabled')
        self.text_area.see(tk.END)

    def send_command(self, event=None):
        cmd = self.entry.get()
        if cmd:
            try:
                self.serial_comm.write(cmd + '\n')
                self.append_text(f"> {cmd}")
                self.entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send command: {e}")

    def read_from_serial(self):
        while self.running:
            try:
                line = self.serial_comm.read_line()
                if line:
                    self.append_text(line)
                else:
                    time.sleep(0.1)
            except Exception as e:
                self.append_text(f"[Error reading serial]: {e}")
                time.sleep(1)

    def on_close(self):
        self.running = False
        try:
            self.serial_comm.close()
        except:
            pass
        self.destroy()

    def threaded_login(self):
        login_id = simpledialog.askstring("Login ID", "Enter login ID:", parent=self)
        if login_id is None:
            return
        password = simpledialog.askstring("Password", "Enter password:", show='*', parent=self)
        if password is None:
            return

        def login_task():
            try:
                self.login_button.config(state='disabled')
                self.append_text("[*] Storing credentials securely...")
                self.login_manager.set_credentials(login_id, password)
                self.append_text("[*] Attempting login...")
                success = self.login_manager.login_sequence(output_callback=self.append_text)
                self.logged_in = success
                if success:
                    messagebox.showinfo("Login", "LOGIN SUCCESS")
                    self.dmesg_button.config(state='normal')
                else:
                    messagebox.showerror("Login", "LOGIN FAILED")
            finally:
                self.login_button.config(state='normal')

        threading.Thread(target=login_task, daemon=True).start()

    def threaded_run_dmesg(self):
        if not self.logged_in:
            messagebox.showwarning("Warning", "Please login first!")
            return

        def dmesg_task():
            self.dmesg_button.config(state='disabled')
            # Run 'dmesg' command using generic command runner
            dmesg_output, folder_path = self.command_manager.run_command('dmesg', output_callback=self.append_text, timeout=15)
            if not dmesg_output.strip():
                self.append_text("[!] No dmesg output received.")
                self.dmesg_button.config(state='normal')
                return

            # Save parsed logs inside the timestamped folder
            boot_time, warnings, errors = self.command_manager.parse_dmesg_output(dmesg_output)

            # Save boot time log
            boot_time_file = folder_path + '/boot_time.txt'
            try:
                with open(boot_time_file, 'w') as f:
                    if boot_time:
                        f.write(boot_time + '\n')
                    else:
                        f.write('Boot time not found.\n')
                self.append_text(f"[*] Saved boot time to {boot_time_file}")
            except Exception as e:
                self.append_text(f"[Error saving boot time]: {e}")

            self.append_text(f"[*] Boot time line: {boot_time if boot_time else 'Not found'}")
            self.append_text(f"[*] Total warnings: {len(warnings)}")
            self.append_text(f"[*] Total errors: {len(errors)}")

            self.command_manager.save_to_file(folder_path + '/dmesg_warnings.txt', warnings, output_callback=self.append_text)
            self.command_manager.save_to_file(folder_path + '/dmesg_errors.txt', errors, output_callback=self.append_text)

            messagebox.showinfo("dmesg Parsing", f"Boot time: {boot_time if boot_time else 'Not found'}\n"
                                                 f"Warnings: {len(warnings)}\nErrors: {len(errors)}")
            self.dmesg_button.config(state='normal')

        threading.Thread(target=dmesg_task, daemon=True).start()

def main():
    root = tk.Tk()
    root.withdraw()

    port = simpledialog.askstring("Serial Port", "Enter serial port (e.g. /dev/ttyUSB0):")
    if not port:
        messagebox.showerror("Error", "Serial port is required.")
        return

    baudrate_str = simpledialog.askstring("Baudrate", "Enter baudrate (default 9600):")
    baudrate = 115200
    if baudrate_str and baudrate_str.isdigit():
        baudrate = int(baudrate_str)

    root.destroy()

    try:
        serial_comm = SerialComm(port, baudrate=baudrate, timeout=1)
        serial_comm.open()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open serial port: {e}")
        return

    app = SerialUI(serial_comm)
    app.mainloop()

if __name__ == '__main__':
    main()
