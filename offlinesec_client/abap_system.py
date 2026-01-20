from offlinesec_client.sap_system import SAPSystem
from offlinesec_client.sap_table import SAPTable
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

        self.kernel_version = SAPSystem.check_kernel_version(args["krnl_version"]) \
            if ("krnl_version" in args.keys() and args["krnl_version"] is not None and args["krnl_version"] != "") else ""

        self.kernel_patch = SAPSystem.check_kernel_patch(args["krnl_patch"]) \
            if "krnl_patch" in args.keys() and args["krnl_patch"] is not None and args["krnl_patch"] != ""else ""

        self.softs = ABAPSystem.parse_softs_file(args["softs"], root_dir) \
            if "softs" in args.keys() else list()

        if self.kernel_version == "" and len(self.softs) == 0:
            raise ValueError("[ERROR] System '{}' you must specify 'softs' or 'krnl_version' keys"
                             .format(self.system_name))
        if "cwbntcust" in args.keys() and args["cwbntcust"] is not None:
            self.parse_cwbntcust_file(args["cwbntcust"], root_dir, self.system_name)
        else:
            self.cwbntcust = list()
            self.cwbntcust_new = dict()

        if "cwbntcust_dev" in args.keys() and args["cwbntcust_dev"] is not None:
            self.parse_dev_cwbntcust(args["cwbntcust_dev"], root_dir)
        else:
            self.cwbntcust_dev = dict()

        if "sla" in args:
            self.parse_sla(args["sla"], root_dir)

        # versions
        if "cwbnthead" in args.keys() and args["cwbnthead"] is not None:
            self.parse_cwbnthead(args["cwbnthead"], root_dir)
        else:
            self.cwbnthead = dict()

        self.exclude = ABAPSystem.parse_exclude_file(args["exclude"], root_dir, self.system_name) \
            if "exclude" in args.keys() and args["exclude"] is not None and args["exclude"] != ""else list()

        self.host_agent_version = ABAPSystem.check_kernel_version(args["host_agent_version"]) \
            if ("host_agent_version" in args.keys() and args["host_agent_version"] is not None and args["host_agent_version"] != "") else ""

        self.host_agent_patch = ABAPSystem.check_kernel_patch(args["host_agent_patch"]) \
            if "host_agent_patch" in args.keys() and args["host_agent_patch"] is not None and args["host_agent_patch"] != ""else ""

        self.sapui5 = args["sapui5"] if "sapui5" in args.keys() and args["sapui5"] is not None and \
            args["sapui5"] != "" and ABAPSystem.check_sapui5_ver(args["sapui5"]) else ""

        self.hana = args["hana"] if "hana" in args.keys() and args["hana"] is not None and \
            args["hana"] != "" and ABAPSystem.check_hana_ver(args["hana"]) else ""

    @staticmethod
    def check_soft_line(soft, version, pkg_num, package):
        res2 = re.match(r"^[\d_]+$", pkg_num)
        if not res2:
            return False

        return True

    @staticmethod
    def parse_softs_file(softs_file, root_dir):
        # SAP_BASIS	750	0006	SAPK-75006INSAPBASIS	SAP Basis Component

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
                    if ABAPSystem.check_soft_line(soft, version, pkg_num, package):
                        softs.append((soft, version, pkg_num, package))

        if not len(softs):
            raise ValueError("File {} has wrong format".format(softs_file))

        return softs

    def parse_cwbntcust_file(self, cwbntcust_file, root_dir, system_name):
        if root_dir:
            path = os.path.join(root_dir, cwbntcust_file)
        else:
            path = cwbntcust_file
        if not os.path.exists(path):
            raise FileNotFoundError("File %s not found" % (cwbntcust_file,))

        if not (cwbntcust_file.upper().endswith(".TXT") or cwbntcust_file.upper().endswith(".XLSX")):
            raise ValueError("File {} has wrong extension. Only TXT or XLSX files supported".format(cwbntcust_file))


        tbl = SAPTable(table_name="CWBNTCUST", file_name=path)
        self.cwbntcust = ABAPSystem.parse_cwbntcust_data(tbl)
        self.cwbntcust_new = ABAPSystem.parse_cwbntcust_data_new(tbl)

        if self.cwbntcust is None or not len(self.cwbntcust):
            print("* [WARNING] File {} has wrong format or doesn't contain completely implemented notes"
                  .format(cwbntcust_file,))

    def parse_dev_cwbntcust(self, cwbntcust_file, root_dir):
        if root_dir:
            path = os.path.join(root_dir, cwbntcust_file)
        else:
            path = cwbntcust_file
        if not os.path.exists(path):
            raise FileNotFoundError("File %s not found" % (cwbntcust_file,))

        if not (cwbntcust_file.upper().endswith(".TXT") or cwbntcust_file.upper().endswith(".XLSX")):
            raise ValueError("File {} has wrong extension. Only TXT or XLSX files supported".format(cwbntcust_file))


        tbl = SAPTable(table_name="CWBNTCUST", file_name=path)
        self.dev_cwbntcust = ABAPSystem.parse_cwbntcust_data_new(tbl)


    def parse_cwbnthead(self, cwbnthead_file, root_dir):
        if root_dir:
            path = os.path.join(root_dir, cwbnthead_file)
        else:
            path = cwbnthead_file
        if not os.path.exists(path):
            raise FileNotFoundError("File %s not found" % (cwbnthead_file,))

        if not (cwbnthead_file.upper().endswith(".TXT") or cwbnthead_file.upper().endswith(".XLSX")):
            raise ValueError("File {} has wrong extension. Only TXT or XLSX files supported".format(cwbnthead_file))

        tbl = SAPTable(table_name="CWBNTHEAD", file_name=path)

        outdict = dict()
        for line in tbl:
            if "NUMM" in line and "VERSNO" in line:
                if ("INCOMPLETE" in line and line["INCOMPLETE"] != "X") or "INCOMPLETE" not in line:
                    try:
                        note_id = line["NUMM"].lstrip("0")
                        vers = int(line["VERSNO"])
                    except:
                        continue
                    else:
                        if note_id not in outdict:
                            outdict[note_id] = vers
                        elif note_id in outdict and outdict[note_id] < vers:
                            outdict[note_id] = vers
        self.cwbnthead = outdict

    @staticmethod
    def check_sapui5_ver(sapui5_ver):
        reg_exp = "^\\d+.\\d+.\\d+$"
        if re.match(reg_exp, sapui5_ver):
            return True
        raise ValueError("SAPUI5 version must be in the following format: 1.84.56")

    @staticmethod
    def check_hana_ver(hana_ver):
        reg_exp = "^\\d+.\\d+.\\d+.\\d+.\\d+"
        if re.match(reg_exp, hana_ver):
            return True
        raise ValueError("HANA version must be in the following format: 2.00.033.00.1535710")

    @staticmethod
    def parse_cwbntcust_data(cwbntcust_table):
        notes = list()
        PRSTATUS_COLUMN = "PRSTATUS"
        NOTE_COLUMN = "NUMM"
        if not cwbntcust_table:
            raise ValueError("Bad CWBNTCUST table")

        if PRSTATUS_COLUMN in cwbntcust_table.columns and NOTE_COLUMN in cwbntcust_table.columns:
            idx_prstatus = cwbntcust_table.columns.index(PRSTATUS_COLUMN)
            idx_note = cwbntcust_table.columns.index(NOTE_COLUMN)
            for line in cwbntcust_table.data:
                prstatus = line[idx_prstatus]
                if prstatus == "E" or prstatus == "O":
                    notes.append(line[idx_note])

        return notes

    @staticmethod
    def parse_cwbntcust_data_new(cwbntcust_table):
        notes = dict()
        PRSTATUS_COLUMN = "PRSTATUS"
        NTSTATUS_COLUMN = "NTSTATUS"
        NOTE_COLUMN = "NUMM"
        if not cwbntcust_table:
            raise ValueError("Bad CWBNTCUST table")

        if (PRSTATUS_COLUMN in cwbntcust_table.columns and
                NOTE_COLUMN in cwbntcust_table.columns and
                NTSTATUS_COLUMN in cwbntcust_table.columns):
            idx_prstatus = cwbntcust_table.columns.index(PRSTATUS_COLUMN)
            idx_note = cwbntcust_table.columns.index(NOTE_COLUMN)
            idx_ntstatus = cwbntcust_table.columns.index(NTSTATUS_COLUMN)
            for line in cwbntcust_table.data:
                notes[line[idx_note]] =  [line[idx_ntstatus], line[idx_prstatus]]

        return notes

