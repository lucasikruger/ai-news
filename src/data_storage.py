from src.content_provider.content_provider import ContentProvider
from src.tiny_db_backend import TinyDBBackend
from typing import List, Dict
from datetime import datetime
import os
import glob
class DataStorage:
    def __init__(self, folder: str) -> None:
        if not isinstance(folder, str):
            raise TypeError("folder must be a string")
        
        if not folder:
            raise ValueError("folder must not be empty")
        
        self._folder = folder
        if self._folder[-1] != "/":
            self._folder += "/"
        if not os.path.exists(self._folder):
            os.makedirs(self._folder)

    def validate_timestamp(self, timestamp: int) -> None:
        try:
            datetime.utcfromtimestamp(timestamp)
        except (ValueError, TypeError, OverflowError):
            raise ValueError("Invalid timestamp value")
        
    def validate_id(self, identifier: str) -> None:
        if not isinstance(identifier, str):
            raise ValueError("ID must be a string")
        if not identifier:
            raise ValueError("ID must not be empty")
        

    def validate_item(self, item: Dict) -> None:
        if 'id' not in item:
            raise ValueError("ID must be present in the item")
        self.validate_id(item['id'])
        if 'timestamp' not in item:
            raise ValueError("Timestamp must be present in the item")
        self.validate_timestamp(item['timestamp'])

    def save_reports(self, storage_file_name: str, reports: List[Dict]) -> None:
        if not isinstance(storage_file_name, str):
            raise ValueError("content_provider must be a string")
        
        if not isinstance(reports, list):
            raise TypeError("reports must be a list")
        
        if not all(isinstance(report, dict) for report in reports):
            raise TypeError("reports must be a list of dictionaries")
        
        if not reports:
            raise ValueError("reports must not be empty")
        db = TinyDBBackend(self._folder + storage_file_name + ".json")
        for report in reports:
            self.validate_item(report)
            if not db.exists(report["id"]):
                db.insert(report)

    def exists(self, storage_file_name: str, identifier: str) -> bool:
        if not isinstance(storage_file_name, str):
            raise ValueError("content_provider must be a string")
        
        if not isinstance(identifier, str):
            raise ValueError("identifier must be a string")
        
        db = TinyDBBackend(self._folder + storage_file_name + ".json")
        return db.exists(identifier)