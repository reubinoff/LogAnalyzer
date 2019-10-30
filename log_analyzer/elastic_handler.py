from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import logging

def get_elastic():
    """ get elasticsearch handler """
    # https://elasticsearch-py.readthedocs.io/en/master/api.html
    es = Elasticsearch()
    logger = logging.getLogger("elasticsearch")
    logger.setLevel(logging.WARN)

    logger = logging.getLogger("urllib3.connectionpool")
    logger.setLevel(logging.WARN)
    return es

def put_mapping(data):
    """ Adds new fields to an existing index or changes the search settings of existing fields """
    # from https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-put-mapping.html
    es = get_elastic()
    
    for index, mapping in data.items():
        if es.indices.exists(index):
            es.indices.delete(index)
        res = es.indices.create(index=index, body=dict({"mappings":{"properties": mapping}}))
        print(res)