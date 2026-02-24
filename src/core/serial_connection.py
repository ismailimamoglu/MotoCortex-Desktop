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
        """Returns a list of available COM ports on the system."""
        ports = serial.tools.list_ports.comports()
        return [(port.device, port.description) for port in ports]

    def connect(self, port: str):
        """
        Attempt to establish a connection to the specified COM port.
        """
        try:
            self.connection = serial.Serial(
                port=port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            self.port = port
            logger.info(f"Successfully connected to {port} at {self.baudrate} baud.")
            return True
        except serial.SerialException as e:
            logger.error(f"Failed to connect to {port}: {e}")
            return False

    def disconnect(self):
        """Safely close the serial connection."""
        if self.connection and self.connection.is_open:
            self.connection.close()
            logger.info(f"Disconnected from {self.port}.")
        self.connection = None

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
