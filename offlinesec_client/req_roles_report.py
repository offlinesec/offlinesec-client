import argparse
import os
import json
import requests
from offlinesec_client.const import FILE, SYSTEM_NAME, ERR_MESSAGE, VERSION
import offlinesec_client.func
from offlinesec_client.agr_cfg_read import RolesCfgFile
FILE_ALLOWED_EXTENSIONS = ["yaml"]
ZIP_ALLOWED_EXTENSIONS = ["zip"]
MAX_FILE_SIZE = 20000

UPLOAD_URL = "/roles-upload"


def check_file_arg(s):
    return offlinesec_client.func.check_file_arg(s, FILE_ALLOWED_EXTENSIONS, MAX_FILE_SIZE)

def check_variant(s):
    return offlinesec_client.func.check_variant(s)

def init_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-f", "--file", action="store", type=check_file_arg,
                        help="The config file name (SAP systems (ABAP, JAVA, BO, ...) and role tables (AGR_1251, AGR_USERS, USR02) in YAML format)", required=True)
    parser.add_argument("-v", "--variant", action="store", type=check_variant,
                        help="Check Variant (numeric)", required=False)
    parser.add_argument('-na', '--ignore_na_roles', action='store_true', help="Do not exclude notes marked as 'Not Relevant'")
    parser.add_argument('-ff', '--ignore_ff', action='store_true', help="Do not exclude notes marked as 'Not Relevant'")
    parser.add_argument('--do-not-send', action='store_true', help="Don't upload data to the server (review first)")
    parser.parse_args()

    parser.parse_args()
    return vars(parser.parse_args())

def process_it(args):
    file_name = args[FILE] if FILE in args else None
    ignore_ff = args["ignore_ff"] if "ignore_ff" in args else False
    ignore_na = args["ignore_na_roles"] if "ignore_na_roles" in args else False
    if not file_name:
        return
    cfg = RolesCfgFile(file_name, ignore_na_roles=ignore_na, ignore_ff_roles=ignore_ff)
    data = cfg.parse()

    if len(cfg.err_list):
        for err in cfg.err_list:
            print(err)
        if cfg.err_flag:
            return
        resp = input("There are some warning. Do you want to continue?" + " (y/N):").strip().lower()
        if resp is None or resp == "" or resp[0].lower() == "n":
            return

    new_data = RolesCfgFile.masking(data)
    zip_file_name = RolesCfgFile.save_and_zip(new_data)

    if not zip_file_name or not os.path.isfile(zip_file_name):
        return

    if "do_not_send" in args.keys() and args["do_not_send"]:
        return

    additional_keys = dict()
    additional_keys[VERSION] = offlinesec_client.__version__
    additional_keys["request_type"] = "roles"

    if cfg.ff_masks and len(cfg.ff_masks):
        additional_keys["ff_masks"] = cfg.ff_masks

    COPY_KEYS_FROM_CMD = ["variant", "ignore_na_roles", "ignore_ff"]

    for key1 in COPY_KEYS_FROM_CMD:
        if key1 in args and args[key1] is not None:
            additional_keys[key1] = args[key1]

    wait = True
    do_not_wait = False
    offlinesec_client.func.send_file_to_server(file_name=zip_file_name,
                                               extras=additional_keys,
                                               url=UPLOAD_URL,
                                               wait=wait,
                                               do_not_wait=do_not_wait)

def main():
    args = init_args()
    if FILE in args and args[FILE]:
        process_it(args)
    else:
        print("Please choose the configuration YAML file (-f option)")

if __name__ == '__main__':
    main()
