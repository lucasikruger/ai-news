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

    def test_insert_and_get(self):
        item = {'type': 'post', 'content': 'Content of the post'}
        self.db.insert(item)
        items = self.db.get()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0], item)

    def test_exists(self):
        item = {'id': 'id1', 'type': 'post', 'content': 'Content of the post'}
        self.assertFalse(self.db.exists('id1'))
        self.db.insert(item)
        self.assertTrue(self.db.exists('id1'))

    def test_get_one(self):
        item = {'id': 'id1', 'type': 'post', 'content': 'Content of the post'}
        self.assertIsNone(self.db.get_one('id1'))
        self.db.insert(item)
        self.assertEqual(self.db.get_one('id1'), item)

    def test_multiple_inserts(self):
        items = [
            {'type': 'post', 'content': 'Content 1'},
            {'type': 'post', 'content': 'Content 2'}
        ]
        for item in items:
            self.db.insert(item)

        retrieved_items = self.db.get()
        self.assertEqual(len(retrieved_items), len(items))
        self.assertListEqual(retrieved_items, items)

    def test_delete(self):
        item1 = {'id': 'id1', 'type': 'post', 'content': 'Content 1'}
        item2 = {'id': 'id2', 'type': 'post', 'content': 'Content 2'}
        self.db.insert(item1)
        self.db.insert(item2)
        self.assertTrue(self.db.exists('id1'))
        self.assertTrue(self.db.exists('id2'))
        self.db.delete('id1')
        self.assertFalse(self.db.exists('id1'))
        self.assertTrue(self.db.exists('id2'))

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

if __name__ == '__main__':
    unittest.main()
