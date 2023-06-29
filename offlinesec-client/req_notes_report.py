import requests
import argparse
import os
import func
from const import ERR_MESSAGE
import json
from const import FILE, SYSTEM_NAME

ALLOWED_EXTENSIONS = ['txt']
ALLOWED_WITHOUT_EXTENSION = False
MAX_FILE_SIZE = 200000

UPLOAD_URL = "/file-upload"


def check_system_name(s):
    if len(s) <= 20:
        return s
    raise argparse.ArgumentTypeError("The System Name must have length less than 20")


def check_file_arg(s):
    if not os.path.isfile(s):
        raise argparse.ArgumentTypeError("File not found")

    ext = s.split('.')[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise argparse.ArgumentTypeError("File extension not supported. Only permitted: %s" %
                                         (", ".join(ALLOWED_EXTENSIONS)))

    if os.path.getsize(s) > MAX_FILE_SIZE:
        raise argparse.ArgumentTypeError("File too big. Please upload text files")

    return s


def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--%s" % (FILE,), action="store", type=check_file_arg,
                        help="File Name (Software Components)", required=True)
    parser.add_argument("-s", "--%s" % (SYSTEM_NAME,), action="store", type=check_system_name,
                        help="SAP System Name (max 20 characters)", required=False)
    parser.parse_args()
    return vars(parser.parse_args())


def send_file(file, system_name=""):
    url = func.get_connection_str(UPLOAD_URL)

    data = func.get_base_json(system_name=system_name)

    files = {
        'json': ('description', json.dumps(data), 'application/json'),
        'file': (os.path.basename(file), open(file, 'rb'), 'application/octet-stream')
    }

    r = requests.post(url, files=files)

    if r.content:
        try:
            response = json.loads(r.content)
            if ERR_MESSAGE in response:
                print(response[ERR_MESSAGE])
                return
        except:
            pass

    print("No response from server. Please try later")


def send_it(file, system_name=""):
    if not func.check_server():
        return

    send_file(file, system_name)


def main():
    args = init_args()
    if FILE in args:
        send_it(args[FILE], args[SYSTEM_NAME])


if __name__ == '__main__':
    main()
