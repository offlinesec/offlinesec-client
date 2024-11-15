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

SID_SIGNATURES = [
    r"([\S]{3})CLNT[\d]{3}",
    r"(^[\S]{3})[\d]{3}$",
    "_([\S]{3})_TRUSTED_BACK",
    r"\@([\S]{3})\.",
    r"TRUSTED\@([\S]{3})",
    r"TRUSTING\@([\S]{3})",
    r"_([\S]{3})_[\d]{2}$",
    r"^([\S]{3})$",
  #  r"^([\S]{3})[_-]",

]

# "BACK"
# local
# test in production

def get_sid_from_rfc_name(rfc_name):
    if rfc_name is None or rfc_name.strip() == "":
        return
    for sign in SID_SIGNATURES:
        res = re.search(sign, rfc_name)
        if res:
            return res.group(1)



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
