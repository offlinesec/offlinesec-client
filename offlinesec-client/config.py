from pathlib import Path
from const import CLIENT_ID, INST_DATE, CONNECTION_STR, APIKEY
import json

CONFIG_FILE = "config.json"
SERVER_NAME = "localhost"
PORT = "5000"
ID_LENGTH = 30
API_KEY = "k6zxdehCG23gGXLkgjcW"


class ConfigFile:
    def __init__(self):
        if not Path(CONFIG_FILE).is_file():
            self.create_file()

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
            self.data[APIKEY] = API_KEY
            flag = True
        if flag:
            self.write_file()

    @staticmethod
    def generate_conn_str():
        return SERVER_NAME + ":" + PORT

    @staticmethod
    def create_file():
        config_data = {
            CONNECTION_STR: ConfigFile.generate_conn_str(),
            CLIENT_ID: ConfigFile.generate_client_id(),
            INST_DATE: ConfigFile.generate_date()
        }
        json_data = json.dumps(config_data)

        with open(CONFIG_FILE, "w") as json_file:
            json_file.write(json_data)
            print("The config file successfully created")
            json_file.close()

    def write_file(self):
        with open(CONFIG_FILE, "w") as json_file:
            json.dump(self.data, json_file)
            json_file.close()

    def read_file(self):
        with open(CONFIG_FILE, "r") as json_file:
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
