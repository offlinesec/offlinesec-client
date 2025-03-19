import argparse
import offlinesec_client.func
from offlinesec_client.const import (FILE, SYSTEM_NAME, KRNL_PL, KRNL_VER, CWBNTCUST, VERSION,
                                     ERROR_MSG_PREFIX, EXCLUDE, DO_NOT_WAIT, WAIT, GUISCRIPT, VARIANT)
from offlinesec_client.abap_system import ABAPSystem
from offlinesec_client.masking import Masking, SAPSID_MASK

UPLOAD_URL = "/sec-notes"
DEFAULT_SYSTEM_NAME = "ABAP System"


def check_version(s):
    return offlinesec_client.func.check_num_param("".join(s.split('.')), "Kernel Version")


def check_patch_level(s):
    return offlinesec_client.func.check_num_param(s, "Kernel Patch Level")


def check_system_name(s):
    return offlinesec_client.func.check_system_name(s)

def check_file_arg_sla(s):
    res = offlinesec_client.func.check_file_arg(s, ['yaml'], 200000)
    return res

def check_variant(s):
    return offlinesec_client.func.check_variant(s)


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
    parser.add_argument("--host-agent-ver", action="store", type=check_version,
                        help="Host Agent Version (for instance 7.22)", required=False)
    parser.add_argument("--host-agent-patch", action="store", type=check_patch_level,
                        help="Host Agent Patch Level (for instance 12)", required=False)
    parser.add_argument("-c", "--%s" % (CWBNTCUST,), action="store", type=check_cwbntcust,
                        help="CWBNTCUST table (txt or xlsx)", required=False)
    parser.add_argument("-cd", "--dev-cwbntcust", action="store", type=check_cwbntcust,
                        help="CWBNTCUST table (txt or xlsx) on DEV system", required=False)
    parser.add_argument('-nr', '--keep-not_relevant', action='store_true', help="Do not exclude notes marked as 'Not Relevant'")

    parser.add_argument("-e", "--exclude", action="store",
                        help='Exclude SAP security notes', required=False)
    parser.add_argument("-v", "--variant", action="store", type=check_variant,
                        help="Check Variant (numeric)", required=False)
    parser.add_argument("-l", "--sla", action="store", type=check_file_arg_sla,
                        help="SLA file in YAML format")
    parser.add_argument('--do-not-send', action='store_true', help="Don't upload data to the server (review first)")
    parser.add_argument("-d","--date", action='store', help="The report on specific date in past (DD-MM-YYYY)")

    parser.add_argument('--guiscript', action='store_true', help="Run GUI script to prepare the input data")
    parser.parse_args()
    return vars(parser.parse_args())

def send_file(args):
    additional_keys = dict()
    system_list = list()

    system_name = args[SYSTEM_NAME] if SYSTEM_NAME in args else None
    kernel_version = args[KRNL_VER] if KRNL_VER in args else None
    kernel_patch = args[KRNL_PL] if KRNL_PL in args else None
    cwbntcust = args[CWBNTCUST] if CWBNTCUST in args else None
    cwbntcust_dev = args["dev_cwbntcust"] if "dev_cwbntcust" in args else None
    file = args[FILE] if FILE in args else None
    exclude = args[EXCLUDE] if EXCLUDE in args else None
    wait = True
    do_not_wait = False

    if system_name is None or system_name == "":
        system_name = DEFAULT_SYSTEM_NAME
    else:
        sapsid_masking = Masking(SAPSID_MASK)
        system_name = sapsid_masking.do_mask(system_name)
        sapsid_masking.save_masking()

    additional_keys[VERSION] = offlinesec_client.__version__

    if "variant" in args and args["variant"] is not None:
        additional_keys["variant"] = args["variant"]

    if "host_agent_ver" in args and args["host_agent_ver"] is not None:
        additional_keys["host_agent_ver"] = args["host_agent_ver"]

    if "host_agent_patch" in args and args["host_agent_patch"] is not None:
        additional_keys["host_agent_patch"] = args["host_agent_patch"]

    if "date" in args and args["date"] is not None:
        additional_keys["on_date"] = offlinesec_client.func.parse_date(args["date"])

    if "sla" in args and args["sla"] is not None:
        additional_keys["sla"] = offlinesec_client.func.check_sla_file(args["sla"])

    if "keep_not_relevant" in args and args["keep_not_relevant"]:
        additional_keys["keep_not_relevant"] = True

    try:
        new_abap_system = ABAPSystem(krnl_version=kernel_version,
                                     krnl_patch=kernel_patch,
                                     cwbntcust=cwbntcust,
                                     cwbntcust_dev=cwbntcust_dev,
                                     exclude=exclude,
                                     name=system_name,
                                     softs=file)
    except Exception as err:
        print(ERROR_MSG_PREFIX + str(err))
        new_abap_system = None

    if new_abap_system is not None:
        system_list.append(new_abap_system)

    if "do_not_send" in args and args["do_not_send"]:
        offlinesec_client.func.save_to_json(data=system_list,
                                            extras=additional_keys)
        return

    offlinesec_client.func.send_to_server(data=system_list,
                                          url=UPLOAD_URL,
                                          extras=additional_keys,
                                          wait=wait,
                                          do_not_wait=do_not_wait)


def process_it(args):
    if not offlinesec_client.func.check_server():
        return
    guiscript = args[GUISCRIPT] if GUISCRIPT in args else None
    system_name = args[SYSTEM_NAME] if SYSTEM_NAME in args else None
    wait = args[WAIT] if WAIT in args else None

    if guiscript:
        import platform
        if platform.system() == 'Windows':
            from offlinesec_client.sap_gui import SAPConnection
            conn = SAPConnection.sap_notes_report(system_name=system_name,
                                                  wait=wait)
        else:
            print("SAP GUI Scripting not supported on this platform. Run SAP Gui Scripting only on Windows platform")
        return

    send_file(args)


def main():
    args = init_args()

    if (FILE in args and args[FILE]) or ("guiscript" in args and args["guiscript"]):
        process_it(args)
    else:
        print("You need to specify input file(s) (-f option) or --guiscript option (to run gui script)")


if __name__ == '__main__':
    main()
