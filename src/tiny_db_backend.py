from tinydb import TinyDB, Query
from typing import List, Dict
from src.db_backend_interface import DatabaseBackend
from datetime import datetime

class TinyDBBackend(DatabaseBackend):
    def __init__(self, path: str) -> None:
        self.db = TinyDB(path, sort_keys=True)

    def validate_timestamp(self, timestamp: int) -> None:
        try:
            datetime.utcfromtimestamp(timestamp)
        except (ValueError, TypeError, OverflowError):
            raise ValueError("Invalid timestamp value")
        
    def validate_from_and_to_date(self, from_date, to_date):
        if from_date is not None:
            self.validate_timestamp(from_date)
        if to_date is not None:
            self.validate_timestamp(to_date)
        if from_date is not None and to_date is not None:
            if from_date > to_date:
                raise ValueError("from_date must be less than to_date")
        
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

    def insert(self, item: Dict) -> None:
        self.validate_item(item)
        self.db.insert(item)
    
    def get(self) -> List[Dict]:
        return self.db.all()

    def get_one(self, identifier: str) -> Dict:
        self.validate_id(identifier)
        item_query = Query()
        result = self.db.search(item_query.id == identifier)
        return result[0] if result else None

    def exists(self, identifier: str) -> bool:
        self.validate_id(identifier)
        item_query = Query()
        return bool(self.db.search(item_query.id == identifier))
    
    def delete(self, identifier: str) -> None:
        self.validate_id(identifier)
        item_query = Query()
        self.db.remove(item_query.id == identifier)

    def get_by_date(self, from_date: int = None, to_date: int = None) -> List[Dict]:
        self.validate_from_and_to_date(from_date, to_date)
        
        item_query = Query()
        if from_date is not None and to_date is not None:
            results = self.db.search((item_query.timestamp >= from_date) & (item_query.timestamp <= to_date))
        elif from_date is not None:
            results = self.db.search(item_query.timestamp >= from_date)
        elif to_date is not None:
            results = self.db.search(item_query.timestamp <= to_date)
        else:
            results = self.db.all()

        
        return results



    def delete_by_date(self, from_date: int = None, to_date: int = None) -> None:
        self.validate_from_and_to_date(from_date, to_date)
        item_query = Query()
        if from_date is not None and to_date is not None:
            self.db.remove((item_query.timestamp >= from_date) & (item_query.timestamp <= to_date))
        elif from_date is not None:
            self.db.remove(item_query.timestamp >= from_date)
        elif to_date is not None:
            self.db.remove(item_query.timestamp <= to_date)