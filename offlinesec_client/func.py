from .config import config
import socket
import argparse
import json
import os
import requests
from offlinesec_client.const import ERR_MESSAGE
from offlinesec_client.cwbntcust import Cwbntcust
from offlinesec_client.const import APIKEY, CLIENT_ID, INST_DATE, ACTION, SYSTEM_NAME, CONNECTION_STR, CWBNTCUST,\
    KRNL_PL, KRNL_VER, VAR


def check_server():
    conn = config.data[CONNECTION_STR]
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        result = sock.connect_ex((conn.split(":")[0], int(conn.split(":")[1])))
    except:
        print("The Server %s not available now. Please try later" % (conn,))
        return False

    if result != 0:
        print("The Server %s not available now. Please try later" % (conn,))
        return False

    sock.close()
    return True


def get_connection_str(url):
    return "https://" + config.data[CONNECTION_STR] + url


def get_base_json(action="", system_name="", variant="",
                  kernel_version="", kernel_patch="", cwbntcust="", exclude=""):
    data = dict()

    data[APIKEY] = config.data[APIKEY]
    data[CLIENT_ID] = config.data[CLIENT_ID]
    data[INST_DATE] = config.data[INST_DATE]

    if action:
        data[ACTION] = action
    if system_name:
        data[SYSTEM_NAME] = system_name
    if variant:
        data[VAR] = variant
    if kernel_patch:
        data[KRNL_PL] = kernel_patch
    if kernel_version:
        data[KRNL_VER] = kernel_version
    if cwbntcust:
        tbl = Cwbntcust(cwbntcust)
        notes = tbl.read_file()
        if exclude:
            excludes = [note_id.strip() for note_id in exclude.split(",")]
            for note_id in excludes:
                if note_id != "":
                    notes.append(note_id)
        if notes:
            data[CWBNTCUST] = notes
    return data


def get_file_name(filename, folder=""):
    full_path = os.path.join(folder, filename)

    if not os.path.isfile(full_path):
        return full_path
    else:
        base = ".".join(filename.split('.')[:-1])
        ext = "." + filename.split('.')[-1]

        for i in range(1, 100):
            full_path = os.path.join(folder, base + "_" + '%03d' % i + ext)
            if not os.path.isfile(full_path):
                return full_path


def check_system_name(s):
    if len(s) <= 20:
        return s
    raise argparse.ArgumentTypeError("The System Name must have length less than 20 characters")


def check_file_arg(s, extensions=list(), max_size=0):
    if not os.path.isfile(s):
        raise argparse.ArgumentTypeError("File %s not found" % (s,))

    if len(extensions):
        ext = s.split('.')[-1].lower()
        if ext not in extensions:
            raise argparse.ArgumentTypeError("File type %s not supported. Permitted extensions: %s" % (ext,
                                                                                                ", ".join(extensions)))
    if max_size:
        if os.path.getsize(s) > max_size:
            raise argparse.ArgumentTypeError("File %s too big" % (s,))

    return s


def check_variant(s):
    try:
        num = int(s)
    except:
        raise argparse.ArgumentTypeError("Variant must be numeric")
    return num


def check_num_param(s, title="Argument"):
    try:
        num = int(s)
    except:
        raise argparse.ArgumentTypeError("%s must be numeric" % (title,))
    return num


def send_to_server(data, url, extras={}):
    url = get_connection_str(url)

    send_data = get_base_json()
    send_data["systems"] = [item.to_dict() for item in data]
    if len(extras):
        send_data.update(extras)

    files = {'json': ('description', json.dumps(send_data), 'application/json')}

    r = requests.post(url, files=files)
    if r.content:
        try:
            response = json.loads(r.content)
            if ERR_MESSAGE in response:
                if response[ERR_MESSAGE].startswith("The data successfully"):
                    print(" * " + response[ERR_MESSAGE])
                else:
                    print("[ERROR] " + response[ERR_MESSAGE])
                return
        except:
            pass

    print("[ERROR] No response from the Offline Security server. Please try later")
