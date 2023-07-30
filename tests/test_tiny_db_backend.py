import unittest
import os
from src.db_backend_interface import DatabaseBackend
from src.tiny_db_backend import TinyDBBackend

class TestTinyDBBackend(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_db.json'
        self.db: DatabaseBackend = TinyDBBackend(self.db_path)

    def tearDown(self):
        os.remove(self.db_path)

    def validate_report(self, function):
        # Test insert with invalid ID
        item = {'id': 123, 'type': 'post', 'content': 'Content of the post', 'timestamp': 1000}
        with self.assertRaises(ValueError):
            function(item)

        # Test insert without ID
        item = {'type': 'post', 'content': 'Content of the post', 'timestamp': 1000}
        with self.assertRaises(ValueError):
            function(item)

        # Test insert without timestamp
        item = {'id': 'id1', 'type': 'post', 'content': 'Content of the post'}
        with self.assertRaises(ValueError):
            function(item)

        # Test insert with invalid timestamp
        item = {'id': 'id1', 'type': 'post', 'content': 'Content of the post', 'timestamp': "invalid_timestamp"}
        with self.assertRaises(ValueError):
            function(item)


    def test_insert_and_get(self):
        item = {'id': 'id1', 'type': 'post', 'content': 'Content 1', 'timestamp': 1000}
        self.db.insert(item)
        items = self.db.get()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0], item)

    def test_exists(self):
        item = {'id': 'id1', 'type': 'post', 'content': 'Content 1', 'timestamp': 1000}
        self.assertFalse(self.db.exists('id1'))
        self.db.insert(item)
        self.assertTrue(self.db.exists('id1'))

    def test_get_one(self):
        item = {'id': 'id1', 'type': 'post', 'content': 'Content 1', 'timestamp': 1000}
        self.assertIsNone(self.db.get_one('id1'))
        self.db.insert(item)
        self.assertEqual(self.db.get_one('id1'), item)

    def test_multiple_inserts(self):
        items = [
            {'id': 'id1', 'type': 'post', 'content': 'Content 1', 'timestamp': 1000},
            {'id': 'id2', 'type': 'post', 'content': 'Content 2', 'timestamp': 2000}
        ]
        for item in items:
            self.db.insert(item)

        retrieved_items = self.db.get()
        self.assertEqual(len(retrieved_items), len(items))
        self.assertListEqual(retrieved_items, items)

    def test_delete(self):
        item1 = {'id': 'id1', 'type': 'post', 'content': 'Content 1', 'timestamp': 1000}
        item2 = {'id': 'id2', 'type': 'post', 'content': 'Content 2', 'timestamp': 2000}
        self.db.insert(item1)
        self.db.insert(item2)
        self.assertTrue(self.db.exists('id1'))
        self.assertTrue(self.db.exists('id2'))
        self.db.delete('id1')
        self.assertFalse(self.db.exists('id1'))
        self.assertTrue(self.db.exists('id2'))

    def test_get_by_date_invalid_timestamp(self):
        with self.assertRaises(ValueError):
            self.db.get_by_date(from_date="invalid_timestamp")

    def test_delete_by_date_invalid_timestamp(self):
        with self.assertRaises(ValueError):
            self.db.delete_by_date(from_date="invalid_timestamp")

    def test_get_from_date_greater_than_to_date(self):
        with self.assertRaises(ValueError):
            self.db.get_by_date(from_date=1000, to_date=500)
    
    def test_delete_from_date_greater_than_to_date(self):
        with self.assertRaises(ValueError):
            self.db.delete_by_date(from_date=1000, to_date=500)

    def test_get_by_date(self):
        item1 = {'id': 'id1', 'type': 'post', 'content': 'Content 1', 'timestamp': 1000}
        item2 = {'id': 'id2', 'type': 'post', 'content': 'Content 2', 'timestamp': 2000}
        self.db.insert(item1)
        self.db.insert(item2)
        self.assertEqual(self.db.get_by_date(from_date=1500), [item2])
        self.assertEqual(self.db.get_by_date(to_date=1500), [item1])
        self.assertEqual(self.db.get_by_date(from_date=1000, to_date=2000), [item1, item2])

    def test_delete_by_date(self):
        item1 = {'id': 'id1', 'type': 'post', 'content': 'Content 1', 'timestamp': 1000}
        item2 = {'id': 'id2', 'type': 'post', 'content': 'Content 2', 'timestamp': 2000}
        self.db.insert(item1)
        self.db.insert(item2)
        self.db.delete_by_date(from_date=1500)
        self.assertFalse(self.db.exists('id2'))
        self.assertTrue(self.db.exists('id1'))

    def test_insert_invalid_report(self):
        self.validate_report(self.db.insert)
    def test_invalid_id_get_one(self):
        with self.assertRaises(ValueError):
            self.db.get_one(123)

    def test_invalid_id_exists(self):
        with self.assertRaises(ValueError):
            self.db.exists(123)

    def test_invalid_id_delete(self):
        with self.assertRaises(ValueError):
            self.db.delete(123)


if __name__ == '__main__':
    unittest.main()
