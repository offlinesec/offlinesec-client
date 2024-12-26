# -*- coding: utf-8 -*-

import os.path
import openpyxl

COLUMN_REPLACEMENT = {
    "RFCDES" : {
        "RFCDEST": ["RFC Destination", "Destination"],
        "RFCTYPE": ["Connection Type"],
        "RFCOPTIONS": ["Options"],
        "RFCDOC1": ["Description"]
    },

    "UST04" : {
        "MANDT": ["Client", "Mandant"],
        "BNAME": ["User", "Benutzername"],
        "PROFIL": ["Profile", "Profil"],
    },

    "USR02" : {
        "MANDT": ["Client", "Mandant"],
        "BNAME": ["User Name", "Benutzername"],
        "USTYP": ["User Type", "Benutzertyp"],
        "UFLAG": ["User Lock Status", "Status der Benutzersperre"],
        "CLASS": ["User Master Maintenance: User Group", "Benutzerstammpflege: Benutzergruppe"],
    },

    "CWBNTCUST" : {
        "NUMM" : ["Note number", "Hinweisnummer"],
        "NTSTATUS" : ["Processing Status", "Proc. Status", "Bearb. Stat."],
        "PRSTATUS" : ["Implementation State", "Impl. State", "Einbaustand", "Impl. Status"],
        "CWBUSER" : ["User Name", "Benutzername"],
        "REQID" : ["Request ID", "Request-Id"],
        "IMPL_PROGRESS": ["Implementation Progress", "Impl."]
    },

    "JAVA_SOFTS" : {
        "Version": [],
        "Vendor": [],
        "Name": [],
        "Location": []
    },

    "RSPARAM": {
        "Parameter Name": [],
        "User-Defined Value": [],
        "System Default Value": [],
        "System Default Value(Unsubstituted Form)": [],
        "Comment": []
    }
}

DATA_REPLACEMENT = {
    "CWBNTCUST" : {
        "NTSTATUS" : {
            "A" : ["Finished","erledigt"],
            "N" : ["new", "neu"],
            "R" : ["Not Relevant", "nicht relevant"],
            "I" : ["In Process", "in Bearbeitung"]
        },
        "PRSTATUS" : {
            "N" : ["Can be implemented"],
            "E" : ["Completely implemented"],
            "O" : ["Obsolete"],
            "-" : ["Cannot be implemented"],
            ""  : ["Undefined Implementation State"],
            "U" : ["Incompletely implemented "],
            "V" : ["Obsolete version implemented"],
        },
    }
}


class SAP_Table_SE16:
    def __init__(self, table_name, file_name):
        self.table_name = table_name
        self.file_name = file_name

        self.columns = list()
        self.data = list()

        self.read_table()

        if table_name:
            if table_name in COLUMN_REPLACEMENT.keys():
                self.replace_columns(COLUMN_REPLACEMENT[table_name])

    def replace_columns(self, replacement):
        for column in replacement:
            for item in replacement[column]:
                if item in self.columns:
                    idx = self.columns.index(item)
                    self.columns[idx] = column
                    continue

    def replace_data_values(self, new_line):
        if self.table_name in DATA_REPLACEMENT:
            for column in DATA_REPLACEMENT[self.table_name]:
                column_idx = self.columns.index(column)
                value = new_line[column_idx]
                for new_value in DATA_REPLACEMENT[self.table_name][column]:
                    if value in DATA_REPLACEMENT[self.table_name][column][new_value]:
                        new_line[column_idx] = new_value
                        break

        return new_line

    def read_table(self):
        if not self.file_name:
            raise ValueError("File name is empty")

        if not os.path.isfile(self.file_name):
            raise ValueError("File %s not exist" % (self.file_name,))

        if not self.file_name.lower().endswith(".txt"):
            raise ValueError("Bad file extension %s" % (self.file_name,))

        f = open(self.file_name, "r", errors="ignore")
        header_flag = True
        column_num = 0
        column_lens = list()

        for line in f:
            if line.startswith("|"):
                if header_flag:
                    header_flag = False
                    self.columns = [item.strip() for item in line.split("|")]
                    column_lens = [len(item) for item in line.split("|")]
                    if not len(self.columns):
                        raise ValueError("Wrong file structure. Columns not found in the file")
                    column_num = len(self.columns)
                else:
                    row = [item.strip() for item in line.split("|")]
                    if len(row) != column_num:
                        row = list()
                        pos = 0
                        for i in range(0, len(self.columns)):
                            column_len = column_lens[i]
                            row.append(line[pos:pos+column_len].strip())
                            pos += column_len + 1

                        if len(row) != column_num:
                            raise ValueError("Wrong file structure. Bad line: %s in the file" % (line,))

                    self.data.append(row)

        f.close()

        if not len(self.columns):
            raise ValueError("Wrong file structure. Columns not found in the file")

    def __iter__(self):
        for row in self.data:
            out_row = dict()
            for num, column in enumerate(self.columns):
                out_row[column] = row[num]
            yield out_row


class HANA_SAP_Table(SAP_Table_SE16):
    def read_table(self):
        if not self.file_name:
            raise ValueError("File name is empty")

        if not os.path.isfile(self.file_name):
            raise ValueError("File %s not exist" % (self.file_name,))

        if not self.file_name.lower().endswith(".txt"):
            raise ValueError("Bad file extension %s" % (self.file_name,))

        f = open(self.file_name, "r", errors="ignore")
        header_flag = True
        column_num = 0

        for line in f:
            if True:
                if header_flag:
                    header_flag = False
                    self.columns = [item.strip() for item in line.split(";")]
                    if len(self.columns) < 2:
                        raise ValueError("Wrong file structure. Columns not found in the file")
                    column_num = len(self.columns)
                else:
                    row = [item.strip() for item in line.split(";")]
                    if len(row) != column_num:
                        raise ValueError("Wrong file structure. Bad line: %s in the file" % (line,))
                    self.data.append(row)

        f.close()


class XLSX_SE16_Table(SAP_Table_SE16):
    def read_table(self):
        if self.file_name is None or self.file_name == "":
            raise ValueError("File name is empty")

        if not os.path.isfile(self.file_name):
            raise ValueError("File %s not exist" % (self.file_name,))

        if not self.file_name.lower().endswith(".xlsx"):
            raise ValueError("Bad file extension %s" % (self.file_name,))

        wb_obj = openpyxl.load_workbook(self.file_name)
        sheet_obj = wb_obj.active
        max_col = sheet_obj.max_column
        max_row = sheet_obj.max_row
        column_num = 0

        for i in range(1, max_row + 1):
            if i == 1:
                for k in range(1, max_col + 1):
                    self.columns.append(sheet_obj.cell(row=i, column=k).value)
                if not len(self.columns):
                    raise ValueError("Wrong file structure. Columns not found")
                else:
                    column_num = len(self.columns)
                    if self.table_name in COLUMN_REPLACEMENT.keys():
                        self.replace_columns(COLUMN_REPLACEMENT[self.table_name])
            else:
                new_line = list()
                for k in range(1, max_col + 1):
                    new_line.append(sheet_obj.cell(row=i, column=k).value)
                if len(new_line) != column_num:
                    raise ValueError("Wrong file structure. Bad line: %s in the file" % (", ".join(new_line,)))

                self.data.append(self.replace_data_values(new_line))

        wb_obj.close()


class SAPTable:
    def __init__(self, table_name, file_name):
        classmap = {
            "SAP_Table_SE16": SAP_Table_SE16,
            "HANA_SAP_Table": HANA_SAP_Table,
            "XLSX_SE16_Table": XLSX_SE16_Table,
        }
        self.table_name = table_name

        created_object = None
        err_list = list()
        for class_name in classmap:
            try:
                created_object = classmap[class_name](table_name, file_name)
                self.class_name = class_name
            except ValueError as err:
                err_list.append(class_name + ": " + str(err))
            else:
                break

        if created_object:
            self.tbl = created_object
            self.columns = self.tbl.columns
            self.data = self.tbl.data
        else:
            print(err_list)
            raise ValueError("* [WARNING] Unsupported file format: %s. Supported files: HANA STUDIO, SE16-Unconverted, SE16-Spreadsheet" %
                             (file_name,))

    def __iter__(self):
        for row in self.tbl.data:
            out_row = dict()
            for num, column in enumerate(self.tbl.columns):
                out_row[column] = row[num]
            yield out_row
