from langchain.chains.base import Chain
from src.content_provider import ContentProvider
from typing import List
import requests
import json
import logging
class Reporter:
    def __init__(self, content_providers: List[ContentProvider], llm_chain: Chain, logger: logging.Logger = None):

        if not isinstance(llm_chain, Chain):
            raise TypeError('llm_chain must be an instance of Chain')
        if not isinstance(content_providers, list) or len(content_providers) == 0:
            raise ValueError('content_providers must be a list with at least one ContentProvider')
        if not all(isinstance(cp, ContentProvider) for cp in content_providers):
            raise TypeError('All content_providers must be instances of ContentProvider')
        self._content_providers = content_providers
        self._llm_chain = llm_chain
        self._logger = logger


    def report(self):
        self._logger.info("Starting reporting")
        reports = []
        for content_provider in self._content_providers:
            try:
                contents = content_provider.get_content()
                self._logger.info(f"Got {len(contents)} contents from {content_provider.name()}")
                for content in contents:
                    post = self._llm_chain.run(content)
                    report = {"report" : {"post": post, 'content_provider': content_provider.name()}}
                    reports.append(report)
                    self._logger.info(json.dumps(report))
            except requests.exceptions.HTTPError as e:
                self._logger.error(f"Error getting content from {content_provider.name()}: {e}")
                self._logger.info(f"Got 0 contents from {content_provider.name()}")
        self._logger.info("Finished reporting")
        return reports