
from log_analyzer.elastic_handler import get_elastic

CONFIG = {
    "analyze":[
        {
            "name": "reservation",
            "description": "measure the duration of reservation",
            "indices": [
                {
                    "keys": ["job_id", "reservation_id", "topology_id"],
                    "indice_items": {
                        "start_reservation": {
                            "fields": [
                                "time"
                            ]
                        },
                        "end_reservation": {
                            "fields": [
                                "time"
                            ]
                        }
                    },
                    "measurment":{
                        "test":[
                            {
                                "name": "time_perioed",
                                "type": "time_between_indices",
                                "args": ["start_reservation", "end_reservation"]
                            }
                        ]
                    }
                }
            ]
        }
    ]
}
class AnalyzeItem(object):
    def __init__(self, analyze_data):
        self._es = get_elastic()
        self._data = analyze_data
        self._name = self._data["name"]
        self._description = self._data["description"]
        self._indices = self._data["indices"]

    def _get_query(self):
        q = dict({
            "query": {
                "match_all": {}
            },
            "aggs": {
                "bulks": {
                    "terms": {
                        "field": "reservation_id.keyword",
                        "size": 10
                    },
                    "aggs": {
                        "orders": {
                            "top_hits": {
                                "size": 10
                            }
                        }
                    }
                }
            }
        })
        return q
    def analyze(self):
        res = self._es.search(index="3rd", body=self._get_query()) 
        print(res)
            


class AnalyzerEngine(object):
    def __init__(self):
        self._data = CONFIG
    

    def run(self):
        for analyze_item in self._data.get("analyze", []):
            item = AnalyzeItem(analyze_item)
            item.analyze()


