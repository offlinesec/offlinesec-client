import os
import yaml

from offlinesec_client.rfcdes import *
from offlinesec_client.sap_table import SAPTable

SYS_TYPES = ["prd", "qa", "dev", "pre-prd", "sndbox"]

SYS_ROLES = {
    "prd" : ["prod", "prd", "production"],
    "qa": ["test", "QA", "qa"],
    "dev": ["dev", "development"],
    "pre-prd": ["pre-prd", "pre-production", "pre-prod"],
    "sndbox": ["sandbox", "sndbx"]
}

UNKNOWN = "unknown"

class YamlCfgRfc:
    def __init__(self, file_name):
        self.err_list = list()
        self.rfcdes_list = dict()
        self.ust04_list = dict()
        self.usr02_list = dict()
        self.sid_list = dict()

        if not os.path.isfile(file_name):
            self.err_list.append("* [ERROR] File %s not found" % (file_name,))
            return

        self.file_name = file_name

    def read_file(self):
        try:
            with open(self.file_name, 'r', encoding="utf-8") as f:
                file_content = yaml.safe_load(f)
        except Exception as err:
            self.err_list.append("* [ERROR] " + str(err))
        else:
            root_dir = file_content["root_dir"] if "root_dir" in file_content else ""
            if not "sap_systems" in file_content:
                self.err_list.append("* [ERROR] Wrong file format. The key 'sap_systems' not found")
                return

            for num, system in enumerate(file_content["sap_systems"]):
                if "name" not in system.keys():
                    self.err_list.append("* [WARNING] System (%s) without name in file %f" % (str(num), os.path.basename(self.file_name)))
                    continue
                name = system["name"]
                rfcdes = os.path.join(root_dir, system["rfcdes"]) if "rfcdes" in system.keys() else ""
                role = system["role"] if "role" in system.keys() else ""
                if role not in SYS_TYPES:
                    self.err_list.append("* [WARNING] Wrong system type %s (System %s). Allowed only: %s" % (role, name, ", ".join(SYS_TYPES)))

                if "usr02" in system.keys():
                    if isinstance(system["usr02"],list):
                        usr02 = list()
                        for item in system["usr02"]:
                            usr02.append(os.path.join(root_dir, item))
                    elif isinstance(system["usr02"], str):
                        usr02 = os.path.join(root_dir, system["usr02"])
                        # string or list

                if "ust04" in system.keys():
                    if isinstance(system["ust04"],list):
                        ust04 = list()
                        for item in system["ust04"]:
                            ust04.append(os.path.join(root_dir, item))
                    elif isinstance(system["ust04"], str):
                        ust04 = os.path.join(root_dir, system["ust04"])

                if rfcdes:
                    if name not in self.rfcdes_list.keys():
                        self.rfcdes_list[name] = rfcdes
                    else:
                        self.err_list.append("* [WARNING] System %s. Redefinition of RFCDES table" % (name, ))
                if ust04:
                    if name not in self.ust04_list.keys():
                        self.ust04_list[name] = ust04
                    else:
                        self.err_list.append("* [WARNING] System %s. Redefinition of UST04 table" % (name, ))

                if usr02:
                    if name not in self.usr02_list.keys():
                        self.usr02_list[name] = usr02
                    else:
                        self.err_list.append("* [WARNING] System %s. Redefinition of USR02 table" % (name, ))

                if name:
                    self.sid_list[name] = role

    def load_tables(self):
        rfc_conn_list = list()

        if not len(self.rfcdes_list):
            self.err_list.append("* [ERROR] RFCDES tables not found in the config file")

        for sid in self.rfcdes_list.keys():
            lines = self.read_rfcdes_table(self.rfcdes_list[sid], sid)
            rfc_conn_list.extend(lines)

        self.check_systems(rfc_conn_list)
        self.ust04_enrichment(rfc_conn_list)
        self.usr02_enrichment(rfc_conn_list)
        return rfc_conn_list

    def read_rfcdes_table(self, file_name, sid):
        lines = list()
        if not os.path.isfile(file_name):
            self.err_list.append("* [WARNING] File %s not exist" % (file_name,))
            return

        tbl = SAPTable(table_name="RFCDES",
                        file_name=file_name )

        for line in tbl:
            if RFCTYPE_COLUMN in line.keys():
                nl = rfcdes_parse_rfcdes_line(line, line[RFCTYPE_COLUMN])
                nl["SRCSID"] = sid
                if nl["RFCTYPE"] == "3":
                    if "I" not in nl.keys() or nl["I"] is None or nl["I"].strip() == "":
                        if "H" not in nl.keys() or nl["H"].strip() == "":
                            nl["I"] = sid
                        else:
                            temp_sid = get_sid_from_rfc_name(nl["RFCDEST"])
                            if temp_sid is not None:
                                nl["I"] = temp_sid

                if sid in self.sid_list:
                    nl["SRC_SYS_ROLE"] = self.sid_list[sid]

                lines.append(nl)
        return lines

    def ust04_enrichment(self, rfc_conn_list):
        ust04_buffer = dict()

        for conn in rfc_conn_list:
            if conn["RFCTYPE"] == "3" and "I" in conn.keys():
                system_in_conn = conn["I"]
                if "U" in conn.keys() and "M" in conn.keys() and conn["U"].strip() != "" and conn["M"].strip() != "":
                    if system_in_conn in self.ust04_list.keys():
                        if system_in_conn not in ust04_buffer:
                            ust04_buffer[system_in_conn] = self.read_ust04(self.ust04_list[system_in_conn])
                        if ust04_buffer[system_in_conn] is not None:
                            conn["PROFILES"] = YamlCfgRfc.get_profiles(user=conn["U"],
                                                                           client=conn["M"],
                                                                           ust04_table=ust04_buffer[system_in_conn])
                        else:
                            conn["PROFILES"] = UNKNOWN
                    else:
                        conn["PROFILES"] = UNKNOWN


    def usr02_enrichment(self, rfc_conn_list):
        usr02_buffer = dict()
        for conn in rfc_conn_list:
            if conn["RFCTYPE"] == "3" and "I" in conn.keys():
                system_in_conn = conn["I"]
                if "U" in conn.keys() and "M" in conn.keys() and conn["U"].strip() != "" and conn["M"].strip() != "":
                    if system_in_conn in self.usr02_list:
                        if system_in_conn not in usr02_buffer:
                            usr02_buffer[system_in_conn] = self.read_usr02(self.usr02_list[system_in_conn])
                        if usr02_buffer[system_in_conn] is not None:
                            conn.update(YamlCfgRfc.get_userinfo(user=conn["U"],
                                                                client=conn["M"],
                                                                usr02_table=usr02_buffer[system_in_conn]))
                        else:
                            conn["USTYP"] = UNKNOWN
                            conn["UFLAG"] = UNKNOWN
                            conn["CLASS"] = UNKNOWN
                    else:
                        conn["USTYP"] = UNKNOWN
                        conn["UFLAG"] = UNKNOWN
                        conn["CLASS"] = UNKNOWN


    def read_usr02(self, file_name):
        lines = list()

        if isinstance(file_name, list):
            tables = file_name
        else:
            tables = list()
            tables.append(file_name)

        for file in tables:
            if not os.path.isfile(file):
                self.err_list.append("* [WARNING] Table file %s not found" % (file, ))
                continue
            try:
                tbl = SAPTable(table_name="USR02",
                            file_name=file )
            except Exception as err:
                self.err_list.append("* [WARNING] Bad table file %s" % (file,))
                continue
            else:
                for line in tbl:
                    lines.append(line)
        return lines


    def read_ust04(self, file_name):
        lines = list()

        if isinstance(file_name, list):
            tables = file_name
        else:
            tables = list()
            tables.append(file_name)

        for file in tables:
            if not os.path.isfile(file):
                self.err_list.append("* [WARNING] Table file %s not found" % (file, ))
                continue
            try:
                tbl = SAPTable(table_name="UST04",
                            file_name=file )
            except Exception as err:
                self.err_list.append("* [WARNING] Bad table file %s" % (file,))
                continue
            else:
                for line in tbl:
                    lines.append(line)
        return lines

    @staticmethod
    def get_userinfo(user, client, usr02_table):
        userinfo = dict()
        mandt_flag = False
        for line in usr02_table:
            if "MANDT" in line.keys() and "BNAME" in line.keys():
                if line["MANDT"] == client and line["BNAME"] == user:
                    userinfo = dict()
                    if "USTYP" in line.keys() and line["USTYP"]:
                        userinfo["USTYP"] = line["USTYP"]
                    else:
                        userinfo["USTYP"] = UNKNOWN
                    if "UFLAG" in line.keys() and line["UFLAG"].strip() != "":
                        userinfo["UFLAG"] = line["UFLAG"]
                    else:
                        userinfo["UFLAG"] = UNKNOWN
                    if "CLASS" in line.keys():
                        userinfo["CLASS"] = line["CLASS"]
                    else:
                        userinfo["CLASS"] = UNKNOWN
                    break
                if line["MANDT"] == client:
                    mandt_flag = True
            else:
                userinfo["USTYP"] = UNKNOWN
                userinfo["UFLAG"] = UNKNOWN
                userinfo["CLASS"] = UNKNOWN

        if not len(userinfo) and not mandt_flag:
            userinfo["USTYP"] = UNKNOWN
            userinfo["UFLAG"] = UNKNOWN
            userinfo["CLASS"] = UNKNOWN
        return userinfo


    @staticmethod
    def get_profiles(user, client, ust04_table):
        profiles = list()
        mandt_flag = False
        for line in ust04_table:
            if "MANDT" in line.keys() and "BNAME" in line.keys() and "PROFILE" in line.keys():
                if line["MANDT"] == client and line["BNAME"] == user:
                    if line["PROFILE"].startswith("S"):
                        profiles.append(line["PROFILE"])
                if line["MANDT"] == client:
                    mandt_flag = True
            else:
                return "unknown"

        if not len(profiles) and not mandt_flag:
            return "unknown"

        return ", ".join(profiles)

    @staticmethod
    def get_system_list_with_users(rfc_conn_list):
        system_list = [conn["I"] for conn in rfc_conn_list if "U" in conn.keys() and "I" in conn.keys() and "M" in conn.keys() and not "UNKNOWN_DSTSID" in conn.keys()]
        return list(set(system_list))

    def check_systems(self, rfc_conn_list):
        for conn in rfc_conn_list:
            if conn[RFCTYPE_COLUMN] == "3":
                if "I" in conn.keys() and conn["I"] is not None:
                    if conn["I"] not in self.sid_list and conn["I"].strip() != "":
                        conn["UNKNOWN_DSTSID"] = True
                    elif conn["I"] in self.sid_list:
                        conn["DST_SYS_ROLE"] = self.sid_list[conn["I"]]
                    else:
                        conn["DST_SYS_ROLE"] = conn["SRC_SYS_ROLE"]
                else:
                    conn["DST_SYS_ROLE"] = conn["SRC_SYS_ROLE"]