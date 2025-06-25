import argparse
import json
import offlinesec_client.func

UPLOAD_URL = "/sec-notes"
YAML_ALLOWED_EXTENSIONS = ["yaml"]
MAX_YAML_FILE_SIZE = 10000

class OfflineSecRequest:
    def __init__(self, request_type, upload_url=None):
        self.parser = None
        self.inargs = self.init_argprase()
        self.request_type = request_type
        if upload_url is None:
            upload_url = UPLOAD_URL
        self.upload_url = upload_url

    def init_argprase(self):
        parser = argparse.ArgumentParser()

        parser.add_argument("-f", "--file", action="store", type=OfflineSecRequest.check_yaml_arg,
                            help="YAML configuration file for the report", required=True)
        parser.add_argument("-v", "--variant", action="store", type=OfflineSecRequest.check_variant,
                            help="check variant (needed for specific check, numeric)", required=False)
        parser.add_argument('--do-not-send', action='store_true', help="don't upload the data to the server (review first)")

        self.extra_parser_keys(parser)

        parser.parse_args()
        return vars(parser.parse_args())

    def extra_parser_keys(self, parser):
        pass

    def extra_addit_keys(self, additional_keys):
        pass

    def get_data(self):
        return

    def do_masking(self, data):
        return data

    def process(self, wait=True, do_not_wait=False):
        data = self.get_data()
        if not data:
            print(" * [ERROR] No data to send to the server")
            return

        self.do_masking(data)

        if "do_not_send" in self.inargs.keys() and self.inargs["do_not_send"]:
            OfflineSecRequest.save_json(data)
            return

        addit_keys = self.gen_addit_keys()

        offlinesec_client.func.send_to_server_gen(data=data,
                                                  url=self.upload_url,
                                                  extras=addit_keys,
                                                  wait=wait,
                                                  do_not_wait=do_not_wait)

    @staticmethod
    def is_error_in_yaml(yaml_file):
        if hasattr(yaml_file, "errors"):
            if len(yaml_file.errors):
                err_msgs = map(lambda x: " * [ERROR] " + x, yaml_file.errors)
                for msg in err_msgs:
                    print(msg)
                return True

        if hasattr(yaml_file, "warnings"):
            if len(yaml_file.warnings):
                warn_msgs = map (lambda x: " * [ERROR] " + x, yaml_file.warnings)
                for msg in warn_msgs:
                    print(msg)

                resp = input("There are some warning. Do you want to continue?" + " (y/N):").strip().lower()
                if resp is None or resp == "" or resp[0].lower() == "n":
                    return True

        return False

    def gen_addit_keys(self):
        additional_keys = dict()
        if "id" in self.inargs.keys() and self.inargs["id"]:
            additional_keys["id"] = self.inargs["id"]

        additional_keys["version"] = offlinesec_client.__version__
        additional_keys["request_type"] = self.request_type

        if "variant" in self.inargs.keys() and self.inargs["variant"]:
            additional_keys["variant"] = self.inargs["variant"]

        self.extra_addit_keys(additional_keys)

        return additional_keys

    @staticmethod
    def check_yaml_arg(s):
        return offlinesec_client.func.check_file_arg(s, YAML_ALLOWED_EXTENSIONS, MAX_YAML_FILE_SIZE)

    @staticmethod
    def check_variant(s):
        return offlinesec_client.func.check_variant(s)

    @staticmethod
    def save_json(data_to_save):
        json_filename = offlinesec_client.func.get_file_name("new_data.json")
        with open(json_filename, 'w') as f:
            json.dump(data_to_save, f)
        print(
            "* The data saved to the '%s' file. Review it and send it with option -j to the server" % (json_filename,))

