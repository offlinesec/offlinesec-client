import requests
import argparse
import os
import offlinesec_client.func
from offlinesec_client.const import ERR_MESSAGE, FILE, SYSTEM_NAME, KRNL_PL, KRNL_VER, CWBNTCUST
import json

UPLOAD_URL = "/file-upload"


def check_version(s):
    return offlinesec_client.func.check_num_param("".join(s.split('.')), "Kernel Version")


def check_patch_level(s):
    return offlinesec_client.func.check_num_param(s, "Kernel Patch Level")


def check_system_name(s):
    return offlinesec_client.func.check_system_name(s)


def check_file_arg(s):
    return offlinesec_client.func.check_file_arg(s, ['txt'], 200000)


def check_cwbntcust(s):
    return offlinesec_client.func.check_file_arg(s, ["xlsx"], 2000000)


def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--%s" % (FILE,), action="store", type=check_file_arg,
                        help="File Name (Software Components)", required=True)
    parser.add_argument("-s", "--%s" % (SYSTEM_NAME,), action="store", type=check_system_name,
                        help="SAP System Name (max 20 characters)", required=False)
    parser.add_argument("-k", "--%s" % (KRNL_VER,), action="store", type=check_version,
                        help="Kernel Version (for instance 7.53)", required=False)
    parser.add_argument("-p", "--%s" % (KRNL_PL,), action="store", type=check_patch_level,
                        help="Kernel Patch Level (for instance 1200)", required=False)
    parser.add_argument("-c", "--%s" % (CWBNTCUST,), action="store", type=check_cwbntcust,
                        help="SAP System Name (max 20 characters)", required=False)
    parser.parse_args()
    return vars(parser.parse_args())


def send_file(file, system_name="", kernel_version="", kernel_patch="", cwbntcust=""):
    url = offlinesec_client.func.get_connection_str(UPLOAD_URL)
    data = offlinesec_client.func.get_base_json(system_name=system_name,
                                                kernel_version=kernel_version,
                                                kernel_patch=kernel_patch,
                                                cwbntcust=cwbntcust)

    files = {
        'json': ('description', json.dumps(data), 'application/json'),
        'file': (os.path.basename(file), open(file, 'rb'), 'application/octet-stream')
    }
    print("Uploading file %s" % (os.path.basename(file)))
    r = requests.post(url, files=files)

    if r.content:
        try:
            response = json.loads(r.content)
            if ERR_MESSAGE in response:
                print(" * " + response[ERR_MESSAGE])
                return
        except:
            pass

    print("No response from server. Please try later")


def process_it(file, system_name="", kernel_version="", kernel_patch="", cwbntcust=""):
    if not offlinesec_client.func.check_server():
        return

    send_file(file, system_name, kernel_version, kernel_patch, cwbntcust)


def main():
    args = init_args()
    if FILE in args:
        process_it(args[FILE], args[SYSTEM_NAME], args[KRNL_VER], args[KRNL_PL], args[CWBNTCUST])


if __name__ == '__main__':
    main()
