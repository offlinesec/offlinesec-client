from datetime import datetime
import yaml
import os


class SAPSystem:
    def __init__(self, system_name=""):
        self.system_name = system_name

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def parse_exclude_file(exclude_yaml_file, root_dir, system_name):
        if exclude_yaml_file is None or exclude_yaml_file == "":
            return list()
        if root_dir:
            path = os.path.join(root_dir, exclude_yaml_file)
        else:
            path = exclude_yaml_file
        if not os.path.exists(path):
            raise FileNotFoundError("File %s not found" % (path,))

        if not exclude_yaml_file.upper().endswith(".YAML"):
            raise ValueError("File {} has wrong extension. Only YAML file supported".format(exclude_yaml_file))
        try:
            with open(path, 'r', encoding="utf-8") as f:
                file_content = yaml.safe_load(f)
        except:
            raise ValueError("File {} has wrong structure. Only YAML files supported".format(path))
        else:
            outlist = list()
            note_num = 0
            for item in file_content:
                note_num += 1
                if "note" not in item.keys():
                    print("[WARNING] System {} File {} note {} has no key 'note'".format(system_name,
                                                                                         exclude_yaml_file,
                                                                                         str(note_num)))
                    continue

                try:
                    note_id = int(item["note"])

                except ValueError as err:
                    print("[WARNING] System {} File {} contains wrong Note ID {}".format(system_name,
                                                                                         exclude_yaml_file,
                                                                                         item["note"]))
                    continue

                until_date = item["until"] if "until" in item.keys() else ""
                comment = item["comment"] if "comment" in item.keys() else ""
                if until_date:
                    try:
                        until = datetime.strptime(until_date, "%m.%d.%Y")
                    except ValueError as err:
                        print("[WARNING] System {} File {} contains wrong Date {}".format(system_name,
                                                                                             exclude_yaml_file,
                                                                                             item["until"]))
                        until_date = ""

                outlist.append((note_id, until_date, comment))

            return outlist


class SimpleSystem(SAPSystem):
    def __init__(self, system_name="", version=""):
        super().__init__(system_name)
        self.version = version

