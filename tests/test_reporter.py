from src.fake_chain import FakeChain
from langchain.chains.base import Chain
import unittest
from unittest import TestCase
from unittest.mock import call, patch
from src.reporter import Reporter
from src.content_provider.content_provider import ContentProvider
from src.content_provider.papers_with_code_content_provider import PapersWithCodeContentProvider
from typing import Dict
import requests
import logging
import json
import os
import glob
from src.data_storage import DataStorage
from src.tiny_db_backend import TinyDBBackend
import hashlib
from datetime import datetime
class TestReporter(TestCase):
	def create_id(self,json_obj):
		json_str = json.dumps(json_obj, sort_keys=True) # Sort keys to ensure consistent ordering
		return hashlib.sha256(json_str.encode()).hexdigest()

	def tearDown(self):
		files = glob.glob('data/*')
		for file in files:
			os.remove(file)
	def get_one_content_provider_in_a_list(self):

		content_providers = [ContentProvider()]

		return content_providers

	
	def create_logger(self, name: str, level: int=logging.INFO):
		logger = logging.getLogger(name)
		logger.setLevel(level)
		
		
		ch = logging.StreamHandler()
		ch.setLevel(level)
		
		
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		ch.setFormatter(formatter)
		
		
		logger.addHandler(ch)
		

		return logger
	
	def test_create_reporter_instance(self):
		logger = self.create_logger("test_logger")

		content_providers = self.get_one_content_provider_in_a_list()
		
		llm_chain = FakeChain()
		
		data_storage = DataStorage("data/")
		reporter = Reporter(content_providers, llm_chain, logger, data_storage)

		self.assertIsNotNone(reporter._llm_chain)
		self.assertIsNotNone(reporter._content_providers)

		

	def test_invalid_llm_chain_instance(self):
		
		logger = self.create_logger("test_logger")
		content_providers = self.get_one_content_provider_in_a_list()
		llm_chain = "This is not a Chain instance"  
		with self.assertRaises(TypeError):  
			data_storage = DataStorage("data/")
			reporter = Reporter(content_providers, llm_chain, logger, data_storage)



	def test_invalid_content_provider_instance(self):
		logger = self.create_logger("test_logger")
		content_providers = ["This is not a ContentProvider instance"]  
		llm_chain = FakeChain() 
		
		with self.assertRaises(TypeError):  
			data_storage = DataStorage("data/")
			reporter = Reporter(content_providers, llm_chain, logger, data_storage)

	def test_empty_list_content_providers(self):
		logger = self.create_logger("test_logger")
		content_providers = []  
		llm_chain = FakeChain() 
		
		with self.assertRaises(ValueError):  
			data_storage = DataStorage("data/")
			reporter = Reporter(content_providers, llm_chain, logger, data_storage)

	def test_not_list_content_providers(self):
		logger = self.create_logger("test_logger")
		content_providers = 0
		llm_chain = FakeChain() 
		
		with self.assertRaises(ValueError):  
			data_storage = DataStorage("data/")
			reporter = Reporter(content_providers, llm_chain, logger, data_storage)


	@patch('src.content_provider.content_provider.ContentProvider.get_content', return_value=[{"test_content":"content"}])
	@patch('src.content_provider.content_provider.ContentProvider.name', return_value="test_content_provider")
	@patch('src.reporter.Reporter.get_timestamp', return_value=1000)
	def test_report_function_getting_one_post(self,mock_time, mock_name, mock_get_content):
		logger = self.create_logger("test_logger")     
		content_provider = ContentProvider()
		
		def inputs_to_outputs(inputs: Dict[str, str]) -> Dict[str, str]:
			return {"post": inputs.pop("test_content") + " test"}

		llm_chain = FakeChain(
			expected_inputs=["test_content"],
			expected_outputs=["post"],
			inputs_to_outputs=inputs_to_outputs,
		)

		content_providers = [content_provider]

		data_storage = DataStorage("data/")
		reporter = Reporter(content_providers, llm_chain, logger, data_storage)

		result = reporter.report() 

		self.assertEqual(result, [{'content':{'test_content':'content'},'report': {'post': 'content test', 'content_provider': content_provider.name()},'id':self.create_id({"test_content":"content"}), 'timestamp':1000}])


	@patch('src.content_provider.content_provider.ContentProvider.get_content', return_value=[{"test_content":"content1"}, {"test_content":"content2"}])
	@patch('src.content_provider.content_provider.ContentProvider.name', return_value="test_content_provider")
	@patch('src.reporter.Reporter.get_timestamp', return_value=1000)
	def test_report_function_getting_two_post(self, mock_time,mock_name, mock_get_content):
		
		
		logger = self.create_logger("test_logger")
		content_provider = ContentProvider()

		def inputs_to_outputs(inputs: Dict[str, str]) -> Dict[str, str]:
			return {"post": inputs.pop("test_content") + " test"}

		llm_chain = FakeChain(
			expected_inputs=["test_content"],
			expected_outputs=["post"],
			inputs_to_outputs=inputs_to_outputs,
		)

		content_providers = [content_provider]

		data_storage = DataStorage("data/")
		reporter = Reporter(content_providers, llm_chain, logger, data_storage)

		
		result = reporter.report()  

		self.assertEqual(
			result,
			[
				{'content':{ 'test_content':'content1'},'report': {'post': 'content1 test', 'content_provider': content_provider.name()},
				'id':self.create_id({"test_content":"content1"}), 'timestamp':1000},
				{'content':{ 'test_content':'content2'},'report': {'post': 'content2 test', 'content_provider': content_provider.name()},
				'id':self.create_id({"test_content":"content2"}), 'timestamp':1000}
			]
		)

	@patch('src.content_provider.content_provider.ContentProvider.get_content', side_effect=[[{"test_content":"content1"}], [{"test_content":"content2"}]])
	@patch('src.content_provider.content_provider.ContentProvider.name', return_value="test_content_provider")
	@patch('src.reporter.Reporter.get_timestamp', return_value=1000)
	def test_report_function_from_two_content_providers(self,mock_time,mock_name, mock_get_content):
		
		
		logger = self.create_logger("test_logger")
		
		content_provider1 = ContentProvider()
		content_provider2 = ContentProvider()

		def inputs_to_outputs(inputs: Dict[str, str]) -> Dict[str, str]:
			return {"post": inputs.pop("test_content") + " test"}

		llm_chain = FakeChain(
			expected_inputs=["test_content"],
			expected_outputs=["post"],
			inputs_to_outputs=inputs_to_outputs,
		)

		content_providers = [content_provider1, content_provider2]

		data_storage = DataStorage("data/")
		reporter = Reporter(content_providers, llm_chain, logger, data_storage)

		
		result = reporter.report()  

		self.assertEqual(
			result,
			[
				{'content':{ 'test_content':'content1'},'report': {'post': 'content1 test', 'content_provider': content_provider1.name()},
				'id':self.create_id({"test_content":"content1"}), 'timestamp':1000},
				{'content':{ 'test_content':'content2'},'report': {'post': 'content2 test', 'content_provider': content_provider1.name()},
				'id':self.create_id({"test_content":"content2"}), 'timestamp':1000}
			]
		)


	@patch('requests.get')
	def test_report_handles_content_provider_fail(self, mock_get):
		logger = self.create_logger("test_logger")
		mock_get.return_value.status_code = 500  
		content_provider = PapersWithCodeContentProvider()
		
		llm_chain = FakeChain()

		content_providers = [content_provider]

		data_storage = DataStorage("data/")
		reporter = Reporter(content_providers, llm_chain, logger, data_storage)

		result = reporter.report() 

		self.assertEqual(result,[])


	@patch('logging.Logger.info')
	@patch('src.content_provider.content_provider.ContentProvider.get_content', return_value=[{"test_content":"content"}])
	@patch('src.content_provider.content_provider.ContentProvider.name', return_value="test_content_provider")
	@patch('src.reporter.Reporter.get_timestamp', return_value=1000)
	def test_report_logs_content_provider_start_content_report_and_finish(self,mock_time, mock_name, mock_get_content, mock_info):
		logger = self.create_logger('test_logger')

		content_providers = self.get_one_content_provider_in_a_list()
		
		llm_chain = FakeChain(output= {"post": "This is a test post"}, expected_inputs=["test_content"])

		data_storage = DataStorage("data/")
		reporter = Reporter(content_providers, llm_chain, logger, data_storage)
		
		result = reporter.report() 
		calls = [call("Starting reporting"), call(f"Got 1 contents from {content_providers[0].name()}"), call(json.dumps({"content": {"test_content": "content"}, "report": {"post": "This is a test post", "content_provider": "test_content_provider"}, "id": self.create_id({"test_content":"content"}), "timestamp": 1000})), call("Finished reporting")]
		
		mock_info.assert_has_calls(calls, any_order=False)


	@patch('logging.Logger.error')
	@patch('logging.Logger.info')
	@patch('requests.get')
	@patch('src.content_provider.content_provider.ContentProvider.name', return_value="test_content_provider")
	def test_report_logs_content_provider_start_fail_and_finish(self,mock_name, mock_get, mock_info, mock_error):
		logger = self.create_logger('test_logger')
		mock_get.return_value.status_code = 500  
		content_provider = PapersWithCodeContentProvider()
		
		llm_chain = FakeChain()

		content_providers = [content_provider]  

		data_storage = DataStorage("data/")
		reporter = Reporter(content_providers, llm_chain, logger, data_storage)

		result = reporter.report() 
		info_calls = [call("Starting reporting"),call(f"Got 0 contents from {content_provider.name()}"), call("Finished reporting")]  
		error_calls = [call(f"Error getting content from {content_provider.name()}: Error getting content with status code: {mock_get.return_value.status_code}")]
		mock_info.assert_has_calls(info_calls, any_order=False)
		mock_error.assert_has_calls(error_calls, any_order=False)
	def test_invalid_logger(self):
		content_providers = self.get_one_content_provider_in_a_list()
		llm_chain = FakeChain()
		data_storage = DataStorage("data/")
		logger = "invalid_logger"
		with self.assertRaises(TypeError):
			reporter = Reporter(content_providers, llm_chain, logger, data_storage)

	def test_invalid_data_storage(self):
		logger = self.create_logger('test_logger')
		content_providers = self.get_one_content_provider_in_a_list()
		llm_chain = FakeChain()
		data_storage = "invalid_data_storage"
		with self.assertRaises(TypeError):
			reporter = Reporter(content_providers, llm_chain, logger, data_storage)

	@patch('src.content_provider.content_provider.ContentProvider.get_content', side_effect=[[{"test_content":"content1"}], [{"test_content":"content2"}]])
	@patch('src.content_provider.content_provider.ContentProvider.name', return_value="test_content_provider")
	@patch('src.reporter.Reporter.get_timestamp', return_value=1000)
	def test_report_save_on_db(self,mock_time,mock_name, mock_get_content):
		
		
		logger = self.create_logger("test_logger")
		
		content_provider1 = ContentProvider()
		content_provider2 = ContentProvider()

		def inputs_to_outputs(inputs: Dict[str, str]) -> Dict[str, str]:
			return {"post": inputs.pop("test_content") + " test"}

		llm_chain = FakeChain(
			expected_inputs=["test_content"],
			expected_outputs=["post"],
			inputs_to_outputs=inputs_to_outputs,
		)

		content_providers = [content_provider1, content_provider2]

		data_storage = DataStorage("data/")
		reporter = Reporter(content_providers, llm_chain, logger, data_storage)

		
		result = reporter.report()  

		items = [
				{'content':{ 'test_content':'content1'},'report': {'post': 'content1 test', 'content_provider': content_provider1.name()},
				'id':self.create_id({"test_content":"content1"}), 'timestamp':1000},
				{'content':{ 'test_content':'content2'},'report': {'post': 'content2 test', 'content_provider': content_provider1.name()},
				'id':self.create_id({"test_content":"content2"}), 'timestamp':1000}
			]
		db = TinyDBBackend(f"data/{content_provider1.name()}.json")

		self.assertEqual(db.get(), items)

	@patch('src.content_provider.content_provider.ContentProvider.get_content', side_effect=[[{"test_content":"content1"}], [{"test_content":"content2"}],[{"test_content":"content1"}], [{"test_content":"content2"}]])
	@patch('src.content_provider.content_provider.ContentProvider.name', return_value="test_content_provider")
	@patch('src.reporter.Reporter.get_timestamp', return_value=1000)
	def test_report_already_saved_on_db(self,mock_time,mock_name, mock_get_content):
		
		
		logger = self.create_logger("test_logger")
		
		content_provider1 = ContentProvider()
		content_provider2 = ContentProvider()

		def inputs_to_outputs(inputs: Dict[str, str]) -> Dict[str, str]:
			return {"post": inputs.pop("test_content") + " test"}

		llm_chain = FakeChain(
			expected_inputs=["test_content"],
			expected_outputs=["post"],
			inputs_to_outputs=inputs_to_outputs,
		)

		content_providers = [content_provider1, content_provider2]

		data_storage = DataStorage("data/")
		reporter = Reporter(content_providers, llm_chain, logger, data_storage)

		
		result = reporter.report()  

		result2 = reporter.report()  
		self.assertEqual(result2, [])

if __name__ == '__main__':
    unittest.main()
