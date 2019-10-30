
from log_analyzer.elastic_handler import get_elastic

CONFIG = {
    "analyze":[
        {
            "name": "reservation",
            "description": "measure the duration of reservation",
            "measurment": {
                "data": {
                    "keys": ["job_id", "reservation_id", "topology_id"],
                    "index_items": {
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
                    }
                },
                "tests":[{
                    "name": "time_perioed",
                    "args": {
                            "first_index": "start_reservation"
                    }
                }]
            }

        }
    ]
}
class AnalyzeItem(object):
    def __init__(self, analyze_data):
        self._es = get_elastic()
        self._data = analyze_data
        self._name = self._data["name"]
        self._description = self._data["description"]
        self._measurment = self._data["measurment"]

    def _invoke_tests(self):
        test_results = {}
        for test in self._measurment["tests"]:
            test_cb = self._get_measurment(test["name"])
            test_data = self._measurment["data"]
            result = test_cb(test_data, test["args"])
            test_results.update({test["name"]: result})
        return test_results
        

    def _get_measurment(self, name):
        return getattr(self, "_measurment_" + name)


    def _measurment_time_perioed(self, measurment_data, test_args=None):
        indexes = measurment_data.get("index_items")
        if len(indexes.keys()) != 2:
            raise Exception("Invalid Parameters for test time_perioed")
        first_arg = test_args["first_index"]
        
    def analyze(self):
        result = {self._name: self._invoke_tests()}
        print(result)
        return result
            


class AnalyzerEngine(object):
    def __init__(self):
        self._data = CONFIG
    

    def run(self):
        for analyze_item in self._data.get("analyze", []):
            item = AnalyzeItem(analyze_item)
            item.analyze()


