from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

def get_elastic():
    es = Elasticsearch()
    return es