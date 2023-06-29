from config import config
import socket
from const import APIKEY, CLIENT_ID, INST_DATE, ACTION, SYSTEM_NAME, CONNECTION_STR


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
    return "http://" + config.data[CONNECTION_STR] + url


def get_base_json(action="", system_name=""):
    data = dict()

    data[APIKEY] = config.data[APIKEY]
    data[CLIENT_ID] = config.data[CLIENT_ID]
    data[INST_DATE] = config.data[INST_DATE]

    if action:
        data[ACTION] = action
    if system_name:
        data[SYSTEM_NAME] = system_name
    return data
