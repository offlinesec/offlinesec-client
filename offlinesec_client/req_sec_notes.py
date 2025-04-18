import argparse
import yaml
import offlinesec_client.func
from offlinesec_client.const import FILE, VERSION, WAIT, DO_NOT_WAIT, SCAN_ID, SAP_SYSTEMS_KEY
from offlinesec_client.multi_systems import process_yaml_file
from offlinesec_client.masking import Masking, SAPSID_MASK

UPLOAD_URL = "/sec-notes"


def check_variant(s):
    return offlinesec_client.func.check_variant(s)


def check_file_arg(s):
    res = offlinesec_client.func.check_file_arg(s, ['yaml'], 200000)
    try:
        with open(s, 'r') as file:
            yaml_content = yaml.safe_load(file)
        if SAP_SYSTEMS_KEY not in yaml_content:
            raise argparse.ArgumentTypeError(" * [ERROR] Bad YAML file structure (%s). The 'sap_systems' key not found in YAML file" % (s,))
    except:
        raise argparse.ArgumentTypeError(
            " * [ERROR] Bad YAML file structure (%s). Please check the file content" % (s,))

    return res

def check_file_arg_sla(s):
    res = offlinesec_client.func.check_file_arg(s, ['yaml'], 200000)
    return res


def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", action="store", type=check_file_arg,
                        help="The config file name (SAP systems (ABAP, JAVA, BO, ...) and their software components in YAML format)", required=True)
    parser.add_argument("-v", "--variant", action="store", type=check_variant,
                        help="Check Variant (numeric)", required=False)
    parser.add_argument("-l", "--sla", action="store", type=check_file_arg_sla,
                        help="SLA file in YAML format")
    parser.add_argument('-nr', '--keep-not_relevant', action='store_true', help="Do not exclude notes marked as 'Not Relevant'")
    parser.add_argument("-d","--date", action='store', help="The report on specific date in past (DD-MM-YYYY)")
    parser.add_argument('-i', '--id', action='store', help="The scan Id (any unique identifier)")
    parser.add_argument('--do-not-send', action='store_true', help="Don't upload data to the server (review first)")
    parser.parse_args()
    return vars(parser.parse_args())


def do_masking(input_data):
    sapsid_masking = Masking(SAPSID_MASK)
    for sys in input_data:
        if hasattr(sys, "system_name"):
            sys.system_name = sapsid_masking.do_mask(sys.system_name)
    sapsid_masking.save_masking()


def process_it(args):
    systems = process_yaml_file(args)
    do_masking(systems)
    additional_keys = dict()

    additional_keys[VERSION] = offlinesec_client .__version__

    if args[SCAN_ID] and args[SCAN_ID] is not None:
        additional_keys[SCAN_ID] = args[SCAN_ID]

    if "variant" in args and args["variant"] is not None:
        additional_keys["variant"] = args["variant"]

    if "date" in args and args["date"] is not None:
        additional_keys["on_date"] = offlinesec_client.func.parse_date(args["date"])

    if "sla" in args and args["sla"] is not None:
        for system in systems:
            if not hasattr(system,"sla") or system.sla is None:
                system.sla = offlinesec_client.func.check_sla_file(args["sla"])

    if "keep_not_relevant" in args and args["keep_not_relevant"]:
        additional_keys["keep_not_relevant"] = True

    wait = True
    do_not_wait = False

    if "do_not_send" in args and args["do_not_send"]:
        offlinesec_client.func.save_to_json(data=systems,
                                            extras=additional_keys)
        return

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

