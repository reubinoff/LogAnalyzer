import os
import argparse
import logging
import json
import ntpath

from datetime import datetime

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

from log_analyzer.indexer import Indexer

CONFIG = {
    ""
}

def set_logger():
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    # filename='/var/log/app.log',
                    filemode='a')

def setup_elastic():
    es = Elasticsearch()
    return es

def _get_parse_data(parse_file_path):
    parse_data = None
    if parse_file_path is None:
        parse_file_path = CONFIG
    else:
        if os.path.exists(parse_file_path) is False:
            return None
        with open(parse_file_path, 'r') as f:
            parse_data = json.load(f)
    return parse_data

def _get_giles_to_search(parse_data):
    return []

def _get_all_full_path_files_in_dir(dir_name):
    files = []
    for dirpath, _, filenames in os.walk(dir_name):
        for _file in filenames:
            files.append(os.path.join(dirpath, _file))
    return files

def _path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def index_logs(log_folder_path, parse_file_path, elasticsearch_instances):
    parse_data = _get_parse_data(parse_file_path)
    
    # get all the files from the config to search
    files_to_search = _get_giles_to_search(parse_data)

    # get all logs to read
    files = _get_all_full_path_files_in_dir(log_folder_path)
    relevant_files = [f for f in files if _path_leaf(f) in files_to_search]
    for _file in relevant_files:
        _indexer = Indexer(elasticsearch_instances, _file, parse_data)
        _indexer.index()



def main(log_folder_path, parse_file_path):
    set_logger()
    logging.info("")
    logging.info("#################################")
    logging.info("######   Quali  Analyzer   ######")
    logging.info("#################################")
    logging.info("")
    es = setup_elastic()
    index_logs(log_folder_path, parse_file_path, es)




if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.realpath(__file__))
    parser = argparse.ArgumentParser()
    parser.add_argument('--logs-folder', default='c:\\logs', help='folder of the logs')
    parser.add_argument('--parse-file-path', default=None, help='path to the json file which has the parsing details')
    
    args = parser.parse_args()

    main(args.logs_folder, args.parse_file_path)





    # doc = {
    # 'author': 'kiqweqweqweqwemchy',
    # 'text': 'Elasticsearch: cool. bonsai cool.',
    # 'timestamp': datetime.now(),
    # }
    # res = es.index(index="test-index", doc_type='tweet',  body=doc)
    # logging.info(res['result'])
    # res = es.get(index="test-index", doc_type='tweet', id=1) 
    # logging.info(res['_source'])
    # search_body = {
    #     "query": {
    #         "match": {
    #             "author":   "kiqweqweqweqwemchy"
    #         }
    #     }
    # }
    # res = es.search(index="test-index", body=search_body) 
    # logging.info(res)
    # s = Search().query("match", author="kiqweqweqweqwemchy")