import base64
from behave.formatter.base import Formatter
from behave.model_core import Status
import six
import json


class BehaveFormatter(Formatter):
    name = "json"
    description = "JSON dump of test run"
    dumps_kwargs = {}
    split_text_into_lines = True

    json_number_types = six.integer_types + (float,)
    json_scalar_types = json_number_types + (six.text_type, bool, type(None))

    def __init__(self, stream_opener, config):
        super(BehaveFormatter, self).__init__(stream_opener, config)
        self.stream = self.open()
        self.feature_count = 0
        self.current_feature = None
        self.current_feature_data = None
        self.current_scenario = None
        self._step_index = 0

    def reset(self):
        self.current_feature = None
        self.current_feature_data = None
        self.current_scenario = None
        self._step_index = 0

    def uri(self, uri):
        pass

    def feature(self, feature):
        self.reset()
        self.current_feature = feature
        self.current_feature_data = {
            "keyword": feature.keyword,
            "name": feature.name,
            "tags": list(feature.tags),
            "location": six.text_type(feature.location),
            "status": None,
        }
        element = self.current_feature_data
        if feature.description:
            element["description"] = feature.description

    def background(self, background):
        element = self.add_feature_element({
            "type": "background",
            "keyword": background.keyword,
            "name": background.name,
            "location": six.text_type(background.location),
            "steps": [],
        })
        if background.name:
            element["name"] = background.name
        self._step_index = 0

        for step_ in background.steps:
            self.step(step_)

    def scenario(self, scenario):
        self.finish_current_scenario()
        self.current_scenario = scenario

        element = self.add_feature_element({
            "type": "scenario",
            "keyword": scenario.keyword,
            "name": scenario.name,
            "tags": scenario.tags,
            "location": six.text_type(scenario.location),
            "steps": [],
            "status": None,
        })
        if scenario.description:
            element["description"] = scenario.description
        self._step_index = 0

    @classmethod
    def make_table(cls, table):
        table_data = {
            "headings": table.headings,
            "rows": [list(row) for row in table.rows]
        }
        return table_data

    def step(self, step):
        s = {
            "keyword": step.keyword,
            "step_type": step.step_type,
            "name": step.name,
            "location": six.text_type(step.location),
        }

        if step.text:
            text = step.text
            if self.split_text_into_lines and "\n" in text:
                text = text.splitlines()
            s["text"] = text
        if step.table:
            s["table"] = self.make_table(step.table)
        element = self.current_feature_element
        element["steps"].append(s)

    def match(self, match):
        args = []
        for argument in match.arguments:
            argument_value = argument.value
            if not isinstance(argument_value, self.json_scalar_types):
                argument_value = argument.original
            assert isinstance(argument_value, self.json_scalar_types)
            arg = {
                "value": argument_value,
            }
            if argument.name:
                arg["name"] = argument.name
            if argument.original != argument_value:
                arg["original"] = argument.original
            args.append(arg)

        match_data = {
            "location": six.text_type(match.location) or "",
            "arguments": args,
        }
        if match.location:
            steps = self.current_feature_element["steps"]
            steps[self._step_index]["match"] = match_data

    def result(self, result):
        steps = self.current_feature_element["steps"]
        steps[self._step_index]["result"] = {
            "status": result.status.name,
            "duration": result.duration,
        }
        if result.error_message and result.status == Status.failed:
            error_message = result.error_message
            if self.split_text_into_lines and "\n" in error_message:
                error_message = error_message.splitlines()
            result_element = steps[self._step_index]["result"]
            result_element["error_message"] = error_message
        self._step_index += 1

    def embedding(self, mime_type, data):
        step = self.current_feature_element["steps"][-1]
        step["embeddings"].append({
            "mime_type": mime_type,
            "data": base64.b64encode(data).replace("\n", ""),
        })

    def eof(self):
        if not self.current_feature_data:
            return

        self.finish_current_scenario()
        self.update_status_data()

        if self.feature_count == 0:
            self.write_json_header()
        else:
            self.write_json_feature_separator()

        self.write_json_feature(self.current_feature_data)
        self.reset()
        self.feature_count += 1

    def close(self):
        if self.feature_count == 0:
            self.write_json_header()
        self.write_json_footer()
        self.close_stream()

    def add_feature_element(self, element):
        assert self.current_feature_data is not None
        if "elements" not in self.current_feature_data:
            self.current_feature_data["elements"] = []
        self.current_feature_data["elements"].append(element)
        return element

    @property
    def current_feature_element(self):
        assert self.current_feature_data is not None
        return self.current_feature_data["elements"][-1]

    def update_status_data(self):
        assert self.current_feature
        assert self.current_feature_data
        self.current_feature_data["status"] = self.current_feature.status.name

    def finish_current_scenario(self):
        if self.current_scenario:
            status_name = self.current_scenario.status.name
            self.current_feature_element["status"] = status_name

    def write_json_header(self):
        self.stream.write("[\n")

    def write_json_footer(self):
        self.stream.write("\n]\n")

    def write_json_feature(self, feature_data):
        self.stream.write(json.dumps(feature_data, **self.dumps_kwargs))
        self.stream.flush()

    def write_json_feature_separator(self):
        self.stream.write(",\n\n")
