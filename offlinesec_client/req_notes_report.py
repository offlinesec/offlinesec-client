import argparse
import offlinesec_client.func
from offlinesec_client.const import (FILE, SYSTEM_NAME, KRNL_PL, KRNL_VER, CWBNTCUST, VERSION,
                                     ERROR_MSG_PREFIX, EXCLUDE, DO_NOT_WAIT, WAIT, GUISCRIPT)
from offlinesec_client.abap_system import ABAPSystem

UPLOAD_URL = "/sec-notes"
DEFAULT_SYSTEM_NAME = "ABAP System"


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
                        help='Exclude SAP security notes', required=False)
    parser.add_argument('-w', '--wait', action='store_true', help="Wait 5 minutes and download the report")
    parser.add_argument('-nw', '--do-not-wait', action='store_true', help="Don't ask to download the report")

    parser.add_argument('--guiscript', action='store_true', help="Run GUI script to prepare the input data")
    parser.parse_args()
    return vars(parser.parse_args())


def send_file(file, system_name="", kernel_version="", kernel_patch="",
              cwbntcust="", exclude="", wait=False, do_not_wait=False):
    additional_keys = dict()
    system_list = list()

    if system_name is None or system_name == "":
        system_name = DEFAULT_SYSTEM_NAME
    additional_keys[VERSION] = offlinesec_client.__version__

    try:
        new_abap_system = ABAPSystem(krnl_version=kernel_version,
                                     krnl_patch=kernel_patch,
                                     cwbntcust=cwbntcust,
                                     exclude=exclude,
                                     name=system_name,
                                     softs=file)
    except Exception as err:
        print(ERROR_MSG_PREFIX + str(err))
        new_abap_system = None

    if new_abap_system is not None:
        system_list.append(new_abap_system)

    offlinesec_client.func.send_to_server(data=system_list,
                                          url=UPLOAD_URL,
                                          extras=additional_keys,
                                          wait=wait,
                                          do_not_wait=do_not_wait)


def process_it(file, system_name="", kernel_version="", kernel_patch="", cwbntcust="",
               guiscript=False, wait=False, exclude="", do_not_wait=False):
    if not offlinesec_client.func.check_server():
        return

    if guiscript:
        import platform
        if platform.system() == 'Windows':
            from offlinesec_client.sap_gui import SAPConnection
            conn = SAPConnection.sap_notes_report(system_name=system_name,
                                                  wait=wait)
        else:
            print("SAP GUI Scripting not supported on this platform. Run SAP Gui Scripting only on Windows platform")
        return

    send_file(file=file,
              system_name=system_name,
              kernel_version=kernel_version,
              kernel_patch=kernel_patch,
              cwbntcust=cwbntcust,
              exclude=exclude,
              wait=wait,
              do_not_wait=do_not_wait)


def main():
    args = init_args()

    if (FILE in args and args[FILE]) or ("guiscript" in args and args["guiscript"]):
        process_it(file=args[FILE],
                   system_name=args[SYSTEM_NAME],
                   kernel_version=args[KRNL_VER],
                   kernel_patch=args[KRNL_PL],
                   cwbntcust=args[CWBNTCUST],
                   guiscript=args[GUISCRIPT],
                   wait=args[WAIT],
                   exclude=args[EXCLUDE],
                   do_not_wait=args[DO_NOT_WAIT])
    else:
        print("You need to specify input file(s) (-f option) or --guiscript option (to run gui script)")


if __name__ == '__main__':
    main()
