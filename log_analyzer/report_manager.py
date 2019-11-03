import json
import datetime
import logging
from log_analyzer.elastic_handler import get_elastic
from elasticsearch import helpers

MAX_CHUNK_SIZE = 1000

class ReportManager(object):
    def __init__(self, report_config, report_data):
        self._report_config = report_config
        self._report_data = report_data
        self._es = get_elastic()

    def publish(self):
        with open(self._report_config.get("report_file_name", "log_analyzer_result.json"), 'w') as f:
            json.dump(self._report_data, f, indent=4)
        
        report_id = self._report_config.get("report_id", datetime.datetime.now().timestamp())


        total_results_data = []
        for analyze_name, analyze_value in  self._report_data.items():
            for test_name, test_results in analyze_value.items():
                index_name = F"{analyze_name.rstrip()}_{test_name.rstrip()}_{report_id}".lower()
                if self._es.indices.exists(index_name):
                    self._es.indices.delete(index_name)
                    self._es.indices.create(index=index_name)
                # res = self._es.bulk(index=index_name, body={"index": test_results})

                actions = [
                    {
                        "_index": index_name,
                        "_source": r
                    }
                    for r in test_results]
                total_results_data.extend(actions)
        r = helpers.bulk(self._es, total_results_data, chunk_size=MAX_CHUNK_SIZE)
        logging.info("Total results: {}".format(len(total_results_data)))


