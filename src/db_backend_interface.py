from typing import List, Dict

class DatabaseBackend:
    def insert(self, item: Dict) -> None:
        pass
    
    def get(self) -> List[Dict]:
        pass

    def get_one(self, identifier: str) -> Dict:
        pass

    def exists(self, identifier: str) -> bool:
        pass

    def delete(self, identifier: str) -> None:
        pass

    def get_by_date(self, from_date: int = None, to_date: int = None) -> List[Dict]:
        pass
    
    def delete_by_date(self, from_date: int = None, to_date: int = None) -> None:
        pass