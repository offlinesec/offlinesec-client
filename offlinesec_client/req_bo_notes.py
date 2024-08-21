import requests
import argparse
import os
import sys
import offlinesec_client.func
from offlinesec_client.const import ERR_MESSAGE, FILE, SYSTEM_NAME, KRNL_PL, KRNL_VER, CWBNTCUST, EXCLUDE
from offlinesec_client.bo_system import BOSystem
import json
import time

UPLOAD_URL = "/sec-notes"


def check_system_name(s):
    return offlinesec_client.func.check_system_name(s)


def check_variant(s):
    return offlinesec_client.func.check_variant(s)


def check_bo_version(v):
    splitted_ver = v.strip('"').split(".")
    if not len(splitted_ver) == 4:
        raise argparse.ArgumentTypeError("Wrong version format")

    if not int(splitted_ver[0]) == 14:
        raise argparse.ArgumentTypeError("Wrong version format")
    try:
        for item in splitted_ver:
            s = int(item)
    except:
        raise argparse.ArgumentTypeError("Wrong version format")
    return v


def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-ver", "--version", action="store", type=check_bo_version,
                        help="SAP Business Object version (for inst. 14.3.2.4121)", required=True)
    parser.add_argument("-s", "--%s" % (SYSTEM_NAME,), action="store", type=check_system_name,
                        help="SAP System Name (max 20 characters)", required=False)
    parser.add_argument("-var", "--variant", action="store", type=check_variant,
                        help="Check Variant (numeric)", required=False)
    parser.add_argument("-e", "--exclude", action="store",
                        help='Exclude SAP BO security notes (YAML file)', required=False)
    parser.add_argument('--wait', action='store_true', help="Wait 5 minutes and download the report")

    parser.parse_args()
    return vars(parser.parse_args())


def send_file(args):
    additional_keys = dict()
    system_list = list()
    system_name = None

    if SYSTEM_NAME in args:
        system_name = args[SYSTEM_NAME]

    if system_name is None or system_name == "":
        system_name = "BO System"

    exclude = args[EXCLUDE] if EXCLUDE in args else ""
    version = args["version"] if "version" in args else ""

    additional_keys["version"] = offlinesec_client.__version__
    new_bo_system = BOSystem(exclude=exclude,
                                 name=system_name,
                                 version=version)
    if new_bo_system is not None:
        system_list.append(new_bo_system)

    offlinesec_client.func.send_to_server(system_list, UPLOAD_URL, additional_keys)


def process_it(args):
    if "version" in args and args["version"]:
        send_file(args)

        if "wait" in args and args["wait"]:
            for remaining in range(310, 0, -1):
                sys.stdout.write("\r")
                sys.stdout.write("{:2d} seconds remaining.".format(remaining))
                sys.stdout.flush()
                time.sleep(1)
            os.system("offlinesec_get_reports")


def main():
    args = init_args()
    process_it(args)


if __name__ == '__main__':
    main()
