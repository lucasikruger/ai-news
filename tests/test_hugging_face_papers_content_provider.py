from src.content_provider.content_provider import ContentProvider
from src.content_provider.hugging_face_papers_content_provider import HuggingFacePapersContentProvider
from unittest import TestCase, mock
import requests
import json
class TestContentProvider(TestCase):

	def test_name_papers_with_code_content_provider(self):
		contentProvider = HuggingFacePapersContentProvider()
		self.assertEqual(contentProvider.name(), "HuggingFacePapersContentProvider")
