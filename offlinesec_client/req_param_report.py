import argparse
import os
import offlinesec_client.func
from offlinesec_client.const import FILE, SYSTEM_NAME, WAIT, DO_NOT_WAIT, VERSION
from offlinesec_client.rsparam import RsparamReport

FILE_ALLOWED_EXTENSIONS = ["xlsx"]
ZIP_ALLOWED_EXTENSIONS = ["zip"]
MAX_FILE_SIZE = 200000

UPLOAD_URL = "/profile-upload"


def check_system_name(s):
    if len(s) <= 20:
        return s
    raise argparse.ArgumentTypeError("The System Name must have length less than 20")


def check_file_arg(s):
    if not os.path.isfile(s):
        raise argparse.ArgumentTypeError("File not found (-f)")

    ext = s.split('.')[-1].lower()
    if ext not in FILE_ALLOWED_EXTENSIONS:
        raise argparse.ArgumentTypeError("File type not supported. Only allowed extensions: %s" %
                                         (", ".join(FILE_ALLOWED_EXTENSIONS)))

    if os.path.getsize(s) > MAX_FILE_SIZE:
        raise argparse.ArgumentTypeError("File too big (-f)")

    return s


def check_zip_arg(s):
    if not os.path.isfile(s):
        raise argparse.ArgumentTypeError("File not found (-z)")

    ext = s.split('.')[-1].lower()
    if ext not in ZIP_ALLOWED_EXTENSIONS:
        raise argparse.ArgumentTypeError("File type not supported. Only allowed extensions: %s" %
                                         (", ".join(ZIP_ALLOWED_EXTENSIONS)))

    if os.path.getsize(s) > MAX_FILE_SIZE:
        raise argparse.ArgumentTypeError("File too big (-z)")

    return s


def check_variant(s):
    try:
        num = int(s)
    except:
        raise argparse.ArgumentTypeError("Variant must be numeric")
    return num


def init_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-f", "--%s" % (FILE,), action="store", type=check_file_arg,
                        help="File XLSX (Profile Parameters)", required=False)

    parser.add_argument("-s", "--%s" % (SYSTEM_NAME,), action="store", type=check_system_name,
                        help="SAP System Name (max 20 characters)", required=False)

    parser.add_argument("-v", "--variant", action="store", type=check_variant,
                        help="Check Variant (numeric)", required=False)

    parser.add_argument('--do-not-send', action='store_true', help="Don't upload file to server (review first)")

    parser.add_argument("-z", "--zip_file", action="store", type=check_zip_arg,
                        help="ZIP file prepared earlier", required=False)

    parser.add_argument('-w', '--wait', action='store_true', help="Wait 5 minutes and download the report")
    parser.add_argument('-nw', '--do-not-wait', action='store_true', help="Don't ask to download the report")


    parser.parse_args()
    return vars(parser.parse_args())


def process_it(args):
    zip_file = None

    if FILE in args.keys() and args[FILE]:
        file = args[FILE]
        rep = RsparamReport(file)
        zip_file = rep.save_to_file()

    if not zip_file and "zip_file" in args:
        zip_file = args["zip_file"]

    if "do_not_send" in args.keys() and args["do_not_send"]:
        return

    if zip_file:
        if not offlinesec_client.func.check_server():
            return
        additional_keys = dict()
        additional_keys[VERSION] = offlinesec_client.__version__

        if "variant" in args and args["variant"] is not None:
            additional_keys["variant"] = args["variant"]

        if SYSTEM_NAME in args and args[SYSTEM_NAME] is not None:
            additional_keys[SYSTEM_NAME] = args[SYSTEM_NAME]

        wait = args[WAIT] if WAIT in args else None
        do_not_wait = args[DO_NOT_WAIT] if DO_NOT_WAIT in args else None

        offlinesec_client.func.send_file_to_server(file_name=zip_file,
                                                   extras=additional_keys,
                                                   url=UPLOAD_URL,
                                                   wait=wait,
                                                   do_not_wait=do_not_wait)


def main():
    args = init_args()
    if args["file"] or args["zip_file"]:
        if (args["file"] and not args["zip_file"]) or (not args["file"] and args["zip_file"]):
            process_it(args)
        else:
            print("You can't specify -f (xlsx) and -z (previously prepared zip file) options at the same request")
    else:
        print("You need to specify file using -f (xlsx) or -z (previously prepared zip file) options")


if __name__ == '__main__':
    main()

