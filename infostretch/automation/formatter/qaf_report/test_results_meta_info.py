import json
import os


class ReportsMetaInfo:
    def __init__(self, path_to_write):
        self.__meta_info_file_path = os.path.join(path_to_write, 'meta-info.json')

        self.name = ''
        self.dir = ''
        self.startTime = ''

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def dir(self):
        return self.__dir

    @dir.setter
    def dir(self, value):
        self.__dir = value

    @property
    def startTime(self):
        return self.__startTime

    @startTime.setter
    def startTime(self, value):
        self.__startTime = value

    def __dump_into_json(self):
        _dict = {
            "name": self.name,
            "dir": self.dir,
            "startTime": self.startTime,
        }
        if os.path.exists(self.__meta_info_file_path):
            with open(self.__meta_info_file_path, "r") as jsonFile:
                data = json.load(jsonFile)
                reports = data['reports']
        else:
            reports = []
        reports.insert(0, _dict)
        final_data = {'reports': reports}

        with open(self.__meta_info_file_path, 'w') as fp:
            json.dump(final_data, fp, sort_keys=True, indent=4)

    def close(self):
        self.__dump_into_json()
