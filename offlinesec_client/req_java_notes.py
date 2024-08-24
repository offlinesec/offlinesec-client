import argparse
import offlinesec_client.func
from offlinesec_client.const import FILE, SYSTEM_NAME, WAIT, EXCLUDE, DO_NOT_WAIT, ERROR_MSG_PREFIX, VERSION
from offlinesec_client.java_system import JAVASystem


UPLOAD_URL = "/sec-notes"
DEFAULT_SYSTEM_NAME = "JAVA System"


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
    parser.add_argument('-nw', '--do-not-wait', action='store_true', help="Don't ask to download the report")

    parser.parse_args()
    return vars(parser.parse_args())


def send_file(file_name, system_name, exclude, wait=False, do_no_wait=False):
    additional_keys = dict()
    system_list = list()

    if system_name is None or system_name == "":
        system_name = DEFAULT_SYSTEM_NAME
    additional_keys[VERSION] = offlinesec_client.__version__
    try:
        new_java_system = JAVASystem(exclude=exclude,
                                     name=system_name,
                                     softs=file_name)
    except Exception as err:
        print(ERROR_MSG_PREFIX + str(err))
        new_java_system = None

    if new_java_system is not None:
        system_list.append(new_java_system)

    offlinesec_client.func.send_to_server(data=system_list,
                                          url=UPLOAD_URL,
                                          extras=additional_keys,
                                          wait=wait,
                                          do_not_wait=do_no_wait)


def process_it(file_name, system_name="", wait=False, exclude="", do_not_wait=False):
    if not offlinesec_client.func.check_server():
        return

    if file_name:
        send_file(file_name=file_name,
                  system_name=system_name,
                  exclude=exclude,
                  wait=wait,
                  do_no_wait=do_not_wait)


def main():
    args = init_args()
    if FILE in args and args[FILE]:
        process_it(file_name=args[FILE],
                   system_name=args[SYSTEM_NAME],
                   wait=args[WAIT],
                   exclude=args[EXCLUDE],
                   do_not_wait=args[DO_NOT_WAIT])
    else:
        print("You need to specify input file(s) (-f option)")


if __name__ == '__main__':
    main()
