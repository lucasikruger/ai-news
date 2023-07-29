from tinydb import TinyDB, Query
from typing import List, Dict
from src.db_backend_interface import DatabaseBackend

class TinyDBBackend(DatabaseBackend):
    def __init__(self, path: str) -> None:
        self.db = TinyDB(path, sort_keys=True)
    
    def insert(self, item: Dict) -> None:
        self.db.insert(item)
    
    def get(self) -> List[Dict]:
        return self.db.all()

    def get_one(self, identifier: str) -> Dict:
        item_query = Query()
        result = self.db.search(item_query.id == identifier)
        return result[0] if result else None

    def exists(self, identifier: str) -> bool:
        item_query = Query()
        return bool(self.db.search(item_query.id == identifier))
    
    def delete(self, identifier: str) -> None:
        item_query = Query()
        self.db.remove(item_query.id == identifier)

    def get_by_date(self, from_date: int = None, to_date: int = None) -> List[Dict]:
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
        item_query = Query()
        if from_date is not None and to_date is not None:
            self.db.remove((item_query.timestamp >= from_date) & (item_query.timestamp <= to_date))
        elif from_date is not None:
            self.db.remove(item_query.timestamp >= from_date)
        elif to_date is not None:
            self.db.remove(item_query.timestamp <= to_date)