from src.content_provider.content_provider import ContentProvider
from src.content_provider.papers_with_code_content_provider import PapersWithCodeContentProvider
from src.data_storage import DataStorage
from src.db_backend_interface import DatabaseBackend
from src.tiny_db_backend import TinyDBBackend
from unittest import TestCase, mock
import requests
import json
import os
import glob
class TestDataStorage(TestCase):
	def tearDown(self):
		files = glob.glob('data/*')
		for file in files:
			os.remove(file)
	def test_incorrect_data_storage_folder_type(self):
		with self.assertRaises(TypeError):
			dataStorage = DataStorage(123)

	def test_incorrect_data_storage_folder_value(self):
		with self.assertRaises(ValueError):
			dataStorage = DataStorage("")

	def test_error_saving_reports_with_invalid_storage_file_name(self):
		dataStorage = DataStorage(folder = "data/")
		storage_file_name = 1
		with self.assertRaises(ValueError):
			dataStorage.save_reports(storage_file_name = storage_file_name, reports = [])

	def test_error_saving_reports_with_invalid_reports(self):
		dataStorage = DataStorage(folder = "data/")
		storage_file_name = "test"
		with self.assertRaises(TypeError):
			dataStorage.save_reports(storage_file_name = storage_file_name, reports = 1)

	def test_error_saving_reports_with_invalid_reports_content(self):
		dataStorage = DataStorage(folder = "data/")
		storage_file_name = "test"
		with self.assertRaises(TypeError):
			dataStorage.save_reports(storage_file_name = storage_file_name, reports = [1,2,3])

	def test_error_saving_empty_reports(self):
		dataStorage = DataStorage(folder = "data/")
		storage_file_name = "test"
		with self.assertRaises(ValueError):
			dataStorage.save_reports(storage_file_name = storage_file_name, reports = [])


	def test_error_saving_reports_with_invalid_report(self):
		dataStorage = DataStorage(folder = "data/")
		storage_file_name = "test"
		with self.assertRaises(ValueError):
			dataStorage.save_reports(storage_file_name = storage_file_name, reports = [{"report":"test"}])

	def test_more_than_one_report(self):
		dataStorage = DataStorage(folder = "data/")
		storage_file_name = "test"
		items = [
            {'id': 'id1', 'type': 'post', 'content': 'Content 1', 'timestamp': 1000},
            {'id': 'id2', 'type': 'post', 'content': 'Content 2', 'timestamp': 2000}
        ]
		dataStorage.save_reports(storage_file_name = storage_file_name, reports = items)

		databaseBackend = TinyDBBackend("data/"+storage_file_name+".json")
		self.assertEqual(databaseBackend.exists("id1"), True)
		self.assertEqual(databaseBackend.exists("id2"), True)
		
	def test_if_already_exists(self):
		dataStorage = DataStorage(folder = "data/")
		storage_file_name = "test"
		items = [
			{'id': 'id1', 'type': 'post', 'content': 'Content 1', 'timestamp': 1000},
			{'id': 'id2', 'type': 'post', 'content': 'Content 2', 'timestamp': 2000}
		]
		dataStorage.save_reports(storage_file_name = storage_file_name, reports = items)
		
		dataStorage.save_reports(storage_file_name = storage_file_name, reports = items)

		databaseBackend = TinyDBBackend("data/"+storage_file_name+".json")

		self.assertEqual(databaseBackend.get(), items)

	def test_exist_function(self):
		dataStorage = DataStorage(folder = "data/")
		storage_file_name = "test"
		items = [
			{'id': 'id1', 'type': 'post', 'content': 'Content 1', 'timestamp': 1000},
			{'id': 'id2', 'type': 'post', 'content': 'Content 2', 'timestamp': 2000}
		]
		dataStorage.save_reports(storage_file_name = storage_file_name, reports = items)
		

		self.assertEqual(dataStorage.exists(storage_file_name,"id1"), True)
		self.assertEqual(dataStorage.exists(storage_file_name,"id2"), True)
		self.assertEqual(dataStorage.exists(storage_file_name,"id3"), False)