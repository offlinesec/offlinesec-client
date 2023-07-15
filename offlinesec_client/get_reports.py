import os.path
from pathlib import Path
from offlinesec_client.const import ACTION, FILENAME, ERR_MESSAGE
import json
import time
import offlinesec_client.func
import requests

UPLOAD_URL = "/get-status"
ACTION_GET_FILE_NAMES = "GET_REPORTS"
ACTION_GET_FILE = "GET_FILE"
ACTION_CONF = "CONFIRMATION"


def get_status():
    if not offlinesec_client.func.check_server():
        return
    get_statuses()


def get_file_name(filename):
    downloads_path = str(Path.home() / "Downloads")
    full_path = os.path.join(downloads_path, filename)

    if not os.path.isfile(full_path):
        return full_path
    else:
        base = ".".join(filename.split('.')[:-1])
        ext = "." + filename.split('.')[-1]

        for i in range(1, 100):
            full_path = os.path.join(downloads_path, base + "_" + '%03d' % i + ext)
            if not os.path.isfile(full_path):
                return full_path


def get_statuses():
    url = offlinesec_client.func.get_connection_str(UPLOAD_URL)
    data = offlinesec_client.func.get_base_json(action=ACTION_GET_FILE_NAMES)
    files = {'json': ('Check available reports to download', json.dumps(data), 'application/json')}
    r = requests.post(url, files=files)

    if not r.content:
        print("No answer from server. Please try later")
        return

    try:
        response = json.loads(r.content)
    except:
        print("Couldn't parse server response. Please update offlinesec-client software")
        return

    if ERR_MESSAGE in response.keys():
        print(response["message"])
        return

    if "files" not in response.keys() or "files_num" not in response.keys():
        print("Couldn't parse server response. Please update offlinesec-client software")
        return

    if "errors" in response.keys() and response["errors"]:
        print("Some Reports not generated due to errors:")
        for error in response["errors"]:
            print(" * " + error)

    print("%s report(s) are available to download from server" % (response["files_num"],))

    i = 0
    for file in response["files"]:
        new_data = offlinesec_client.func.get_base_json(action=ACTION_GET_FILE)
        new_data[FILENAME] = file
        print("Downloading the report '%s'" % (file,))
        files = {'json': ('Get file', json.dumps(new_data), 'application/json')}
        r = requests.post(url, files=files)
        full_path = get_file_name(file)

        if len(r.content) < 1000:
            print(" * File not loaded due to error. Please try later")
            continue

        if r.content:
            open(full_path, 'wb').write(r.content)

        if os.path.isfile(full_path):
            i += 1
            print(" * The report '%s' successfully downloaded (%s bytes)" % (file, len(r.content),))
            new_data = offlinesec_client.func.get_base_json(action=ACTION_CONF)
            new_data[FILENAME] = file
            files = {'json': ('Confirmation', json.dumps(new_data), 'application/json')}
            r = requests.post(url, files=files)
            time.sleep(1)

    print("%s report(s) were downloaded. Please check 'Downloads' folder" % (i,))


def main():
    get_status()


if __name__ == '__main__':
    main()
