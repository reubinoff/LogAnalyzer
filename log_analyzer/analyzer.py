import os
import argparse
import logging
import json
import ntpath
import re

from datetime import datetime
from multiprocessing import Pool
from itertools import repeat

from log_analyzer.indexer import Indexer
from log_analyzer.parser_data import ParserData
from log_analyzer.analyzer_engine import AnalyzerEngine
from log_analyzer.elastic_handler import put_mapping
from log_analyzer.report_manager import ReportManager

DEBUG = True
 

def set_logger():
    formatter = '%(asctime)s >> %(processName)s %(threadName)s >> %(name)-6s %(levelname)-8s %(message)s'
    logging.basicConfig(level=logging.DEBUG,
                    format=formatter,
                    datefmt='%m-%d %H:%M',
                    # filename='/var/log/app.log',
                    filemode='a')
    fh = logging.FileHandler('log_analyzer.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(formatter))
    logging.getLogger().addHandler(fh)


def _get_parse_data(parse_file_path):
    parse_data = None
    if parse_file_path is None:
        dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        with open(os.path.join(dir_path, "config.json"), "r") as f:
            parse_data = json.load(f)
    else:
        if os.path.exists(parse_file_path) is False:
            raise FileNotFoundError(parse_file_path)
        with open(parse_file_path, 'r') as f:
            parse_data = json.load(f)
    return parse_data

def _get_all_full_path_files_in_dir(dir_name):
    """ get all logs to read """
    files = []
    for dirpath, _, filenames in os.walk(dir_name):
        for _file in filenames:
            files.append(os.path.join(dirpath, _file))
    return files

def _path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def _get_relevant_files_from_pattern(parse_data_handler, log_folder_path):
    files_pattern_to_search = parse_data_handler.get_all_files()
    files = _get_all_full_path_files_in_dir(log_folder_path)
    relevant_files = []
    for f in files:
        file_name = _path_leaf(f)
        for pattern in files_pattern_to_search:
            if bool(re.match(pattern, file_name)) is True:
                relevant_files.append(f)
    return relevant_files

def _index_file(_file, parse_data_handler):
    _indexer = Indexer(_file, parse_data_handler)
    return _indexer.index()


def index_logs(log_folder_path, parse_data_handler):
   
    mapping = parse_data_handler.get_es_mapping_data()
    put_mapping(mapping)
    relevant_files = _get_relevant_files_from_pattern(parse_data_handler, log_folder_path)

    results = []
    if DEBUG: # remove parallel
        for _file in relevant_files:
            results.append(_index_file(_file, parse_data_handler))
    else:
        with Pool(processes=10) as _pool:
            results = _pool.starmap(_index_file, zip(relevant_files, repeat(parse_data_handler)))
    print (results)


def analyze_logs(parse_data):
    engine = AnalyzerEngine(parse_data["analyze"])
    return engine.run()

def main(log_folder_path, parse_file_path):
    set_logger()
    logging.info("")
    logging.info("#################################")
    logging.info("######   Quali  Analyzer   ######")
    logging.info("#################################")
    logging.info("")
    parse_data = _get_parse_data(parse_file_path)
    parse_data_handler = ParserData(parse_data)
    
    # index results in ES
    index_logs(log_folder_path, parse_data_handler)

    # analyze ES data
    results = analyze_logs(parse_data)

    #publish the results
    reporter = ReportManager(parse_data["report"], results)
    reporter.publish()





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
