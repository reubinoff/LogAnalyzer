import logging 


class Indexer(object):
    def __init__(self, elasticsearch_instances, file_to_index, parser_data):
        self._es = elasticsearch_instances
        self._file = file_to_index
        self._parser = parser_data
    
    def _get_lines(self):
        lines = None
        with open(self._file) as fp:
            lines = [line.rstrip('\n') for line in fp]
        return lines

    def index(self):
        lines = self._get_lines()
        logging.info("Total scanned lines in file {} is {}".format(self._file, len(lines)))

        return True
        

        