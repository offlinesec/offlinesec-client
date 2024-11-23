import datetime
import socket
import argparse
import json
import os
import yaml
import sys
import requests
import time
import datetime
from offlinesec_client.config import config
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
        print("The Offline Security Server %s not available now. Please try later" % (conn,))
        return False

    if result != 0:
        print("The Offline Security Server %s not available now. Please try later" % (conn,))
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


def wait_5_minutes(seconds=310):
    for remaining in range(seconds, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} seconds remaining".format(remaining))
        sys.stdout.flush()
        time.sleep(1)
    print("")
    os.system("offlinesec_get_reports")


def ask_and_wait_5_minutes(wait, do_not_wait=False, seconds=310):
    if do_not_wait:
        return
    elif wait:
        wait_5_minutes(seconds)
    else:
        resp = input("Do you want to wait 5 minutes and get report automatically" + " (y/N):").strip().lower()
        if resp is None or resp == "" or resp[0].lower() == "n":
            return
        elif resp[0].lower() == "y":
            wait_5_minutes(seconds)

def send_file_to_server(file_name, url, extras={}, wait=False, do_not_wait=False, remove_file=True):
    url = get_connection_str(url)

    send_data = get_base_json()
    if len(extras):
        send_data.update(extras)
    file_body = open(file_name, 'rb')
    files = {
        'json': ('description', json.dumps(send_data), 'application/json'),
        'file': (os.path.basename(file_name), file_body, 'application/zip')
    }

    r = requests.post(url, files=files)
    if r.content:
        try:
            response = json.loads(r.content)
            if file_body:
                file_body.close()
            if ERR_MESSAGE in response:
                if "File successfully" in response[ERR_MESSAGE]:
                    print(" * " + response[ERR_MESSAGE])
                    print(" * Your report will be available in 5 minutes (Please run offlinesec_get_reports in 5 minutes)")
                else:
                    raise "[ERROR] " + response[ERR_MESSAGE]

        except Exception as err:
            print("[ERROR] " + str(err))
            print("[ERROR] No response from the Offline Security server. Please try later")
        else:
            if remove_file:
                if os.path.isfile(file_name):
                    os.remove(file_name)
            ask_and_wait_5_minutes(wait=wait,
                                   do_not_wait=do_not_wait)


def send_to_server(data, url, extras={}, wait=False, do_not_wait=False):
    url = get_connection_str(url)

    send_data = get_base_json()
    send_data["systems"] = [item.to_dict() for item in data]
    if len(extras):
        send_data.update(extras)
    if not len(send_data["systems"]):
        print("[ERROR] No data to send to the server. Check input data")
        return

    files = {'json': ('description', json.dumps(send_data), 'application/json')}

    r = requests.post(url, files=files)
    if r.content:
        try:
            response = json.loads(r.content)
            if ERR_MESSAGE in response:
                if response[ERR_MESSAGE].startswith("The data successfully"):
                    print(" * " + response[ERR_MESSAGE])
                    print(" * Your report will be available in 5 minutes (Please run offlinesec_get_reports in 5 minutes)")
                    ask_and_wait_5_minutes(wait=wait,
                                           do_not_wait=do_not_wait)
                else:
                    print("[ERROR] " + response[ERR_MESSAGE])
                return
        except Exception as err:
            print("[ERROR] " + str(err))
            print("[ERROR] No response from the Offline Security server. Please try later")

def save_to_json(data, extras):
    json_filename =get_file_name("secnotes.json","")

    send_data = get_base_json()
    send_data["systems"] = [item.to_dict() for item in data]
    if len(extras):
        send_data.update(extras)

    with open(json_filename, 'w') as f:
        json.dump(send_data, f)
    print("* The data saved to the '%s' file. Review it and send it with option -j to the server" % (json_filename,))

def parse_date(date_from_cli):
    try:
        temp_dat = datetime.datetime.strptime(date_from_cli, "%d-%m-%Y")
    except ValueError as err:
        print(" * [Warning] Wrong the date format: %s (expected DD-MM-YYYY)" % (date_from_cli,))
    else:
        present = datetime.datetime.now()
        if temp_dat < present:
            return date_from_cli
        else:
            print(" * [Warning] The date %s from future not supported" % (date_from_cli,))

def check_sla_file(sla_file):
    if not os.path.isfile(sla_file):
        print(" * [Warning] The SLA file %s not found" % (sla_file,))
        return
    if not sla_file.lower().endswith(".yaml"):
        print(" * [Warning] Bad SLA file %s (supported only YAML format)" % (sla_file,))
        return
    try:
        with open(sla_file, 'r', encoding="utf-8") as f:
            file_content = yaml.safe_load(f)
    except Exception as err:
        print(" * [Warning] can't read the SLA file %s" % (sla_file,))
        return
    else:
        supported_keys = ["hotnews", "medium", "low", "high"]

        for key in file_content.keys():
            if key not in supported_keys:
                print(" * [Warning] Unsupported key %s in the SLA file %s" % (key, sla_file,))
                return
            if not isinstance(file_content[key], int):
                print(" * [Warning] Unsupported value %s for the key %s in the SLA file %s. Please set a numeric value" %
                      (file_content[key], key, sla_file,))
                return
        if len(file_content):
            return file_content


def send_to_server_gen(data, url, extras={}, wait=False, do_not_wait=False):
    url = get_connection_str(url)

    send_data = get_base_json()
    send_data["data"] = data
    if len(extras):
        send_data.update(extras)
    if data is None or data == "" or not len(send_data["data"]):
        print("[ERROR] No data to send to the server. Check the input")
        return

    files = {'json': ('description', json.dumps(send_data), 'application/json')}

    r = requests.post(url, files=files)
    if r.content:
        try:
            if r.status_code == 404:
                print(" * [ERROR] Bad request - %s (%s)" % (r.reason, url))
                return

            response = json.loads(r.content)
            if ERR_MESSAGE in response:
                if response[ERR_MESSAGE].startswith("The data successfully"):
                    print(" * " + response[ERR_MESSAGE])
                    print(" * Your report will be available in 5 minutes (Please run offlinesec_get_reports in 5 minutes)")
                    ask_and_wait_5_minutes(wait=wait,
                                           do_not_wait=do_not_wait)
                else:
                    print("[ERROR] " + response[ERR_MESSAGE])
                return
        except Exception as err:
            print("[ERROR] " + str(err))
            print("[ERROR] No response from the Offline Security server. Please try later")

