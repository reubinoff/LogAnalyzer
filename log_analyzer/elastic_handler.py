from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import logging

class ElasticSearchService(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def get_elastic(self):
        """ get elasticsearch handler """
        # https://elasticsearch-py.readthedocs.io/en/master/api.html
        es = Elasticsearch()
        logger = logging.getLogger("elasticsearch")
        logger.setLevel(logging.WARN)

        logger = logging.getLogger("urllib3.connectionpool")
        logger.setLevel(logging.WARN)
        return es

    def put_mapping(self, data):
        """ Adds new fields to an existing index or changes the search settings of existing fields """
        # from https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-put-mapping.html
        es = self.get_elastic()

        for index, mapping in data.items():
            if es.indices.exists(index):
                es.indices.delete(index)
            res = es.indices.create(index=index, body=dict({"mappings":{"properties": mapping}}))
            print(res)

# Factory to generate ES handler. put the factory in singleton which get the configuration from the config at once,
# and return factory instance for relevant configuration. the factory will create new ES instance for each call of get_elastic

class ElasticSearchFactory:
    _host = ''
    _port = 0
    _ElasticSearchFactory = None

    def __init__(self):
        _ElasticSearchFactory = ElasticSearchFactory()

    @staticmethod
    def getInstance():
        global _ElasticSearchFactory
        return _ElasticSearchFactory

    def config(host, port):
        _host = host
        _port = port

    def get_elastic(self):
        global _host, _port
        return ElasticSearchService(_host, _port)







