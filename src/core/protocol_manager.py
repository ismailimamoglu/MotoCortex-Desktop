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
    def __init__(self):
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
