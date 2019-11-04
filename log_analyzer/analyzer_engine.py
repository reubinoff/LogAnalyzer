
import logging

from log_analyzer.elastic_handler import ElasticSearchFactory

MAX_RESULT = 1000

class AnalyzeItem(object):
    def __init__(self, analyze_data):
        self._es = ElasticSearchFactory.getInstance().get_elastic()
        self._data = analyze_data
        self._name = self._data["name"]
        self._description = self._data["description"]
        self._measurment = self._data["measurment"]
        self._enabled = self._data.get("enabled", True)

    @property
    def enabled(self):
        return self._enabled

    def _invoke_tests(self):
        test_results = {}
        for test in self._measurment["tests"]:
            try:
                test_cb = self._get_measurment(test["name"])
            except Exception as e:
                logging.error("Failed to find test: " + test["name"])
                continue
            test_data = self._measurment["data"]
            result = test_cb(test_data, test["args"])
            test_results.update({test["name"]: result})
        return test_results
        

    def _get_measurment(self, name):
        return getattr(self, "_measurment_" + name)


    def _get_q_by_time(self, minimum_time, with_sort=False):
        search_body = {
            "query": {
                "range": {
                    "time": {
                        "gte": minimum_time
                    }
                }
            }
        }
        if with_sort is True:
            search_body.update({"sort" : [{"time": "asc"}]})
        return search_body
    def _get_q_by_value(self, values = None, first_time=1000, with_sort=False):
        data = self._get_q_by_time(first_time, with_sort)
        if values is not None:
            new_data = {}
            vals = [{"match": {k:v}} for k,v in values.items()]
            new_data["query"] ={"bool": { "must": [data["query"], *vals]}}
            data = new_data
        return data

    def _get_source_data(self, es_result):
        if isinstance(es_result, list):
            return  [i["_source"] for i in es_result]
        else:
            return es_result["_source"]
    
    def _measurment_count_events(self, measurment_data, test_args=None):
        # sample_period_in_sec
        test_result = []
        event_pairs = []
        init_time = None
        end_time = None
        indexes = measurment_data.get("index_items")
        if len(indexes) != 2:
            raise Exception("Invalid Parameters for test time_perioed")
        first_arg = test_args["first_index"]

        items = self._get__all_results(first_arg)
        itesm_src = self._get_source_data(items)
        
        second_arg = [x for x in indexes if x!=first_arg][0]
        for result in itesm_src:
            values = dict()
            try:
                values = {key: result[key] for key in measurment_data["keys"]}
            except Exception as e:
                logging.fatal(e)
            results = self._get__all_results(second_arg, values)
            data = self._get_source_data(results)
            if len(data) == 0:
                logging.warning("for test time_perioed didnt find the second value")
                continue
        
            if init_time is None:
                init_time = result["time"]
                end_time = init_time
            arg_2 = data[0]

            end_time = end_time if end_time > arg_2["time"] else arg_2["time"]
            event_pairs.append((result["time"], arg_2["time"]))

        if end_time is None:
            logging.warning("No result found for " +self._name)
            return []
            
        sample_period_in_sec = test_args["sample_period_in_sec"]
        times_array = range(round(init_time)-1, round(end_time)+1, int(sample_period_in_sec))

        results_time = []
        for time_item in times_array:
            results = len(list(filter(lambda x: x[0] <= time_item <= x[1], event_pairs)))
            results_time.append({
                "time": time_item,
                "total": results
            })
        return results_time

    def _measurment_time_perioed(self, measurment_data, test_args=None):
        test_result = []
        indexes = measurment_data.get("index_items")
        if len(indexes) != 2:
            raise Exception("Invalid Parameters for test time_perioed")
        first_arg = test_args["first_index"]
     
        items = self._get__all_results(first_arg)
        itesm_src = self._get_source_data(items)
        
        second_arg = [x for x in indexes if x!=first_arg][0]
        for result in itesm_src:
            values = {key: result[key] for key in measurment_data["keys"]}
            results = self._get__all_results(second_arg, values)
            data = self._get_source_data(results)
            if len(data) == 0:
                logging.warning("for test time_perioed didnt find the second value")
                continue
            arg_2 = data[0]
            threshold = test_args["threshold"]
            diff = float(arg_2["time"]) - float(result["time"])
            
            is_passed =  diff < threshold.get("max", 60 * 60 * 24) and diff > threshold.get("min",-1)
            test_result.append({"result": is_passed, "time": diff})
        return test_result

    def _get__all_results(self, index, query = None, first_time=1000):
        search_body = self._get_q_by_value(query, first_time, with_sort=False)
        res = self._es.count(index=index, body=search_body)
        total_results = res["count"]
        _from = 0
        hits = []
        search_body = self._get_q_by_value(query, first_time, with_sort=True)
        while total_results > MAX_RESULT * (_from):
            search_body.update({
                "from": _from,
                "size": MAX_RESULT
            })
            res = self._es.search(index=index, body=search_body)
            hits.extend(res["hits"]["hits"])
            _from = _from + 1
        return hits
        
    def analyze(self):
        result = {self._name: self._invoke_tests()}
        return result
            


class AnalyzerEngine(object): 
    def __init__(self, parse_data):
        self._data = parse_data
    

    def run(self):
        results = {}
        for analyze_item in self._data:
            item = AnalyzeItem(analyze_item)
            if item.enabled:
                res = item.analyze()
                results.update(res)
        return results


