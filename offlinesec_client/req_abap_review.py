import argparse
import os
import zipfile
import binascii
import json
import requests
import offlinesec_client.func as func
from offlinesec_client.const import SYSTEM_NAME, ERR_MESSAGE

UPLOAD_URL = "/tran-upload"


def check_system_name(s):
    return func.check_system_name(s)


def check_variant(s):
    return func.check_variant(s)


def check_path_arg(s):
    if os.path.isdir(s):
        return s
    raise argparse.ArgumentTypeError("You must choose the transport directory (-p)")


def check_file_format(filename):
    magic = "0000003320543030"
    with open(filename, 'rb') as f:
        first_8 = f.read(8)
        if binascii.hexlify(bytearray(first_8)).decode('ascii') == magic:
            return True
    return False


def enum_files(fpath):
    outlist = list()
    for file in os.listdir(fpath):
            full_path = os.path.join(fpath, file)
            if os.path.isfile(full_path):
                if check_file_format(full_path):
                    outlist.append(full_path)
    return outlist


def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", action="store", help="Transport Directory", type=check_path_arg, required=True)
    parser.add_argument("-s", "--%s" % (SYSTEM_NAME,), action="store", type=check_system_name,
                        help="SAP System Name (max 20 characters)", required=False)
    parser.add_argument("-v", "--variant", action="store", type=check_variant,
                        help="Check Variant (numeric)", required=False)
    parser.parse_args()
    args = parser.parse_args()
    return vars(args)


def print_errors(errors):
    for error in errors:
        print(error)


def upload_it(zip_file, args):
    url = func.get_connection_str(UPLOAD_URL)

    system_name = args[SYSTEM_NAME] if SYSTEM_NAME in args else ""
    variant = args["variant"] if "variant" in args else ""

    data = func.get_base_json(system_name=system_name, variant=variant)

    with open(zip_file, 'rb') as file_body:
        files = {
            'json': ('description', json.dumps(data), 'application/json'),
            'file': (os.path.basename(zip_file), file_body, 'application/zip')
        }
        print(" * Uploading file %s to the server. Please wait (Maximum file size: 100MB)" % (
            os.path.basename(zip_file)))
        try:
            r = requests.post(url, files=files)
        except TimeoutError:
            print("Connection timed out")
        else:
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
                except Exception as err:
                    print(r.content)


def zip_files(files):
    print(" * %s transport files found in the directory. Compressing" % (len(files),))
    zipfilename = func.get_file_name("tran.zip")
    zip = zipfile.ZipFile(zipfilename, mode='w', compression=zipfile.ZIP_DEFLATED, compresslevel=9)

    for filename in files:
        zip.write(filename, os.path.basename(filename), compress_type=zipfile.ZIP_DEFLATED)

    zip.close()
    if os.path.isfile(zip.filename):
        stat = os.stat(zip.filename)
        size_mb = stat.st_size / (1024 * 1024)
        if size_mb <= 100:
            print(" * ZIP file created. File size is %s MB" % (round(size_mb),))
            return zip.filename
        else:
            print("[ERROR] ZIP file is too big (Maximum file size: 100MB)")


def main():
    args = init_args()
    if "path" in args and args["path"]:
        file_list = enum_files(args["path"])
        if not len(file_list):
            print("[ERROR] Transport files not found in the directory")
            return
        temp_file = zip_files(file_list)
        if temp_file is None or temp_file == "":
            print("[ERROR] ZIP archive not created due to error")
            return
        upload_it(temp_file, args)
        if os.path.isfile(temp_file):
            os.remove(temp_file)


if __name__ == '__main__':
    main()
