import argparse
import os
import json
import requests
from offlinesec_client.const import FILE, SYSTEM_NAME, ERR_MESSAGE
import offlinesec_client.func
from agr_1251 import Agr1251
FILE_ALLOWED_EXTENSIONS = ["xlsx"]
ZIP_ALLOWED_EXTENSIONS = ["zip"]
MAX_FILE_SIZE = 200000

UPLOAD_URL = "/roles-upload"


def check_file_arg(s):
    return offlinesec_client.func.check_file_arg(s, FILE_ALLOWED_EXTENSIONS, MAX_FILE_SIZE)


def check_system_name(s):
    return offlinesec_client.func.check_system_name(s)


def check_variant(s):
    return offlinesec_client.func.check_variant(s)


def check_zip_arg(s):
    return offlinesec_client.func.check_file_arg(s, ZIP_ALLOWED_EXTENSIONS, MAX_FILE_SIZE)


def init_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-f", "--%s" % (FILE,), action="store", type=check_file_arg,
                        help="File XLSX (Table AGR_1251)", required=False)

    parser.add_argument("-s", "--%s" % (SYSTEM_NAME,), action="store", type=check_system_name,
                        help="SAP System Name (max 20 characters)", required=False)

    parser.add_argument("-v", "--variant", action="store", type=check_variant,
                        help="Check Variant (numeric)", required=False)

    parser.add_argument('--do-not-send', action='store_true', help="Don't upload file to server (review first)")

    parser.add_argument("-z", "--zip_file", action="store", type=check_zip_arg,
                        help="ZIP file prepared earlier", required=False)

    parser.parse_args()
    return vars(parser.parse_args())


def process_it(args):
    zip_file = None

    if FILE in args.keys() and args[FILE]:
        table = Agr1251(args[FILE])
        table.read_file()
        table.masking()
        zip_file = table.save_results()

    if not zip_file and "zip_file" in args:
        zip_file = args["zip_file"]

    if "do_not_send" in args.keys() and args["do_not_send"]:
        return

    if zip_file:
        if not offlinesec_client.func.check_server():
            return

        upload_it(zip_file, args)


def upload_it(zip_file, args):
    url = offlinesec_client.func.get_connection_str(UPLOAD_URL)

    system_name = args[SYSTEM_NAME] if SYSTEM_NAME in args else ""
    variant = args["variant"] if "variant" in args else ""

    data = offlinesec_client.func.get_base_json(system_name=system_name, variant=variant)

    file_body = open(zip_file, 'rb')

    files = {
        'json': ('description', json.dumps(data), 'application/json'),
        'file': (os.path.basename(zip_file), file_body, 'application/zip')
    }

    print("Uploading file %s" % (os.path.basename(zip_file)))
    r = requests.post(url, files=files)

    if r.content:
        try:
            response = json.loads(r.content)

            if ERR_MESSAGE in response:
                print(" * " + response[ERR_MESSAGE])
                if file_body:
                    file_body.close()
                if os.path.isfile(zip_file):
                    os.remove(zip_file)
                return
        except :
            pass

    print("No response from server. Please try later")


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
