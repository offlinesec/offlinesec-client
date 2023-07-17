import os.path
from pathlib import Path
from offlinesec_client.const import CLIENT_ID, INST_DATE, CONNECTION_STR, API_KEY_VALUE, APIKEY
import json
import sysconfig

CONFIG_FILE = "config.json"
SERVER_NAME = "offlinesec.com"
PORT = "443"
ID_LENGTH = 128


class ConfigFile:
    def __init__(self):
        full_path = os.path.join(sysconfig.get_path('purelib'), 'offlinesec_client', CONFIG_FILE)
        if not Path(full_path).is_file():
            self.create_file(full_path)

        self.data = dict()
        self.read_file()
        self.check_params()

    def check_params(self):
        flag = False
        if CLIENT_ID not in self.data.keys():
            self.data[CLIENT_ID] = ConfigFile.generate_client_id()
            flag = True
        if INST_DATE not in self.data.keys():
            self.data[INST_DATE] = ConfigFile.generate_date()
            flag = True
        if CONNECTION_STR not in self.data.keys():
            self.data[CONNECTION_STR] = ConfigFile.generate_conn_str()
            flag = True
        if APIKEY not in self.data.keys():
            self.data[APIKEY] = API_KEY_VALUE
            flag = True
        if flag:
            self.write_file()

    @staticmethod
    def generate_conn_str():
        return SERVER_NAME + ":" + PORT

    @staticmethod
    def create_file(path):
        config_data = {
            CONNECTION_STR: ConfigFile.generate_conn_str(),
            CLIENT_ID: ConfigFile.generate_client_id(),
            INST_DATE: ConfigFile.generate_date()
        }
        json_data = json.dumps(config_data)

        with open(path, "w") as json_file:
            json_file.write(json_data)
            print("The config file successfully created")
            json_file.close()

    def write_file(self):
        os.makedirs(os.path.dirname(os.path.join(sysconfig.get_path('purelib'), 'offlinesec_client')), exist_ok=True)
        full_path = os.path.join(sysconfig.get_path('purelib'), 'offlinesec_client', CONFIG_FILE)
        with open(full_path, "w") as json_file:
            json.dump(self.data, json_file)

    def read_file(self):
        full_path = os.path.join(sysconfig.get_path('purelib'), 'offlinesec_client', CONFIG_FILE)
        with open(full_path, "r") as json_file:
            try:
                data = json.load(json_file)
            except:
                data = dict()
            json_file.close()
        self.data = data

    @staticmethod
    def generate_date():
        from datetime import date

        today = date.today()
        return str(today)

    @staticmethod
    def generate_client_id():
        import random
        import string

        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for i in range(ID_LENGTH))


config = ConfigFile()
