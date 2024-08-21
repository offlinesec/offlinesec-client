import requests
import argparse
import os
import sys
import offlinesec_client.func
from offlinesec_client.const import ERR_MESSAGE, FILE, SYSTEM_NAME, KRNL_PL, KRNL_VER, CWBNTCUST, WAIT, EXCLUDE
from offlinesec_client.java_system import JAVASystem
import json
import time

UPLOAD_URL = "/sec-notes"


def check_system_name(s):
    return offlinesec_client.func.check_system_name(s)


def check_variant(s):
    return offlinesec_client.func.check_variant(s)


def check_file_arg(s):
    return offlinesec_client.func.check_file_arg(s, ['csv'], 200000)


def check_exclude_file(s):
    return offlinesec_client.func.check_file_arg(s, ['txt'], 200000)


def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", action="store", type=check_file_arg,
                        help="SAP JAVA software components file (CSV)", required=True)
    parser.add_argument("-s", "--%s" % (SYSTEM_NAME,), action="store", type=check_system_name,
                        help="SAP System Name (max 20 characters)", required=False)
    parser.add_argument("-var", "--variant", action="store", type=check_variant,
                        help="Check Variant (numeric)", required=False)
    parser.add_argument("-e", "--exclude", action="store",
                        help='Exclude SAP JAVA security notes (YAML file)', required=False)
    parser.add_argument('--wait', action='store_true', help="Wait 5 minutes and download the report")

    parser.parse_args()
    return vars(parser.parse_args())


def send_file(file_name, system_name, exclude):
    additional_keys = dict()
    system_list = list()

    if system_name is None or system_name == "":
        system_name = "JAVA System"
    additional_keys["version"] = offlinesec_client.__version__
    new_java_system = JAVASystem(exclude=exclude,
                                 name=system_name,
                                 softs=file_name)
    if new_java_system is not None:
        system_list.append(new_java_system)

    offlinesec_client.func.send_to_server(system_list, UPLOAD_URL, additional_keys)


def process_it(file_name, system_name="", wait=False, exclude=""):
    if not offlinesec_client.func.check_server():
        return

    if file_name:
        send_file(file_name, system_name, exclude)

        if wait:
            for remaining in range(310, 0, -1):
                sys.stdout.write("\r")
                sys.stdout.write("{:2d} seconds remaining.".format(remaining))
                sys.stdout.flush()
                time.sleep(1)
            print("")
            os.system("offlinesec_get_reports")


def main():
    args = init_args()
    if (FILE in args and args[FILE]):
        process_it(file_name=args[FILE],
                   system_name=args[SYSTEM_NAME],
                   wait=args[WAIT],
                   exclude=args[EXCLUDE])
    else:
        print("You need to specify input file(s) (-f option)")


if __name__ == '__main__':
    main()
