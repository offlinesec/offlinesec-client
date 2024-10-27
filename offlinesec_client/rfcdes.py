import re

RFCOPTIONS_KEY_ABAP = {
    "H": "H=",
    "U": "U=",
    "I": "I=",
    "N": "N=",
    "M": "M=",
    "G": "G=",
    "D": "D=",
}

RFCOPTIONS_COLUMN = "RFCOPTIONS"
RFCTYPE_COLUMN = "RFCTYPE"
RFCDEST_COLUMN = "RFCDEST"

COLUMNS = [RFCDEST_COLUMN, RFCTYPE_COLUMN]

def rfcdes_parse_rfcdes_line(line, rfctype):
    out_line = dict()
    for column in COLUMNS:
        if column in line.keys():
            out_line[column] = line[column]

    if RFCOPTIONS_COLUMN in line.keys():
        extension = rfcdes_parse_rfcoptions(line[RFCOPTIONS_COLUMN], rfctype)
        out_line.update(extension)

    return out_line

def rfcdes_parse_rfcoptions(line, rfctype):
    out_line = dict()

    if rfctype == "3":
        keys = RFCOPTIONS_KEY_ABAP
    else:
        keys = RFCOPTIONS_KEY_ABAP

    if keys:
        for signature in keys:
            regexp = keys[signature] + "([^,]+),"
            res = re.search(regexp, line)
            if res:
                out_line[signature] = res.group(1)
                line = re.sub(regexp, "", line)

    out_line[RFCOPTIONS_COLUMN] = line

    return out_line
