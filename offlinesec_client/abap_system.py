from offlinesec_client.sap_system import SAPSystem
from offlinesec_client.cwbntcust import Cwbntcust
import os
import re

ABAP = "ABAP"
KRNL_VERSION = "krnl_version"
KRNL_PATCH = "krnl_patch"
ABAP_SOFTS = "softs"
CWBNTCUST = "cwbntcust"
EXCLUDE_NOTES = "exclude"
ABAP_NAME = "name"


class ABAPSystem (SAPSystem):
    def __init__(self, **args):
        super().__init__(args["name"])
        self.type = ABAP
        root_dir = args["root_dir"] if "root_dir" in args else None

        self.kernel_version = ABAPSystem.check_kernel_version(args["krnl_version"]) \
            if ("krnl_version" in args.keys() and args["krnl_version"] is not None and args["krnl_version"] != "") else ""

        self.kernel_patch = ABAPSystem.check_kernel_patch(args["krnl_patch"]) \
            if "krnl_patch" in args.keys() and args["krnl_patch"] is not None and args["krnl_patch"] != ""else ""

        self.softs = ABAPSystem.parse_softs_file(args["softs"], root_dir) \
            if "softs" in args.keys() else list()

        if self.kernel_version == "" and len(self.softs) == 0:
            raise ValueError("[ERROR] System '{}' you must specify 'softs' or 'krnl_version' keys"
                             .format(self.system_name))

        self.cwbntcust = ABAPSystem.parse_cwbntcust_file(args["cwbntcust"], root_dir, self.system_name) \
            if "cwbntcust" in args.keys() and args["cwbntcust"] is not None and args["cwbntcust"] != ""else list()

        self.exclude = ABAPSystem.parse_exclude_file(args["exclude"], root_dir, self.system_name) \
            if "exclude" in args.keys() and args["exclude"] is not None and args["exclude"] != ""else list()

    @staticmethod
    def check_kernel_version(kernel_version):
        kernel_version = str(kernel_version).replace(',', '')
        kernel_version = kernel_version.replace('.', '')
        try:
            return int(kernel_version)
        except ValueError:
            raise ValueError("Kernel Version must be numeric. For example: 7.53 or 753.")

    @staticmethod
    def check_kernel_patch(kernel_patch):
        kernel_patch = str(kernel_patch).replace(',', '')
        kernel_patch = kernel_patch.replace('.', '')
        try:
            return int(kernel_patch)
        except ValueError:
            raise ValueError("Kernel Patch Level must be numeric. For example: 1100.")

    @staticmethod
    def parse_softs_file(softs_file, root_dir):
        if root_dir:
            path = os.path.join(root_dir, softs_file)
        else:
            path = softs_file
        if not os.path.exists(path):
            raise FileNotFoundError("File %s not found" % (path,))

        if not softs_file.upper().endswith(".TXT"):
            raise ValueError("File {} has wrong extension. Only TXT files supported".format(softs_file))
        softs = list()
        with open(path, 'r', encoding="utf-8") as f:
            num = 0
            for line in f:
                num += 1
                line = line.strip('\r\n').strip()
                line = re.sub(' +', ' ', line).split()
                if len(line) > 4:
                    soft = line[0]
                    soft = soft.encode("utf-8").decode("utf-8-sig")
                    # print(soft.decode('utf-8'))
                    version = line[1]
                    pkg_num = line[2].lstrip("0")
                    if pkg_num == "":
                        pkg_num = "0"
                    package = line[3]
                    softs.append((soft, version, pkg_num, package))
                else:
                    print("[ERROR] File %s Line %s: %s" % (softs_file, str(num), " ".join(line)))

        if not len(softs):
            raise ValueError("File {} has wrong format".format(softs_file))

        return softs

    @staticmethod
    def parse_cwbntcust_file(cwbntcust_file, root_dir, system_name):
        if root_dir:
            path = os.path.join(root_dir, cwbntcust_file)
        else:
            path = cwbntcust_file
        if not os.path.exists(path):
            raise FileNotFoundError("File %s not found" % (cwbntcust_file,))

        if not (cwbntcust_file.upper().endswith(".TXT") or cwbntcust_file.upper().endswith(".XLSX")):
            raise ValueError("File {} has wrong extension. Only TXT or XLSX files supported".format(cwbntcust_file))

        tbl = Cwbntcust(path)
        notes = tbl.read_file()

        if not len(notes):
            print("[WARNING] System '{}' File {} has wrong format or doesn't contain completely implemented notes"
                  .format(system_name, cwbntcust_file,))

        return notes

