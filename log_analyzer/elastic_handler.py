from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import logging

def get_elastic():
    es = Elasticsearch()
    logger = logging.getLogger("elasticsearch")
    logger.setLevel(logging.WARN)

    logger = logging.getLogger("urllib3.connectionpool")
    logger.setLevel(logging.WARN)
    return es