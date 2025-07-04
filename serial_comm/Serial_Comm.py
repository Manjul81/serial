import serial
import threading
import configparser
import serial.tools.list_ports
import os
class SerialComm:
    

    print("Current working directory:", os.getcwd())
    print("Looking for config file at:", os.path.abspath('config.ini'))

    def __init__(self, config_file='config.ini', timeout=1):
        config = configparser.ConfigParser()
        config.read(config_file)

        # No default values; require both port and baudrate in config
        try:
            if config.has_section('SerialPort'):
                if config.has_option('SerialPort', 'port'):
                    port = config.get('SerialPort', 'port')
                else:
                    raise ValueError("Missing 'port' in [SerialPort] section of config.ini")

                if config.has_option('SerialPort', 'baudrate'):
                    baudrate = config.getint('SerialPort', 'baudrate')
                else:
                    raise ValueError("Missing 'baudrate' in [SerialPort] section of config.ini")
            else:
                raise ValueError("Missing [SerialPort] section in config.ini")
        except ValueError as e:
            raise serial.SerialException(f"Configuration error: {e}")

        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = baudrate
        self.ser.timeout = timeout
        self.lock = threading.Lock()

    def open(self):
        try:
            if not self.ser.is_open:
                self.ser.open()
                print(f"Serial port {self.ser.port} opened at {self.ser.baudrate} baud.")
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")

    def close(self):
        if self.ser.is_open:
            self.ser.close()
            print(f"Serial port {self.ser.port} closed.")

    def write(self, data):
        with self.lock:
            try:
                if self.ser.is_open:
                    self.ser.write(data.encode('utf-8'))
            except serial.SerialTimeoutException as e:
                print(f"Write timeout: {e}")

    def read_line(self):
        with self.lock:
            if self.ser.is_open:
                line = self.ser.readline()
                return line.decode('utf-8', errors='ignore').strip()
            return ''

    def read_all(self):
        with self.lock:
            if self.ser.is_open:
                data = self.ser.read(self.ser.in_waiting or 1)
                return data.decode('utf-8', errors='ignore')
            return ''
