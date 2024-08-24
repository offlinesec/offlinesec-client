import argparse
import yaml
import offlinesec_client.func
from offlinesec_client.const import FILE, VERSION, WAIT, DO_NOT_WAIT, SCAN_ID, SAP_SYSTEMS_KEY
from offlinesec_client.multi_systems import process_yaml_file

UPLOAD_URL = "/sec-notes"


def check_file_arg(s):
    res = offlinesec_client.func.check_file_arg(s, ['yaml'], 200000)
    with open(s, 'r') as file:
        yaml_content = yaml.safe_load(file)
        if SAP_SYSTEMS_KEY not in yaml_content:
            raise argparse.ArgumentTypeError("Wrong the YAML file (%s) structure. The 'sap_systems' key not found" % (s,))
    return res


def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", action="store", type=check_file_arg,
                        help="File Name (SAP systems (ABAP, JAVA, BO, ...) and their software components in YAML format)", required=True)
    parser.add_argument('-w', '--wait', action='store_true', help="Wait 5 minutes and download the report")
    parser.add_argument('-nw', '--do-not-wait', action='store_true', help="Don't ask to download the report")
    parser.add_argument('-i', '--id', action='store', help="The scan Id (any unique identifier)")
    parser.parse_args()
    return vars(parser.parse_args())


def process_it(args):
    systems = process_yaml_file(args)
    additional_keys = dict()

    if args[SCAN_ID]:
        additional_keys[SCAN_ID] = args[SCAN_ID]

    additional_keys[VERSION] = offlinesec_client .__version__

    wait = args[WAIT] if WAIT in args else ""
    do_not_wait = args[DO_NOT_WAIT] if DO_NOT_WAIT in args else ""

    offlinesec_client.func.send_to_server(data=systems,
                                          url=UPLOAD_URL,
                                          extras=additional_keys,
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

