import openpyxl


class Cwbntcust:
    def __init__(self, filename):
        self.filename = filename
        self.data = list()

    def read_file(self):
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
