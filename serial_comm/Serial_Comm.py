import serial
import threading
import time

class SerialComm:
    def __init__(self, port='COM5', baudrate=115200, timeout=1):
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = baudrate
        self.ser.timeout = timeout
        self.lock = threading.Lock()

    def open(self):
        try:
            if not self.ser.is_open:
                self.ser.open()
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")

    def close(self):
        if self.ser.is_open:
            self.ser.close()

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
