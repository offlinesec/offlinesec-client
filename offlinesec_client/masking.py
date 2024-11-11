import os
from pathlib import Path
import json

SUBDIR = ".offlinesec_client"

ROLE_MASK = "ROLENAME"
RFCDEST_MASK = "RFCDEST"
SAPSID_MASK = "SAPSID"
HOST_MASK = "HOST"
PATH_MASK = "PATH"
USER_MASK = "USERNAME"

FILENAMES = {
    ROLE_MASK : "role_masking.json",
    RFCDEST_MASK : "rfcdes_masking.json",
    SAPSID_MASK : "sid_masking.json",
    HOST_MASK : "host_masking.json",
    PATH_MASK : "path_masking.json",
    USER_MASK : "user_masking.json"
}

TEMPLATES = {
    ROLE_MASK : "Z_ROLE_%s",
    RFCDEST_MASK : "Z_RFCDES_%s",
    SAPSID_MASK : "Z_SID_%s",
    HOST_MASK : "Z_HOST_%s",
    PATH_MASK : "Z_PATH_%s",
    USER_MASK : "Z_USER_%s"
}


class Masking:
    def __init__(self, masking_type):
        if masking_type not in FILENAMES.keys():
            raise ValueError("Unsupported masking type %s" % (masking_type,))
        self.masking_type = masking_type
        self.data = list()
        self.read_masking()

    def get_file_name(self):
        file_name = os.path.join(Path.home(), SUBDIR, FILENAMES[self.masking_type])
        return file_name

    def get_folder_name(self):
        folder = os.path.join(Path.home(), SUBDIR)
        return folder

    def do_mask(self, in_value):
        tmpl = TEMPLATES[self.masking_type]

        if in_value.upper() in self.data:
            idx = self.data.index(in_value.upper())
            return tmpl % (str(idx),)
        else:
            pos = len(self.data)
            self.data.append(in_value.upper())
            return tmpl % (str(pos),)

    def do_unmask(self, in_value):
        tmpl = TEMPLATES[self.masking_type]
        tmpl_len = len(tmpl) - 2
        if not in_value.startswith(tmpl[:-2]):
            return in_value
        if not len(self.data):
            return in_value
        try:
            num = int(in_value[tmpl_len:])
        except ValueError:
            return in_value

        if len(self.data) >= num:
            return self.data[num]
        else:
            return in_value

    def read_masking(self):
        file_name = self.get_file_name()

        if not os.path.isfile(file_name):
            self.data = list()
        else:
            with open(file_name, "r") as f:
                self.data = json.load(f)

    def save_masking(self):
        folder = self.get_folder_name()
        os.makedirs(folder, exist_ok=True)

        file_name = self.get_file_name()

        with open(file_name, "w") as f:
            json.dump(self.data, f)
