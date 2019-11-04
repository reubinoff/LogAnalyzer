from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import logging



# Factory to generate ES handler. put the factory in singleton which get the configuration from the config at once,
# and return factory instance for relevant configuration. the factory will create new ES instance for each call of get_elastic

class ElasticSearchFactory(object):
    _host = None
    _port = None
    _instance = None

    @staticmethod
    def getInstance():

        if(ElasticSearchFactory._instance is None):
            ElasticSearchFactory._instance = ElasticSearchFactory()

        return ElasticSearchFactory._instance

    def config(self, host, port):
        self._host = host
        self._port = port

    def get_elastic(self):
        if self._host is None or self._port is None:
            logging.error("Please run factory config before create instance")
            return None
        return self._create__elastic()

    def _create__elastic(self):
        """ get elasticsearch handler """
        # https://elasticsearch-py.readthedocs.io/en/master/api.html
        es = Elasticsearch([{'host': self._host, 'port': self._port}])
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






