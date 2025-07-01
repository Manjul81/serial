import serial
import threading
import configparser
import serial.tools.list_ports


class SerialComm:
    def __init__(self, config_file='config.ini', timeout=1):
        config = configparser.ConfigParser()
        config.read(config_file)

        default_port = None  # We'll try to pick from available ports if not specified
        default_baudrate = 115200

        # Get baudrate from config or use default
        try:
            if config.has_section('SerialPort') and config.has_option('SerialPort', 'baudrate'):
                baudrate = config.getint('SerialPort', 'baudrate')
            else:
                baudrate = default_baudrate
        except ValueError:
            print("Invalid baudrate in config; using default.")
            baudrate = default_baudrate

        # Get port from config if available
        if config.has_section('SerialPort') and config.has_option('SerialPort', 'port'):
            port = config.get('SerialPort', 'port')
        else:
            port = default_port

        # List available COM ports
        available_ports = self.list_com_ports()
        print(f"Available COM ports: {available_ports}")

        # If no port specified or specified port not available, pick the first available port
        if port is None or port not in available_ports:
            if available_ports:
                print(f"Configured port '{port}' not found. Using first available port: {available_ports[0]}")
                port = available_ports[0]
            else:
                raise serial.SerialException("No COM ports available on the system.")

        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = baudrate
        self.ser.timeout = timeout
        self.lock = threading.Lock()

    @staticmethod
    def list_com_ports():
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

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
