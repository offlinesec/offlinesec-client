import argparse
import yaml
import sys
import time
import os
import offlinesec_client.func
from offlinesec_client.const import FILE
from offlinesec_client.multi_systems import process_yaml_file


# SUPPORTED_SYSTEMS = ["ABAP", "JAVA", "BO", "HANA"]
UPLOAD_URL = "/sec-notes"


def check_file_arg(s):
    res = offlinesec_client.func.check_file_arg(s, ['yaml'], 200000)
    with open(s, 'r') as file:
        yaml_content = yaml.safe_load(file)
        if "sap_systems" not in yaml_content:
            raise argparse.ArgumentTypeError("Wrong the YAML file (%s) structure. The 'sap_systems' key not found" % (s,))
    return res


def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", action="store", type=check_file_arg,
                        help="File Name (SAP systems (ABAP, JAVA, BO, ...) and their software components in YAML format)", required=True)
    parser.add_argument('-p', '--patch_day', action='store_true', help="Last Patch Day Variant")
    parser.add_argument('-i', '--id', action='store', help="The Scan ID (any unique identifier)")
    parser.parse_args()
    return vars(parser.parse_args())


def print_errors(errors):
    for error in errors:
        print(error)


def process_it(args):
    systems = process_yaml_file(args)
    additional_keys = dict()
    if args["patch_day"]:
        additional_keys["patch_day"] = True
    additional_keys["api_call"] = True
    if args["id"]:
        additional_keys["id"] = args["id"]
    additional_keys["version"] = offlinesec_client.__version__
    offlinesec_client.func.send_to_server(systems, UPLOAD_URL, additional_keys)


def main():
    args = init_args()
    if FILE in args and args[FILE]:
        process_it(args)
    else:
        print("Please choose the configuration YAML file (-f option)")


if __name__ == '__main__':
    main()

