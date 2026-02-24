import serial
import serial.tools.list_ports
import logging

logger = logging.getLogger(__name__)

class ECUConnection:
    """
    Handles robust, low-latency communication with the Motorcycle ECU via physical COM ports.
    """
    
    def __init__(self, baudrate: int = 115200, timeout: float = 1.0):
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None
        self.port = None

    @staticmethod
    def list_available_ports():
        """Returns a list of available physical COM ports, filtering out known Bluetooth virtual ports."""
        try:
            ports = serial.tools.list_ports.comports()
            valid_ports = []
            for port in ports:
                # Filter out obvious Bluetooth virtual ports based on description or hwid
                desc_lower = port.description.lower()
                # hwid often contains BTHENUM for bluetooth on Windows
                hwid_lower = port.hwid.lower() if port.hwid else ""
                
                if "bluetooth" not in desc_lower and "bthenum" not in hwid_lower:
                    valid_ports.append((port.device, port.description))
                    
            return valid_ports
        except Exception as e:
            logger.error(f"Error enumerating ports: {e}")
            return []

    def connect(self, port: str):
        """
        Attempt to establish a connection to the specified COM port.
        Returns (success: bool, error_message: str)
        """
        if self.connection and self.connection.is_open:
            self.disconnect()

        try:
            self.connection = serial.Serial(
                port=port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                write_timeout=self.timeout
            )
            self.port = port
            logger.info(f"Successfully connected to {port} at {self.baudrate} baud.")
            return True, ""
            
        except serial.SerialException as e:
            error_msg = f"Serial Error: The port {port} might be in use, disconnected, or lacks permissions."
            logger.error(f"{error_msg} | Details: {e}")
            self.connection = None
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected connection error on {port}."
            logger.error(f"{error_msg} | Details: {e}")
            self.connection = None
            return False, error_msg

    def disconnect(self):
        """Safely close the serial connection with try/except in case the cable was yanked."""
        if self.connection:
            try:
                if self.connection.is_open:
                    self.connection.flush() # ensure everything is written before closing
                    self.connection.close()
                logger.info(f"Disconnected successfully from {self.port}.")
            except serial.SerialException as e:
                logger.warning(f"Error while closing port {self.port} (perhaps the cable was forcefully pulled): {e}")
            except Exception as e:
                logger.error(f"Unexpected error closing port {self.port}: {e}")
            finally:
                self.connection = None
                self.port = None

    def read_parameters(self):
        """
        Stub: Read parametric hex data from the ECU queue.
        Requires continuous buffering in production.
        """
        if not self.connection or not self.connection.is_open:
            raise ConnectionError("Not connected to ECU.")
        
        # Example dummy operation
        return b'\x00\xFF\xAA\xBB'

    def flash_binary(self, bin_path: str):
        """
        Stub: Write a firmware binary to the ECU carefully.
        Critical operation requiring checksum verification.
        """
        pass
