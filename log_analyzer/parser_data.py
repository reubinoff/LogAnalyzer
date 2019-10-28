import logging
import ntpath
import re

class ParseLookupIndex(object):
    """
    {
        "name": JOB_ID,
        "start_delimiter": "resolve for Job",
        "end_delimiter": ","
    }
    """

    def __init__(self, lookup_index_raw_data):
        self._lookup_index_raw_data = lookup_index_raw_data
        self._name = None
        self._start_delimiter = None
        self._end_delimiter = None
        self._parse()
    
    def _parse(self):
        if "name" not in self._lookup_index_raw_data:
            raise KeyError("name")
        if "start_delimiter" not in self._lookup_index_raw_data:
            raise KeyError("start_delimiter")
        self._name = self._lookup_index_raw_data["name"]
        self._start_delimiter = self._lookup_index_raw_data["start_delimiter"]
        self._end_delimiter = self._lookup_index_raw_data.get("end_delimiter")
    

class ParseLookup(object):
    """
    {
        "name": "start reservation",
        "search_str": "Start Topology resolve for Job",
        "index": [
            {
                "name": JOB_ID,
                "start_delimiter": "resolve for Job",
                "end_delimiter": ","
            }
        ]
    }
    """
    def __init__(self, lookup_raw_data):
        self._lookup_raw_data = lookup_raw_data
        self._name = None
        self._search_str = None
        self._index = []
        self._parse()
        

    def _parse(self):
        if "name" not in self._lookup_raw_data:
            raise KeyError("name")
        if "search_str" not in self._lookup_raw_data:
            raise KeyError("search_str")
        if "index" not in self._lookup_raw_data or isinstance(self._lookup_raw_data.get("index"), list) is False:
            raise KeyError("index")
        self._name = self._lookup_raw_data["name"]
        self._search_str = self._lookup_raw_data["search_str"]
        for index in self._lookup_raw_data["index"]:
            p = ParseLookupIndex(index)
            self._index.append(p)


class SignleParseData(object):
    
    def __init__(self, name, data):
        self._raw_data = data
        self._name = name
        self._log_files = []
        self._lookup_parsers = []
        self._parse()

    @property
    def files(self):
        return self._log_files

    def _parse_logs_files(self):
        if "log_files" not in self._raw_data or isinstance(self._raw_data.get("log_files"), list) is False:
            raise KeyError("log_files")
        else:
            self._log_files = self._raw_data.get("log_files")
        
    def _parse(self):
        self._parse_logs_files()
        for lookup in self._raw_data["lookup"]:
            p = ParseLookup(lookup)
            self._lookup_parsers.append(p)

    
    def _get_file_name(self, path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def is_parser_relevant_for_file(self, file_name):
        _file_name = self._get_file_name(file_name)
        return any([ bool(re.match(f, _file_name)) is True for f in self._log_files])

class ParserData(object):
    def __init__(self, parse_raw_data):
        self._raw_data = parse_raw_data
        self._is_valid = False
        self._parsers = []
        self._parse()

    @property
    def valid(self):
        return self._is_valid

    def get_all_files(self):
        """ get all the files from the config to search """
        files = set()
        for a in self._parsers:
            files.update(a.files)
        return list(files)

    def _deep_parse(self):
        if "patterns" not in self._raw_data:
            raise KeyError("patterns")
        pattern_data = dict(self._raw_data.get("patterns"))
        
        for name, pattern in pattern_data.items():
            s = SignleParseData(name, pattern)
            self._parsers.append(s)


    def _parse(self):
        try:
            self._deep_parse()
        except Exception as e:
            logging.exception(str(e))
            self._is_valid = False
            return
        self._is_valid = True

    def get_parsers_for_file_name(self, file_name):
        """ get parser which relevant for specific file """
        parsers = [p for p in self._parsers if p.is_parser_relevant_for_file(file_name) is True]
        return parsers

# CONFIG = {
#     PATTERNS: {
#         "Blueprint resolution": {
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
#     }


# }
