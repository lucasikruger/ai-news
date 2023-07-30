from langchain.chains.base import Chain
from src.content_provider import ContentProvider
from src.data_storage import DataStorage
from typing import List
import requests
import json
import logging
from datetime import datetime
import hashlib
class Reporter:
    def __init__(self, content_providers: List[ContentProvider], llm_chain: Chain, logger: logging.Logger, data_storage: DataStorage):

        self.validate_inputs_types(content_providers, llm_chain, logger, data_storage)
        self._content_providers = content_providers
        self._llm_chain = llm_chain
        self._logger = logger
        self._data_storage = data_storage

    def validate_inputs_types(self, content_providers, llm_chain, logger, data_storage):
        if not isinstance(llm_chain, Chain):
            raise TypeError('llm_chain must be an instance of Chain')
        if not isinstance(content_providers, list) or len(content_providers) == 0:
            raise ValueError('content_providers must be a list with at least one ContentProvider')
        if not all(isinstance(cp, ContentProvider) for cp in content_providers):
            raise TypeError('All content_providers must be instances of ContentProvider')
        if not isinstance(logger, logging.Logger):
            raise TypeError('logger must be an instance of logging.Logger')
        if not isinstance(data_storage, DataStorage):
            raise TypeError('data_storage must be an instance of DataStorage')
        
        
    def get_timestamp(self):
        return int(datetime.utcnow().timestamp())
    def create_id(self,json_obj):
        json_str = json.dumps(json_obj, sort_keys=True) # Sort keys to ensure consistent ordering
        return hashlib.sha256(json_str.encode()).hexdigest()
    def report(self):
        self._logger.info('Starting reporting')
        all_reports = []
        for content_provider in self._content_providers:
            reports = self.get_reports_from_content_provider(content_provider)
            all_reports.extend(reports)
            if len(reports) > 0:
                self._data_storage.save_reports(content_provider.name(), reports)
        self._logger.info('Finished reporting')
        return all_reports



    def get_reports_from_content_provider(self, content_provider):
        reports = []
        try:
            contents = content_provider.get_content()
            self._logger.info(f'Got {len(contents)} contents from {content_provider.name()}')
            for content in contents:
                content_str = json.dumps(content)
                id = self.create_id(json.loads(content_str))
                if not self._data_storage.exists(content_provider.name(), id):
                    post = self._llm_chain.run(content)
                    report = {'content': json.loads(content_str),'report' : {'post': post, 'content_provider': content_provider.name()},'id': id, 'timestamp': self.get_timestamp()}
                    reports.append(report)
                    self._logger.info(json.dumps(report))
                else:
                    self._logger.info(f'Content {json.loads(content_str)} already exists in {content_provider.name()}')
        except requests.exceptions.HTTPError as e:
            self._logger.error(f'Error getting content from {content_provider.name()}: {e}')
            self._logger.info(f'Got 0 contents from {content_provider.name()}')
        return reports