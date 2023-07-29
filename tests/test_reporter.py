from src.fake_chain import FakeChain
from langchain.chains.base import Chain
import unittest
from unittest import TestCase
from unittest.mock import call, patch
from src.reporter import Reporter
from src.content_provider import ContentProvider, PapersWithCodeContentProvider
from typing import Dict
import requests
import logging
class TestReporter(TestCase):

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
        
        reporter = Reporter(content_providers, llm_chain, logger)

        self.assertIsNotNone(reporter._llm_chain)
        self.assertIsNotNone(reporter._content_providers)

        

    def test_invalid_llm_chain_instance(self):
        
        logger = self.create_logger("test_logger")
        content_providers = self.get_one_content_provider_in_a_list()
        llm_chain = "This is not a Chain instance"  
        with self.assertRaises(TypeError):  
            reporter = Reporter(content_providers, llm_chain, logger)



    def test_invalid_content_provider_instance(self):
        logger = self.create_logger("test_logger")
        content_providers = ["This is not a ContentProvider instance"]  
        llm_chain = FakeChain() 
        
        with self.assertRaises(TypeError):  
            reporter = Reporter(content_providers, llm_chain, logger)

    def test_empty_list_content_providers(self):
        logger = self.create_logger("test_logger")
        content_providers = []  
        llm_chain = FakeChain() 
        
        with self.assertRaises(ValueError):  
            reporter = Reporter(content_providers, llm_chain, logger)

    def test_not_list_content_providers(self):
        logger = self.create_logger("test_logger")
        content_providers = 0
        llm_chain = FakeChain() 
        
        with self.assertRaises(ValueError):  
            reporter = Reporter(content_providers, llm_chain, logger)


    @patch('src.content_provider.ContentProvider.get_content', return_value=[{"test_content":"content"}])
    def test_report_function_getting_one_post(self, mock_get_content):
        logger = self.create_logger("test_logger")     
        content_provider = ContentProvider()
        
        def inputs_to_outputs(inputs: Dict[str, str]) -> Dict[str, str]:
            return {"Post": inputs.pop("test_content") + " test"}

        llm_chain = FakeChain(
            expected_inputs=["test_content"],
            expected_outputs=["Post"],
            inputs_to_outputs=inputs_to_outputs,
        )

        content_providers = [content_provider]

        reporter = Reporter(content_providers, llm_chain, logger)

        result = reporter.report() 

        self.assertEqual(result, [{"Post": "content test"}])

    @patch('src.content_provider.ContentProvider.get_content', return_value=[{"test_content":"content1"}, {"test_content":"content2"}])
    def test_report_function_getting_two_post(self, mock_get_content):
        
        
        logger = self.create_logger("test_logger")
        content_provider = ContentProvider()

        def inputs_to_outputs(inputs: Dict[str, str]) -> Dict[str, str]:
            return {"Post": inputs.pop("test_content") + " test"}

        llm_chain = FakeChain(
            expected_inputs=["test_content"],
            expected_outputs=["Post"],
            inputs_to_outputs=inputs_to_outputs,
        )

        content_providers = [content_provider]

        reporter = Reporter(content_providers, llm_chain, logger)

        
        result = reporter.report()  

        self.assertEqual(
            result,
            [
                {"Post": "content1 test"},
                {"Post": "content2 test"}
            ]
        )

    @patch('src.content_provider.ContentProvider.get_content', side_effect=[[{"test_content":"content1"}], [{"test_content":"content2"}]])
    def test_report_function_from_two_content_providers(self, mock_get_content):
        
        
        logger = self.create_logger("test_logger")
        
        content_provider1 = ContentProvider()
        content_provider2 = ContentProvider()

        def inputs_to_outputs(inputs: Dict[str, str]) -> Dict[str, str]:
            return {"Post": inputs.pop("test_content") + " test"}

        llm_chain = FakeChain(
            expected_inputs=["test_content"],
            expected_outputs=["Post"],
            inputs_to_outputs=inputs_to_outputs,
        )

        content_providers = [content_provider1, content_provider2]

        reporter = Reporter(content_providers, llm_chain, logger)

        
        result = reporter.report()  

        self.assertEqual(
            result,
            [
                {"Post": "content1 test"},
                {"Post": "content2 test"}
            ]
        )


    @patch('requests.get')
    def test_report_handles_content_provider_fail(self, mock_get):
        logger = self.create_logger("test_logger")
        mock_get.return_value.status_code = 500  
        content_provider = PapersWithCodeContentProvider()
        
        llm_chain = FakeChain()

        content_providers = [content_provider]

        reporter = Reporter(content_providers, llm_chain, logger)

        result = reporter.report() 

        self.assertEqual(result,[])


    @patch('logging.Logger.info')
    @patch('src.content_provider.ContentProvider.get_content', return_value=[{"test_content":"content"}])
    @patch('src.content_provider.ContentProvider.name', return_value="test_content_provider")
    def test_report_logs_content_provider_start_content_report_and_finish(self, mock_name, mock_get_content, mock_info):
        logger = self.create_logger('test_logger')

        content_providers = self.get_one_content_provider_in_a_list()
        
        llm_chain = FakeChain(output= {"Post": "This is a test post"}, expected_inputs=["test_content"])

        reporter = Reporter(content_providers, llm_chain, logger)

        result = reporter.report() 
        calls = [call("Starting reporting"), call(f"Got 1 contents from {content_providers[0].name()}"), call("Finished reporting")]

        mock_info.assert_has_calls(calls, any_order=False)


    @patch('logging.Logger.error')
    @patch('logging.Logger.info')
    @patch('requests.get')
    @patch('src.content_provider.ContentProvider.name', return_value="test_content_provider")
    def test_report_logs_content_provider_start_fail_and_finish(self,mock_name, mock_get, mock_info, mock_error):
        logger = self.create_logger('test_logger')
        mock_get.return_value.status_code = 500  
        content_provider = PapersWithCodeContentProvider()
        
        llm_chain = FakeChain()

        content_providers = [content_provider]  

        reporter = Reporter(content_providers, llm_chain, logger)

        result = reporter.report() 
        info_calls = [call("Starting reporting"),call(f"Got 0 contents from {content_provider.name()}"), call("Finished reporting")]  
        error_calls = [call(f"Error getting content from {content_provider.name()}: Error getting content with status code: {mock_get.return_value.status_code}")]
        mock_info.assert_has_calls(info_calls, any_order=False)
        mock_error.assert_has_calls(error_calls, any_order=False)


