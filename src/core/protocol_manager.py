import os
import json
import random
import logging

logger = logging.getLogger(__name__)

class ProtocolManager:
    """
    Manages the protocol layer between the UI and the ECU connection.
    Responsible for translating raw byte streams to meaningful data
    and vice-versa.
    """
    def __init__(self, ecu_connection=None):
        self.ecu = ecu_connection
        self.dtc_database_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data",
            "dtc_database.json"
        )
        self.dtc_cache = []
        self._load_dtc_database()

    def _load_dtc_database(self):
        """Loads the DTC database from the JSON file."""
        if not os.path.exists(self.dtc_database_path):
            logger.error(f"DTC database not found at {self.dtc_database_path}")
            return
            
        try:
            with open(self.dtc_database_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.dtc_cache = data.get("dtc_list", [])
                logger.info(f"Loaded {len(self.dtc_cache)} DTC entries from database.")
        except Exception as e:
            logger.error(f"Failed to load DTC database: {e}")

    def get_mock_dtc(self):
        """
        Simulates reading DTCs from the ECU.
        Returns 1 to 2 random DTCs from the database.
        """
        if not self.dtc_cache:
            return [{"code": "ERR", "description": "Veritabanı yüklenemedi"}]
            
        # Return 1 or 2 random DTCs
        count = random.randint(1, 2)
        return random.sample(self.dtc_cache, count)

    def get_dtc(self):
        """
        Reads real DTCs from the ECU or simulates if simulator is active.
        """
        if not self.ecu or self.ecu.is_simulator:
            return self.get_mock_dtc()
            
        if not self.ecu.connection or not self.ecu.connection.is_open:
            return None
            
        try:
            self.ecu.connection.write(b'D')
            response = self.ecu.connection.readline().decode('ascii', errors='ignore').strip()
            
            if not response:
                return None
                
            if response.startswith("D,"):
                parts = response.split(",")[1:]
                result = []
                for code in parts:
                    if not code:
                        continue
                    desc = "Bilinmeyen Arıza Kodu"
                    for item in self.dtc_cache:
                        if item.get("code") == code:
                            desc = item.get("description", desc)
                            break
                    result.append({"code": code, "description": desc})
                
                if not result:
                     return [{"code": "OK", "description": "Arıza Kodu Bulunmadı"}]
                return result
            return None
        except Exception as e:
            logger.error(f"DTC okuma hatası: {e}")
            return None

    def get_mock_live_data(self):
        """
        Simulates reading live data from the ECU.
        Returns a dictionary with realistic fluctuating values.
        """
        return {
            "Motor Devri (RPM)": random.randint(1500, 8000),
            "Soğutma Sıvısı (°C)": random.randint(80, 105),
            "Akü Voltajı (V)": round(random.uniform(13.5, 14.4), 1),
            "Gaz Kelebeği (TPS) (%)": random.randint(0, 100)
        }

    def get_live_data(self):
        """
        Reads real live data from the ECU or simulates if simulator is active.
        """
        if not self.ecu or self.ecu.is_simulator:
            return self.get_mock_live_data()
            
        if not self.ecu.connection or not self.ecu.connection.is_open:
            return None
            
        try:
            self.ecu.connection.write(b'L')
            response = self.ecu.connection.readline().decode('ascii', errors='ignore').strip()
            
            if not response:
                return None
                
            if response.startswith("L,"):
                parts = response.split(",")
                if len(parts) >= 5:
                    return {
                        "Motor Devri (RPM)": parts[1],
                        "Soğutma Sıvısı (°C)": parts[2],
                        "Akü Voltajı (V)": parts[3],
                        "Gaz Kelebeği (TPS) (%)": parts[4]
                    }
            return None
        except Exception as e:
            logger.error(f"Live data okuma hatası: {e}")
            return None
