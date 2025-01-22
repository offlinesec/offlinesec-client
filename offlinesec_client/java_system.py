from offlinesec_client.sap_system import SAPSystem
from offlinesec_client.sap_table import SAPTable
import os

JAVA = "JAVA"
CSV_COLUMNS = ["Version", "Name"]


class JAVASystem (SAPSystem):
    def __init__(self, **args):
        super().__init__(args["name"])
        self.type = JAVA
        root_dir = args["root_dir"] if "root_dir" in args else None
        self.softs = JAVASystem.parse_softs_file(args["softs"], root_dir) if "softs" in args.keys() else list()
        self.kernel_version = SAPSystem.check_kernel_version(args["krnl_version"]) \
            if ("krnl_version" in args.keys() and args["krnl_version"] is not None and args["krnl_version"] != "") else ""

        self.kernel_patch = SAPSystem.check_kernel_patch(args["krnl_patch"]) \
            if "krnl_patch" in args.keys() and args["krnl_patch"] is not None and args["krnl_patch"] != ""else ""
        if len(self.softs) == 0:
            raise ValueError("[ERROR] System '{}' you must specify 'soft' key"
                             .format(self.system_name))
        self.exclude = JAVASystem.parse_exclude_file(args["exclude"], root_dir, self.system_name) \
            if "exclude" in args.keys() else list()

    @staticmethod
    def parse_softs_file(softs_file, root_dir):
        if root_dir:
            path = os.path.join(root_dir, softs_file)
        else:
            path = softs_file
        if not os.path.exists(path):
            raise FileNotFoundError("File %s not found" % (path,))

        if softs_file.upper().endswith(".TXT") or softs_file.upper().endswith(".CSV"):
            out_softs = JAVASystem.parse_csv_file(path)
        elif softs_file.upper().endswith(".XLSX"):
            out_softs = JAVASystem.parse_xlsx_file(path)
        else:
            raise ValueError("File {} has wrong extension. Only TXT,CSV and XLSX files supported".format(softs_file))

        if not len(out_softs):
            raise ValueError("File {} has wrong format".format(softs_file))
        return out_softs

    @staticmethod
    def parse_xlsx_file(file_name):
        out_softs = list()
        tbl = SAPTable(table_name="JAVA_SOFTS", file_name=file_name)
        if tbl:
            idx_name = tbl.columns.index("Name")
            idx_ver = tbl.columns.index("Version")
            if idx_name is not None and idx_ver is not None:
                for line in tbl.data:
                    name = line[idx_name]
                    ver = line[idx_ver]
                    out_softs.append((name, ver))
        return out_softs

    @staticmethod
    def parse_csv_file(path):
        out_softs = list()
        with open(path, 'r') as f:
            columns = dict()
            first_line = True
            for line in f:
                line = line.strip('\r\n')
                if len(line) == 0:
                    continue
                line = line.replace(';', ',')
                line = line.split(',')
                if first_line:
                    first_line = False

                    for column1 in CSV_COLUMNS:
                        for pos, column2 in enumerate(line):
                            if column1.lower() in column2.lower().strip():
                                columns[column1] = pos
                        if column1 not in columns:
                            raise ValueError("The column '{}' not found in the file {}".format(column1, path))
                else:
                    name = line[columns[CSV_COLUMNS[1]]]
                    ver = line[columns[CSV_COLUMNS[0]]]
                    out_softs.append((name, ver))
        return out_softs
