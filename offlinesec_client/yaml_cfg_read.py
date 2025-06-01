import os
import yaml

ADD_ROOT_DIR_KEYS = ["agr_users", "usr02", "agr_1251"]
SAP_SYSTEMS_KEY = "sap_systems"
ROOT_DIR_KEY = "root_dir"
DEF_SYSTEM_NAME = "System %s"

class YamlCfgFile:
    def __init__(self, file_name):
        self.err_list = list()
        self.file_name = file_name

        self.check_file()
        self.content = None
        if self.check_class_item():
            self.read_file()
            self.get_root_dir()

    def check_file(self):
        if not self.file_name:
            self.err_list.append(" [ERROR] YAML filename not defined")
            return

        if not os.path.isfile(self.file_name):
            self.err_list.append("* [ERROR] The configuration file %s not found" % (self.file_name,))
            return

    def check_class_item(self):
        if not len(self.err_list):
            return True
        return False

    def read_file(self):
        self.content = None
        try:
            with open(self.file_name, 'r', encoding="utf-8") as f:
                self.content = yaml.safe_load(f)
        except Exception as err:
            self.err_list.append("* [ERROR] Can't read the file %s due to %s" % (self.file_name, str(err)))
        else:
            if "sap_systems" not in self.content:
                self.err_list.append("* [ERROR] The required key 'sap_systems' not found in file %s" % (self.file_name, ))

    def get_root_dir(self):
        self.root_dir = None
        if not self.content:
            return

        if ROOT_DIR_KEY in self.content:
            self.root_dir = self.content[ROOT_DIR_KEY]

    def __iter__(self):
        if not self.content:
            return

        if not SAP_SYSTEMS_KEY in self.content:
            return

        for pos, system_attr in enumerate(self.content[SAP_SYSTEMS_KEY]):
            if not "name" in system_attr:
                system_attr["name"] = DEF_SYSTEM_NAME % (pos,)
            if self.root_dir:
                for item_key in system_attr:
                    if item_key.lower() in ADD_ROOT_DIR_KEYS:
                        if isinstance(system_attr[item_key], list):
                            temp_list = list()
                            for single_value in system_attr[item_key]:
                                temp_list.append(os.path.join(self.root_dir, single_value))
                            system_attr[item_key] = temp_list
                        else:
                            system_attr[item_key] = os.path.join(self.root_dir, system_attr[item_key])

            yield system_attr
