import argparse
import os
import re
import yaml
import offlinesec_client.func
from offlinesec_client.sap_table import SAPTable
from offlinesec_client.const import FILE, WAIT, DO_NOT_WAIT
from offlinesec_client.masking import Masking, SAPSID_MASK
from offlinesec_client.exclude_params import EXCLUDE_PARAMS

FILE_ALLOWED_EXTENSIONS = ["yaml"]
JSON_ALLOWED_EXTENSIONS = ["json"]
MAX_FILE_SIZE = 200000

UPLOAD_URL = "/sec-notes"

def check_system_name(s):
    if len(s) <= 20:
        return s
    raise argparse.ArgumentTypeError("The System Name must have length less than 20")

def check_file_arg(s):
    if not os.path.isfile(s):
        raise argparse.ArgumentTypeError("File not found (-f)")

    ext = s.split('.')[-1].lower()
    if ext not in FILE_ALLOWED_EXTENSIONS:
        raise argparse.ArgumentTypeError("File type not supported. Only allowed extensions: %s" %
                                         (", ".join(FILE_ALLOWED_EXTENSIONS)))

    if os.path.getsize(s) > MAX_FILE_SIZE:
        raise argparse.ArgumentTypeError("File too big (-f)")

    return s

def check_json_arg(s):
    if not os.path.isfile(s):
        raise argparse.ArgumentTypeError("File not found (-j)")

    ext = s.split('.')[-1].lower()
    if ext not in JSON_ALLOWED_EXTENSIONS:
        raise argparse.ArgumentTypeError("File type not supported. Only allowed extensions: %s" %
                                         (", ".join(JSON_ALLOWED_EXTENSIONS)))

    if os.path.getsize(s) > MAX_FILE_SIZE:
        raise argparse.ArgumentTypeError("File too big (-z)")

    return s

def check_variant(s):
    try:
        num = int(s)
    except:
        raise argparse.ArgumentTypeError("Variant must be numeric")
    return num

def init_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-f", "--%s" % (FILE,), action="store", type=check_file_arg,
                        help="The config file - Systems with profile parameters (YAML format)", required=False)

    parser.add_argument("-v", "--variant", action="store", type=check_variant,
                        help="The Custom Baseline ID (if registered)", required=False)

    parser.add_argument("-e", "--exclude", action="store",
                        help='Exclude Parameters (YAML file) - The single file for all systems', required=False)

    parser.add_argument('--do-not-send', action='store_true', help="Don't upload file to server (review first)")

    parser.add_argument("-j", "--json_file", action="store", type=check_json_arg,
                        help="JSON file prepared earlier", required=False)

    parser.add_argument('-w', '--wait', action='store_true', help="Wait 5 minutes and download the report")
    parser.add_argument('-nw', '--do-not-wait', action='store_true', help="Don't ask to download the report")

    parser.parse_args()
    return vars(parser.parse_args())

def read_profile_files(file_list, root_dir, exclude, system_name):
    tables = list()
    for file in file_list:
        full_path = os.path.join(root_dir,file) if root_dir else file
        if not os.path.isfile(full_path):
            print(" * [Warning] The file %s not found" % (full_path,))
            continue
        tbl = SAPTable("RSPARAM", full_path)
        if tbl:
            tables.append(tbl)

    if len(tables):
        return {"params": process_tables(tables),
                 "system_name": system_name,
                 "exclude": parse_exclude(exclude, system_name),
                 "rsparam_files": str(len(tables))}

def parse_exclude(exclude, system_name):
    if not exclude:
        return list()
    out_list = list()
    for line in exclude:
        if not "system_name" in line or not "param_name" in line:
            continue
        system_name_line = line["system_name"]
        if system_name_line == system_name or system_name_line == "*":
            param_name = line["param_name"]
            until = line["until"] if "until" in line else ""
            comment = line["comment"] if "comment" in line else ""
            out_list.append([param_name, until, comment])
    return out_list


def check_param(param_name):
    for hide_param in EXCLUDE_PARAMS:
        re_str = "(?i)^" + hide_param.lower() + "$"
        res = re.match(re_str, param_name)
        if res:
            return False
    return True


def process_tables(tables):
    out_table = dict()

    for table in tables:
        for param in table:
            param_name = param["Parameter Name"]

            if not check_param(param_name):
                continue

            new_value = get_value(param["User-Defined Value"],
                              param["System Default Value"],
                              param["System Default Value(Unsubstituted Form)"])

            # Path protection:
            if new_value:
                new_value = re.sub(r"/usr/sap/[\S]{3}/", "/usr/sap/XXX/", new_value)

            if param_name not in out_table:
                out_table[param_name] = {
                    "val": None,
                    "desc": None
                }

            if out_table[param_name]["val"] is None:
                out_table[param_name]["val"] = new_value
            elif isinstance(out_table[param_name]["val"], list):
                if new_value not in out_table[param_name]["val"]:
                    out_table[param_name]["val"].append(new_value)
            elif new_value != out_table[param_name]["val"]:
                    out_table[param_name]["val"] = [out_table[param_name]["val"], new_value]
            if out_table[param_name]["desc"] is None:
                out_table[param_name]["desc"] = param["Comment"]
    return out_table

def get_value(inst_val, def_val, krnl_val):
    if inst_val is not None and inst_val != "":
        return inst_val
    if def_val is not None and def_val != "":
        return def_val
    return krnl_val

def do_masking(input_data):
    sapsid_masking = Masking(SAPSID_MASK)
    for sys in input_data:
        if "system_name" in sys.keys():
            sys["system_name"] = sapsid_masking.do_mask(sys["system_name"])
    sapsid_masking.save_masking()


def parse_exclude_file(exclude_yaml_file):
    file_content = list()
    if exclude_yaml_file is None or exclude_yaml_file == "":
        return list()

    if not os.path.exists(exclude_yaml_file):
        raise FileNotFoundError("File %s not found" % (exclude_yaml_file,))

    if not exclude_yaml_file.upper().endswith(".YAML"):
        raise ValueError("File {} has wrong extension. Only YAML file supported".format(exclude_yaml_file))

    try:
        with open(exclude_yaml_file, 'r', encoding="utf-8") as f:
            file_content = yaml.safe_load(f)
    except:
        raise ValueError("File {} has wrong structure. Only YAML files supported".format(exclude_yaml_file))
    else:
        return file_content
    return list()

def process_yaml_file(args):
    file_name = args[FILE]
    error_list = list()
    system_list = list()

    with open(file_name, 'r', encoding="utf-8") as f:
        try:
            file_content = yaml.safe_load(f)
        except:
            file_content = None

    if not file_content:
        print(" * [ERROR] Bad YAML file format %s" % (file_name,))
        return

    root_dir = file_content["root_dir"] if "root_dir" in file_content else ""
    if not "sap_systems" in file_content:
        return
    exclude_file = args["exclude"] if "exclude" in args and args["exclude"] else None
    exclude_content = parse_exclude_file(exclude_file) if exclude_file and os.path.isfile(exclude_file) else list()

    for num, system in enumerate(file_content["sap_systems"]):
        if "name" not in system.keys():
            system["name"] = "Unnamed System {}".format(str(num+1))
        param_files = list()
        for system_key in system:
            if system_key.startswith("params"):
                param_files.append(system[system_key])
        if not len(param_files):
            print(" * [WARNING] Parameters files not found for system %s" % (system["name"],))
            continue

        new_system = read_profile_files(param_files, root_dir, exclude_content, system["name"])
        if new_system:
            system_list.append(new_system)
    return system_list


def process_it(args):
    if FILE in args and len(args[FILE]):
        data = process_yaml_file(args)
        do_masking(data)

        if "do_not_send" in args.keys() and args["do_not_send"]:
            offlinesec_client.func.save_json(data, "params.json")
            return

    elif "json_file" in args.keys() and args["json_file"]:
        data = offlinesec_client.func.read_json(args["json_file"])
    else:
        data = None

    if data is None or not len(data):
        print("* [ERROR] No data to send to the server")
        return

    additional_keys = offlinesec_client.func.populate_additional_keys(args)
    additional_keys["request_type"] = "params"

    wait = args[WAIT] if WAIT in args else ""
    do_not_wait = args[DO_NOT_WAIT] if DO_NOT_WAIT in args else ""


    offlinesec_client.func.send_to_server_gen(data=data, url=UPLOAD_URL,
                                              extras=additional_keys,
                                              wait=wait,
                                              do_not_wait=do_not_wait)

def main():
    args = init_args()
    if args["file"] or args["json_file"]:
        if (args["file"] and not args["json_file"]) or (not args["file"] and args["json_file"]):
            process_it(args)
        else:
            print("You can't specify -f (xlsx) and -j (previously prepared json file) options at the same request")
    else:
        print("You need to specify file using -f (xlsx) or -j (previously prepared json file) options")


if __name__ == '__main__':
    main()

