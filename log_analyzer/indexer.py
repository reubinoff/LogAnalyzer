import logging 

from log_analyzer.elastic_handler import get_elastic

class Indexer(object):
    def __init__(self, file_to_index, parser_data):
        self._es = get_elastic()
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
        for l in lines:
            for parser in parsers:
                val = parser.parse_string(l)
                if len(val) > 0:
                    for key, value in dict(val).items():
                        data = { i["name"] : i["value"]  for i in value }
                        data.update({"event": key})
                        res = self._es.index(index="3rd", body=data)
        logging.info("Total scanned lines in file {} is {}".format(self._file, len(lines)))
        return True
    
        

#   "Blueprint resolution": {
#             "log_files": [
#                 "JobPerformance.txt.*"
#             ],
#             "lookup": [
#                 {
#                     "name": "start reservation",
#                     "search": "Start Topology resolve for Job",
#                     "index": [
#                         {
#                             "name": JOB_ID,
#                             "start_delimiter": "resolve for Job",
#                             "end_delimiter": ","
#                         },
#                         {
#                             "name": RESERVATION_ID,
#                             "start_delimiter": "creating Reservation",
#                             "end_delimiter": ","
#                         },
#                         {
#                             "name": TOPOLOGY_ID,
#                             "start_delimiter": "Topology Id",
#                             "end_delimiter": ","
#                         }
#                     ]
#                 },
#                 {
#                     "name": "end reservation",
#                     "search": "Topology resolve Succeeded for Job",
#                     "index": [
#                         {
#                             "name": JOB_ID,
#                             "start_delimiter": "for Job",
#                             "end_delimiter": ","
#                         },
#                         {
#                             "name": RESERVATION_ID,
#                             "start_delimiter": "creating Reservation",
#                             "end_delimiter": ","
#                         },
#                         {
#                             "name": TOPOLOGY_ID,
#                             "start_delimiter": "Topology Id",
#                             "end_delimiter": ","
#                         }
#                     ]
#                 }
#             ]
#         }