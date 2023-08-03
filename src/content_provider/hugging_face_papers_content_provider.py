import requests
from bs4 import BeautifulSoup
import json
from src.content_provider.content_provider import ContentProvider
class HuggingFacePapersContentProvider(ContentProvider):
    def __init__(self):
        super().__init__()

    def name(self):
        return "HuggingFacePapersContentProvider"