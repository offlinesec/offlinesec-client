import requests
import argparse
import os
import sys
import offlinesec_client.func
from offlinesec_client.const import ERR_MESSAGE, FILE, SYSTEM_NAME, KRNL_PL, KRNL_VER, CWBNTCUST
import json
import time

UPLOAD_URL = "/bonotes-upload"
EXCLUDE_KEYS = ["wait", "exclude", "exclusion file"]


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


def check_exclude_file(s):
    return offlinesec_client.func.check_file_arg(s, ['txt'], 200000)


def prepare_exclusions(excl_list, excl_file):
    outdict = list()

    if excl_file:
        with open(excl_file,'r') as f:
            for line in f:
                line = line.strip("\r\n")
                line = line.split(",")
                if len(line) < 3:
                    line.append(None)
                if len(line) < 3:
                    line.append(None)
                outdict.append(line[:3])

    if excl_list:
        line = excl_list.split(",")
        for item in line:
            outdict.append([item.strip(), None, None])

    return outdict


def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-ver", "--version", action="store", type=check_bo_version,
                        help="SAP Business Object version (for inst. 14.3.2.4121)", required=True)
    parser.add_argument("-s", "--%s" % (SYSTEM_NAME,), action="store", type=check_system_name,
                        help="SAP System Name (max 20 characters)", required=False)
    parser.add_argument("-var", "--variant", action="store", type=check_variant,
                        help="Check Variant (numeric)", required=False)
    parser.add_argument("-e", "--exclude", action="store",
                        help='Exclude SAP BO security notes ("1111111, 2222222, 3333333")', required=False)
    parser.add_argument("-ef", "--exclusion file", action="store", type=check_exclude_file,
                        help='Exclude SAP BO security notes (from text file)', required=False)
    parser.add_argument('--wait', action='store_true', help="Wait 5 minutes and download the report")

    parser.parse_args()
    return vars(parser.parse_args())


def send_file(args):
    url = offlinesec_client.func.get_connection_str(UPLOAD_URL)

    data = offlinesec_client.func.get_base_json()
    data["bo"] = True

    for key, value in args.items():
        if value and key not in EXCLUDE_KEYS:
            data[key] = value

    data["exclusions"] = prepare_exclusions(args["exclude"], args["exclusion file"])

    files = {'json': ('description', json.dumps(data), 'application/json')}

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


def process_it(args):
    if not offlinesec_client.func.check_server():
        return

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
