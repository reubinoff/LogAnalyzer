import json

class ReportManager(object):
    def __init__(self, report_config, report_data):
        self._report_config = report_config
        self._report_data = report_data

    def publish(self):
        with open(self._report_config.get("report_file_name", "log_analyzer_result.json"), 'w') as f:
            json.dump(self._report_data, f, indent=4)
        