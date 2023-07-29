from src.content_provider import ContentProvider
from src.content_provider import PapersWithCodeContentProvider
from unittest import TestCase, mock
import requests
import json
class TestContentProvider(TestCase):

	def test_create_papers_with_code_content_provider(self):
		contentProvider = PapersWithCodeContentProvider()
		self.assertTrue(isinstance(contentProvider, ContentProvider))

	def test_name_papers_with_code_content_provider(self):
		contentProvider = PapersWithCodeContentProvider()
		self.assertEqual(contentProvider.name(), "PapersWithCodeContentProvider")

	@mock.patch('requests.get')
	def test_get_content_error(self, mock_get):
		mock_get.return_value.status_code = 500  # Simulate a server error
		contentProvider = PapersWithCodeContentProvider()
		with self.assertRaises(requests.exceptions.HTTPError):  # replace this with the actual Exception your code raises when there's a server error
			content = contentProvider.get_content()




	@mock.patch('requests.get')
	def test_get_content_paper_page_not_reachable(self, mock_get):
		# Mock HTML for main page
		mock_html_content_main = """
			<div class="infinite-container">
				<div class="row infinite-item item paper-card">
					<h1><a href="/paper/example-paper">Example Paper</a></h1>
					<p class="item-strip-abstract">This is an example abstract.</p>
					<div class="item-image" style="background-image: url('https://example.com/image.jpg')"></div>
					<div class="badge-primary">
						<a href="#">Tag1</a>
						<a href="#">Tag2</a>
					</div>
					<div class="entity-stars">
						<span class="badge">123 stars</span>
					</div>
					<div class="item-github-link">
						<a href="https://github.com/example">Github Link</a>
					</div>
				</div>
			</div>
			"""
		
		def side_effect_func(url):
			response = requests.Response()
			if "paperswithcode.com/paper" in url:  # If the URL is for a specific paper, return status code 500
				response.status_code = 500
			else:  # For the main page, return status code 200
				response.status_code = 200
				response._content = mock_html_content_main.encode()
			return response

		mock_get.side_effect = side_effect_func  # Assign the side effect function to the mock

		contentProvider = PapersWithCodeContentProvider()
		content = contentProvider.get_content()

		# Here's where we check that the content is as expected.
		expected_content = {
			"title": "Example Paper",
			"subtitle": "This is an example abstract.",
			"media": "https://example.com/image.jpg",
			"tags": ["Tag1", "Tag2"],
			"stars": 123,
			"github_link": "https://github.com/example",
			"uid": "/paper/example-paper",
			"abstract": "",
			"arxiv_url": "",
		}
		expected_content = {"paper" : json.dumps(expected_content)}
		self.assertEqual(content[0], expected_content)


	@mock.patch('requests.get')
	def test_get_content_success_returns_expected_dict(self, mock_get):
		# Mock HTML for main page
		mock_html_content_main = """
		<div class="infinite-container">
			<div class="row infinite-item item paper-card">
				<h1><a href="/paper/example-paper">Example Paper</a></h1>
				<p class="item-strip-abstract">This is an example abstract.</p>
				<div class="item-image" style="background-image: url('https://example.com/image.jpg')"></div>
				<div class="badge-primary">
					<a href="#">Tag1</a>
					<a href="#">Tag2</a>
				</div>
				<div class="entity-stars">
					<span class="badge">123 stars</span>
				</div>
				<div class="item-github-link">
					<a href="https://github.com/example">Github Link</a>
				</div>
			</div>
		</div>
		"""
		# Mock HTML for individual paper's page
		mock_html_content_paper = """
		<div class="paper-abstract">
			<p>This is the full abstract of the paper.</p>
			<a class="badge badge-light" href="https://arxiv.org/abs/example">arXiv</a>
		</div>
		"""
		
		# Define a side_effect function to return different responses based on input URL
		def side_effect_func(url):
			response = requests.Response()
			if "paperswithcode.com/paper" in url:
				response.status_code = 200
				response._content = mock_html_content_paper.encode()
			else:
				response.status_code = 200
				response._content = mock_html_content_main.encode()
			return response

		mock_get.side_effect = side_effect_func  # Assign the side effect function to the mock

		contentProvider = PapersWithCodeContentProvider()
		content = contentProvider.get_content()

		# Here's where we check that the content is as expected.
		expected_content = {
			"title": "Example Paper",
			"subtitle": "This is an example abstract.",
			"media": "https://example.com/image.jpg",
			"tags": ["Tag1", "Tag2"],
			"stars": 123,
			"github_link": "https://github.com/example",
			"uid": "/paper/example-paper",
			"abstract": "This is the full abstract of the paper.",  # Abstract from individual paper's page
			"arxiv_url": "https://arxiv.org/abs/example",  # arXiv URL from individual paper's page
		}
		expected_content = {"paper" : json.dumps(expected_content)}
		self.assertEqual(content[0], expected_content)

