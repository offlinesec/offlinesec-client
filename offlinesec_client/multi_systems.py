import yaml
from offlinesec_client.const import FILE
from offlinesec_client.abap_system import ABAPSystem
from offlinesec_client.java_system import JAVASystem
from offlinesec_client.bo_system import BOSystem


def process_yaml_file(args):
    file_name = args[FILE]
    error_list = list()
    system_list = list()

    try:
        with open(file_name, 'r', encoding="utf-8") as f:
            file_content = yaml.safe_load(f)
    except:
        print(" * [ERROR] Bad YAML file structure in %s. Check the file content" % (file_name,))
        return

    root_dir = file_content["root_dir"] if "root_dir" in file_content else ""
    if not "sap_systems" in file_content:
        print(" * [ERROR] The required 'sap_systems' key not defined in the YAML file %s" % (file_name,))
        return

    for num, system in enumerate(file_content["sap_systems"]):
        if "name" not in system.keys():
            system["name"] = "System {}".format(str(num+1))
        system_type = system["type"] if "type" in system.keys() else ""
        if root_dir != "":
            system["root_dir"] = root_dir
        if system_type == "":
            err = " * [ERROR] The system '{}' doesn't contain the required 'type' key. Please set the 'type' attribute (ABAP, JAVA or BO)".format(system["name"])
            print(err)
            continue

        try:
            if system_type.upper().strip() == "ABAP":
                new_item = ABAPSystem(**system)
            elif system_type.upper().strip() == "JAVA":
                new_item = JAVASystem(**system)
            elif system_type.upper().strip() == "BO":
                new_item = BOSystem(**system)
            else:
                err = " * [ERROR] The unknown system type '{}' is set for system '{}'. Supported only: ABAP, JAVA, BO".format(system_type,system["name"])
                print(err)
                continue
        except (FileNotFoundError, ValueError) as error:
            err = " * [ERROR] System '{}' {}".format(system["name"], str(error))
            print(err)
            continue
        else:
            if new_item:
                system_list.append(new_item)

    return system_list
