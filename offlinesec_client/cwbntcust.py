import openpyxl


class Cwbntcust:
    def __init__(self, filename):
        self.filename = filename
        self.data = list()

    def read_file(self):
        if self.filename.split(".")[-1].lower() == "xlsx":
            return self.read_xlsx_file()
        elif self.filename.split(".")[-1].lower() == "txt":
            return self.read_txt_file()

    def read_xlsx_file(self):
        self.data = list()
        outlist = list()
        wb_obj = openpyxl.load_workbook(self.filename)
        sheet_obj = wb_obj.active
        max_col = sheet_obj.max_column

        max_row = sheet_obj.max_row
        for i in range(2, max_row + 1):
            note = str(sheet_obj.cell(row=i, column=1).value)
            #ntstatus = sheet_obj.cell(row=i, column=2).value
            prstatus = str(sheet_obj.cell(row=i, column=3).value)
            if prstatus == "E":             # Completely implemented
                outlist.append(note)
        return outlist

    def read_txt_file(self):
        outlist = list()
        f = open(self.filename, "r")

        header_flag = True
        for line in f:
            if line.startswith("|"):
                if header_flag:
                    header_flag = False
                else:
                    splited_line = line.split("|")
                    note = splited_line[2].strip()
                    prstatus = splited_line[4].strip()
                    if prstatus == "E":  # Completely implemented
                        outlist.append(note)

        f.close()
        return outlist
