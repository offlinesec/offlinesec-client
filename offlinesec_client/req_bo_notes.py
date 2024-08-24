import argparse
import offlinesec_client.func
from offlinesec_client.const import SYSTEM_NAME, EXCLUDE, WAIT, DO_NOT_WAIT, VERSION, ERROR_MSG_PREFIX
from offlinesec_client.bo_system import BOSystem

UPLOAD_URL = "/sec-notes"
DEFAULT_SYSTEM_NAME = "BO System"


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
    parser.add_argument('-w', '--wait', action='store_true', help="Wait 5 minutes and download the report")
    parser.add_argument('-nw', '--do-not-wait', action='store_true', help="Don't ask to download the report")

    parser.parse_args()
    return vars(parser.parse_args())


def send_file(args):
    additional_keys = dict()
    system_list = list()
    system_name = None

    if SYSTEM_NAME in args:
        system_name = args[SYSTEM_NAME]

    if system_name is None or system_name == "":
        system_name = DEFAULT_SYSTEM_NAME

    exclude = args[EXCLUDE] if EXCLUDE in args else ""
    version = args[VERSION] if VERSION in args else ""
    wait = args[WAIT] if WAIT in args else ""
    do_not_wait = args[DO_NOT_WAIT] if DO_NOT_WAIT in args else ""

    additional_keys[VERSION] = offlinesec_client.__version__
    try:
        new_bo_system = BOSystem(exclude=exclude,
                                 name=system_name,
                                 version=version)
    except Exception as err:
        print(ERROR_MSG_PREFIX + str(err))
        new_bo_system = None

    if new_bo_system is not None:
        system_list.append(new_bo_system)

    offlinesec_client.func.send_to_server(data=system_list,
                                          url=UPLOAD_URL,
                                          extras=additional_keys,
                                          wait=wait,
                                          do_not_wait=do_not_wait)


def process_it(args):
    if VERSION in args and args[VERSION]:
        send_file(args)


def main():
    args = init_args()
    process_it(args)


if __name__ == '__main__':
    main()
