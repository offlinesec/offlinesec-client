import requests
import argparse
import os
import sys
import offlinesec_client.func
from offlinesec_client.const import ERR_MESSAGE, FILE, SYSTEM_NAME, KRNL_PL, KRNL_VER, CWBNTCUST
import abap_system
import json
import time

UPLOAD_URL = "/sec-notes"


def check_version(s):
    return offlinesec_client.func.check_num_param("".join(s.split('.')), "Kernel Version")


def check_patch_level(s):
    return offlinesec_client.func.check_num_param(s, "Kernel Patch Level")


def check_system_name(s):
    return offlinesec_client.func.check_system_name(s)


def check_file_arg(s):
    return offlinesec_client.func.check_file_arg(s, ['txt'], 200000)


def check_cwbntcust(s):
    return offlinesec_client.func.check_file_arg(s, ["xlsx", "txt"], 2000000)


def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--%s" % (FILE,), action="store", type=check_file_arg,
                        help="File Name (Software Components)", required=False)
    parser.add_argument("-s", "--%s" % (SYSTEM_NAME,), action="store", type=check_system_name,
                        help="SAP System Name (max 20 characters)", required=False)
    parser.add_argument("-k", "--%s" % (KRNL_VER,), action="store", type=check_version,
                        help="Kernel Version (for instance 7.53)", required=False)
    parser.add_argument("-p", "--%s" % (KRNL_PL,), action="store", type=check_patch_level,
                        help="Kernel Patch Level (for instance 1200)", required=False)
    parser.add_argument("-c", "--%s" % (CWBNTCUST,), action="store", type=check_cwbntcust,
                        help="CWBNTCUST table (txt or xlsx)", required=False)
    parser.add_argument("-e", "--exclude", action="store",
                        help='Exclude SAP security notes ("1111111, 2222222, 3333333")', required=False)
    parser.add_argument('-w', '--wait', action='store_true', help="Wait 5 minutes and download the report")
    parser.add_argument('--guiscript', action='store_true', help="Run GUI script to prepare the input data")
    parser.parse_args()
    return vars(parser.parse_args())


def convert_to_dict(**args):
    system_list = list()
    new_abap_system = abap_system.ABAPSystem(args)
    if new_abap_system is not None:
        system_list.append(system_list)


def send_file(file, system_name="", kernel_version="", kernel_patch="", cwbntcust="", exclude=""):
    additional_keys = dict()
    system_list = list()

    if system_name is None or system_name == "":
        system_name = "ABAP System"

    new_abap_system = abap_system.ABAPSystem(krnl_version=kernel_version,
                                             krnl_patch=kernel_patch,
                                             cwbntcust=cwbntcust,
                                             exclude=exclude,
                                             name=system_name,
                                             softs=file)
    if new_abap_system is not None:
        system_list.append(new_abap_system)

    offlinesec_client.func.send_to_server(system_list, UPLOAD_URL, additional_keys)


def process_it(file, system_name="", kernel_version="", kernel_patch="", cwbntcust="", guiscript=False, wait=False, exclude=""):
    if not offlinesec_client.func.check_server():
        return

    if guiscript:
        import platform
        if platform.system() == 'Windows':
            from offlinesec_client.sap_gui import SAPConnection
            conn = SAPConnection.sap_notes_report(system_name=system_name, wait=wait)
        else:
            print("SAP GUI Scripting not supported on this platform. Run SAP Gui Scripting only on Windows platform")
        return

    send_file(file, system_name, kernel_version, kernel_patch, cwbntcust, exclude)

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
    if (FILE in args and args[FILE]) or ("guiscript" in args and args["guiscript"]):
        process_it(args[FILE], args[SYSTEM_NAME], args[KRNL_VER], args[KRNL_PL], args[CWBNTCUST], args["guiscript"], args["wait"], args["exclude"])
    else:
        print("You need to specify input file(s) (-f option) or --guiscript option (to run gui script)")


if __name__ == '__main__':
    main()
