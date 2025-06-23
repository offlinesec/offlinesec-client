import os
import yaml

from offlinesec_client.sap_table import SAPTable

CORE_SAP_SYSTEM_KEY = "sap_systems"
ROOT_DIR_KEY = "root_dir"
DEF_SYSTEM_NAME = "#%s"

DEFAULT_STRUCTURE = {
    "root_dir": {"required": False, "desc": "Folder name with all files"},
    "sap_systems": {"required": True, "desc": "SAP system list", "sub_keys": {
        "name": {"required": False, "desc": "SAP System name"},}
                    }
    }

class YamlCfg:
    def __init__(self, file_name, yaml_structure=None):
        self.file_name = file_name
        self.errors = list()
        self.warnings = list()
        self.yaml_structure = DEFAULT_STRUCTURE if yaml_structure is None or isinstance(yaml_structure, list) else yaml_structure
        self.content = None
        self.check_file()
        if self.is_error():
           return
        self.read_file()
        if self.is_error():
            return

    def is_error(self):
        if len(self.errors):
            return True
        return False

    def read_tables_from_file(self, file_name_list, table_name, system_desc=None):
        out_list = list()

        if not isinstance(file_name_list, list):
            temp_file_name = file_name_list
            file_name_list = list()
            file_name_list.append(temp_file_name)

        for file_name in file_name_list:
            if not os.path.isfile(file_name):
                if system_desc is not None:
                    self.warnings.append("File %s not found (System: %s)" % (file_name, system_desc))
                else:
                    self.warnings.append("File %s not found" % (file_name,))
                continue

            new_tbl = SAPTable(table_name=table_name, file_name=file_name)
            if new_tbl:
                new_tbl.check_columns()
                if not len(new_tbl.err_list):
                    out_list.append(new_tbl)
                else:
                    self.warnings.extend(new_tbl.err_list)
        return out_list

    def check_file(self):
        if not self.file_name:
            self.errors.append("YAML filename not defined")
            return

        if not os.path.isfile(self.file_name):
            self.errors.append("The configuration file %s not found" % (self.file_name,))
            return

        if not self.file_name.lower().endswith(".yaml"):
            self.errors.append("* Wrong file format %s. Only YAML files supported" % (self.file_name,))
            return

    def read_file(self):
        self.content = None
        try:
            with open(self.file_name, 'r', encoding="utf-8") as f:
                self.content = yaml.safe_load(f)
        except Exception as err:
            self.errors.append("Can't read the file %s due to %s" % (self.file_name, str(err)))
        else:
            if not self.content:
                self.errors.append("The configuration file '%s' is empty" % (self.file_name, ))
                return
            self.check_yaml_content(yaml_content=self.content, yaml_definition=self.yaml_structure)

    def check_yaml_content(self, yaml_content, yaml_definition):
        for key in yaml_definition:
            if "required" in yaml_definition[key] and \
                yaml_definition[key]["required"]:
                if key not in yaml_content:
                    if "desc" in yaml_definition[key]:
                        self.errors.append("Required key '%s' (%s) not found" % (key, yaml_definition[key]["desc"]))
                    else:
                        self.errors.append("Required key '%s' not found" % (key,))
                    return

        for key_content in yaml_content:
            if key_content not in yaml_definition:
                self.warnings.append("Unknown key '%s' in the configuration file" % (key_content,))
                continue

        if CORE_SAP_SYSTEM_KEY not in yaml_content:
            return

        if yaml_content[CORE_SAP_SYSTEM_KEY] is None:
            self.errors.append("Required key 'sap_system' (SAP system list) is empty")
            return

        for key in yaml_definition[CORE_SAP_SYSTEM_KEY]["sub_keys"]:
            for i, system in enumerate(yaml_content[CORE_SAP_SYSTEM_KEY]):
                name = system["name"] if "name" in system else "#%s" % (str(i),)
                if "required" in yaml_definition[CORE_SAP_SYSTEM_KEY]["sub_keys"][key] and \
                    yaml_definition[CORE_SAP_SYSTEM_KEY]["sub_keys"][key]["required"]:

                    if key not in system:
                        if "desc" in yaml_definition[CORE_SAP_SYSTEM_KEY]["sub_keys"][key]:
                            self.warnings.append("Required key '%s' (%s) not found (System: %s)" % (key, yaml_definition[CORE_SAP_SYSTEM_KEY]["sub_keys"][key]["desc"], name))
                        else:
                            self.warnings.append("Required key '%s' not found (System: %s)" % (key, name))
                        continue

        for i, system in enumerate(yaml_content[CORE_SAP_SYSTEM_KEY]):
            name = system["name"] if "name" in system else "#%s" % (str(i),)
            for key in system:
                if key not in yaml_definition[CORE_SAP_SYSTEM_KEY]["sub_keys"]:
                    self.warnings.append("Unknown key %s (System: %s)" % (key, name))
                    continue

    def __iter__(self):

        if not self.content:
            return

        if not CORE_SAP_SYSTEM_KEY in self.content:
            return

        root_dir = self.content[ROOT_DIR_KEY] if ROOT_DIR_KEY in self.content else None

        for pos, system_attr in enumerate(self.content[CORE_SAP_SYSTEM_KEY]):
            if not "name" in system_attr:
                system_attr["name"] = DEF_SYSTEM_NAME % (pos,)
            if root_dir:
                for item_key in system_attr:
                    if item_key in self.yaml_structure[CORE_SAP_SYSTEM_KEY]["sub_keys"]:
                        if "value_type" in self.yaml_structure[CORE_SAP_SYSTEM_KEY]["sub_keys"][item_key]:
                            if self.yaml_structure[CORE_SAP_SYSTEM_KEY]["sub_keys"][item_key]["value_type"].lower() == "string":
                                continue

                    if isinstance(system_attr[item_key], list):
                        temp_list = list()
                        for single_value in system_attr[item_key]:
                            temp_list.append(os.path.join(root_dir, single_value))
                        system_attr[item_key] = temp_list
                    else:
                        system_attr[item_key] = os.path.join(root_dir, system_attr[item_key])

            yield system_attr

