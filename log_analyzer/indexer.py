import logging 

from log_analyzer.elastic_handler import ElasticSearchFactory
from elasticsearch import helpers

MAX_CHUNK_SIZE = 1000

class Indexer(object):
    def __init__(self, file_to_index, parser_data):
        self._es = ElasticSearchFactory.getInstance().get_elastic()
        self._file = file_to_index
        self._parser_data_object = parser_data
    
    def _get_lines(self):
        lines = None
        with open(self._file) as fp:
            lines = [line.rstrip('\n') for line in fp]
        return lines

    def index(self):
        lines = self._get_lines()
        parsers = self._parser_data_object.get_parsers_for_file_name(self._file)
        indexes = set()
        data_to_index = []
        for l in lines:
            for parser in parsers:
                val = parser.parse_string(l)
                if len(val) > 0:
                    for key, value in dict(val).items():
                        indexes.add(key)
                        data = { i["name"] : i["value"]  for i in value }
                        data_to_index.append({
                            "_index": key,
                            "_source": data
                        })
                        # res = self._es.index(index=key, body=data)
        

        r = helpers.bulk(self._es, data_to_index, chunk_size=MAX_CHUNK_SIZE)
        self._es.indices.refresh()

        logging.info("Total scanned lines in file {} is {}".format(self._file, len(lines)))
        return True
    
