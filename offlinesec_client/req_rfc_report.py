# -*- coding: utf-8 -*-
import argparse
import json
import offlinesec_client.func
from offlinesec_client.const import FILE, SYSTEM_NAME, ERR_MESSAGE,SCAN_ID, VERSION, WAIT, DO_NOT_WAIT
from offlinesec_client.masking import *
from offlinesec_client.yaml_cfg_rfc import YamlCfgRfc

UPLOAD_URL = "/sec-notes"
FILE_ALLOWED_EXTENSIONS = ["yaml"]
FILE_ALLOWED_EXT_JSON = ["json"]
MAX_FILE_SIZE = 10000


def check_file_arg(s):
    return offlinesec_client.func.check_file_arg(s, FILE_ALLOWED_EXTENSIONS, MAX_FILE_SIZE)


def check_system_name(s):
    return offlinesec_client.func.check_system_name(s)


def check_variant(s):
    return offlinesec_client.func.check_variant(s)


def check_json_arg(s):
    return offlinesec_client.func.check_file_arg(s, FILE_ALLOWED_EXT_JSON)


def init_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-f", "--%s" % (FILE,), action="store", type=check_file_arg,
                        help="The YAML config file", required=False)
    parser.add_argument("-v", "--variant", action="store", type=check_variant,
                        help="Check Variant (numeric)", required=False)
    parser.add_argument('--do-not-send', action='store_true', help="Don't upload file to server (review first)")
    parser.add_argument("-j", "--json_file", action="store", type=check_json_arg,
                        help="JSON file prepared earlier", required=False)
    parser.add_argument('-i', '--id', action='store', help="The scan Id (any unique identifier)")
    parser.add_argument('-w', '--wait', action='store_true', help="Wait 5 minutes and download the report")
    parser.add_argument('-nw', '--do-not-wait', action='store_true', help="Don't ask to download the report")

    parser.parse_args()
    return vars(parser.parse_args())


def data_masking(rfc_conn_list):
    rfcdest_masking = Masking(RFCDEST_MASK)
    user_masking = Masking(USER_MASK)
    host_masking = Masking(HOST_MASK)
    sapsid_masking = Masking(SAPSID_MASK)
    path_masking = Masking(PATH_MASK)

    for conn in rfc_conn_list:
        conn_type = conn["RFCTYPE"]
        if "RFCDEST" in conn.keys():
            conn["RFCDEST"] = rfcdest_masking.do_mask(conn["RFCDEST"])
        if "U" in conn.keys():
            if not conn["U"] in ("SAP*", "DDIC", "TMSADM", "SAPCPIC", "EARLYWATCH", "WF-BATCH"):
                conn["U"] = user_masking.do_mask(conn["U"])
        if "D" in conn.keys():
            # exclude standard users
            conn["D"] = user_masking.do_mask(conn["D"])
        if "H" in conn.keys():
            conn["H"] = host_masking.do_mask(conn["H"])
        if "G" in conn.keys():
            conn["G"] = host_masking.do_mask(conn["G"])
        if "SRCSID" in conn.keys():
            conn["SRCSID"] = sapsid_masking.do_mask(conn["SRCSID"])
        if "N" in conn.keys():
            conn["N"] = path_masking.do_mask(conn["N"])
        if "I" in conn.keys() and conn_type == "3":
            conn["I"] = sapsid_masking.do_mask(conn["I"])

    rfcdest_masking.save_masking()
    user_masking.save_masking()
    host_masking.save_masking()
    sapsid_masking.save_masking()
    path_masking.save_masking()


def save_json(data_to_save):
    json_filename = offlinesec_client.func.get_file_name("rfc.json")
    with open(json_filename, 'w') as f:
        json.dump(data_to_save, f)
    print("* The data saved to the '%s' file. Review it and send it with option -j to the server" % (json_filename,))


def read_json(file_name):
    if not os.path.isfile(file_name):
        print(" * [ERROR] File %s not exist" % (file_name,))
        return

    try:
        with open(file_name, 'r') as file:
            data = json.load(file)
            return data
    except Exception as err:
        print(" * [ERROR] " + str(err))


def process_it(args):
    rfc_conns = list()

    if FILE in args.keys() and args[FILE]:
        config_file = args[FILE]
        cfg = YamlCfgRfc(config_file)
        cfg.read_file()
        rfc_conns = cfg.load_tables()
        data_masking(rfc_conns)
        rfc_conns = list(filter(lambda conn: conn["RFCTYPE"] in ["3", "H", "G"], rfc_conns))

        if "do_not_send" in args.keys() and args["do_not_send"]:
            save_json(rfc_conns)
            return

        if len(cfg.err_list):
            for err in cfg.err_list:
                print(err)

            resp = input("There are some warning. Do you want to continue?" + " (y/N):").strip().lower()
            if resp is None or resp == "" or resp[0].lower() == "n":
                return

    elif "json_file" in args.keys() and args["json_file"]:
        data = read_json(args["json_file"])
        if data:
            rfc_conns = data

    if not len(rfc_conns):
        print("* [ERROR] No data to send to server")
        return

    additional_keys = dict()
    if SCAN_ID in args.keys() and args[SCAN_ID]:
        additional_keys[SCAN_ID] = args[SCAN_ID]

    additional_keys[VERSION] = offlinesec_client .__version__
    additional_keys["request_type"] = "rfc"

    if "variant" in args.keys() and args["variant"]:
        additional_keys["variant"] = args["variant"]

    wait = args[WAIT] if WAIT in args else ""
    do_not_wait = args[DO_NOT_WAIT] if DO_NOT_WAIT in args else ""

    rfc_conn_dict = dict()
    rfc_conn_dict["connections"] = rfc_conns

    offlinesec_client.func.send_to_server_gen(data=rfc_conns,
                                          url=UPLOAD_URL,
                                          extras=additional_keys,
                                          wait=wait,
                                          do_not_wait=do_not_wait)

def main():
    args = init_args()
    if args["file"] or args["json_file"]:
        if (args["file"] and not args["json_file"]) or (not args["file"] and args["json_file"]):
            process_it(args)
        else:
            print(" * [ERROR] You can't specify -f (yaml) and -j (previously prepared JSON file) options at the same request")
    else:
        print(" * [ERROR] You need to choose the config file with -f option or use -j option to send earlier prepared JSON file to the server ")


if __name__ == '__main__':
    main()
