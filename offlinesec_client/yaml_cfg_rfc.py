import os
import yaml

from offlinesec_client.rfcdes import *
from offlinesec_client.sap_table import SAPTable

SYS_TYPES = ["prd", "qa", "dev", "pre-prd", "sndbox"]


class YamlCfgRfc:
    def __init__(self, file_name):
        self.err_list = list()
        self.rfcdes_list = dict()
        self.ust04_list = dict()
        self.usr02_list = dict()
        self.sid_list = dict()

        if not os.path.isfile(file_name):
            self.err_list.append("* [ERROR] File %s not found" % (file_name))
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
                ust04 = os.path.join(root_dir, system["ust04"]) if "ust04" in system.keys() else ""
                usr02 = os.path.join(root_dir, system["usr02"]) if "usr02" in system.keys() else ""

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
        system_list_with_users  = self.get_user_list(rfc_conn_list)
        self.ust04_enrichment(rfc_conn_list, system_list_with_users)
        self.usr02_enrichment(rfc_conn_list, system_list_with_users)
        return rfc_conn_list

    def read_rfcdes_table(self, file_name, sid):
        lines = list()
        if not os.path.isfile(file_name):
            self.err_list.append("* [WARNING] File %s not exist" % (file_name))
            return

        tbl = SAPTable(table_name="RFCDES",
                        file_name=file_name )

        for line in tbl:
            if RFCTYPE_COLUMN in line.keys():
                nl = rfcdes_parse_rfcdes_line(line, line[RFCTYPE_COLUMN])
                nl["SRCSID"] = sid
                lines.append(nl)
        return lines

    def ust04_enrichment(self, rfc_conn_list, systems):
        ust04_buffer = dict()

        for system in systems:
            for conn in rfc_conn_list:
                if "I" in conn.keys() and "M" in conn.keys() and "U" in conn.keys():
                    sys_in_conn = conn["I"]
                    if sys_in_conn == system:
                        if system in self.ust04_list.keys():
                            if system not in ust04_buffer:
                                ust04_buffer[system] = self.read_ust04(self.ust04_list[system])
                            if ust04_buffer[system] is not None:
                                conn["PROFILES"] = YamlCfgRfc.get_profiles(user=conn["U"],
                                                                        client=conn["M"],
                                                                        ust04_table=ust04_buffer[system])
                            else:
                                conn["PROFILES"] = "unknown"
                        else:
                            conn["PROFILES"] = "unknown"

    def usr02_enrichment(self, rfc_conn_list, systems):
        usr02_buffer = dict()
        for system in systems:
            for conn in rfc_conn_list:
                if "I" in conn.keys() and "M" in conn.keys() and "U" in conn.keys():

                    sys_in_conn = conn["I"]
                    if sys_in_conn == system:

                        if system in self.usr02_list.keys():

                            if system not in usr02_buffer:
                                usr02_buffer[system] = self.read_usr02(self.usr02_list[system])
                            if usr02_buffer[system] is not None:
                                conn.update(YamlCfgRfc.get_userinfo(user=conn["U"],
                                                                client=conn["M"],
                                                                usr02_table=usr02_buffer[system]))


    def read_usr02(self, file_name):
        lines = list()
        if not os.path.isfile(file_name):
            self.err_list.append("* [WARNING] Table %s not found" % (file_name, ))
            return None

        tbl = SAPTable(table_name="USR02",
                        file_name=file_name )

        for line in tbl:
            lines.append(line)
        return lines



    def read_ust04(self, file_name):
        lines = list()
        if not os.path.isfile(file_name):
            self.err_list.append("* [WARNING] Table %s not found" % (file_name, ))
            return None

        tbl = SAPTable(table_name="UST04",
                        file_name=file_name)

        for line in tbl:
            lines.append(line)
        return lines

    @staticmethod
    def get_userinfo(user, client, usr02_table):
        userinfo = dict()
        for line in usr02_table:
            if "MANDT" in line.keys() and "BNAME" in line.keys():
                if line["MANDT"] == client and line["BNAME"] == user:
                    userinfo = dict()
                    if "USTYP" in line.keys() and line["USTYP"]:
                        userinfo["USTYP"] = line["USTYP"]
                    else:
                        userinfo["USTYP"] = "unknown"
                    if "UFLAG" in line.keys() and line["UFLAG"]:
                        userinfo["UFLAG"] = line["UFLAG"]
                    else:
                        userinfo["UFLAG"] = "unknown"
                    if "CLASS" in line.keys() and line["CLASS"]:
                        userinfo["CLASS"] = line["CLASS"]
                    else:
                        userinfo["CLASS"] = "unknown"

                    break
        return userinfo


    @staticmethod
    def get_profiles(user, client, ust04_table):
        profiles = list()
        for line in ust04_table:
            if "MANDT" in line.keys() and "BNAME" in line.keys() and "PROFILE" in line.keys():
                if line["MANDT"] == client and line["BNAME"] == user:
                    if line["PROFILE"].startswith("S"):
                        profiles.append(line["PROFILE"])
        return ", ".join(profiles)


    def get_user_list(self, rfc_conn_list):
        user_list = list()
        for conn in rfc_conn_list:
            if conn[RFCTYPE_COLUMN] == "3":
                if "U" in conn.keys():
                    if "I" in conn.keys():
                        if "M" in conn.keys():
                            if not "UNKNOWN_DSTSID" in conn.keys():
                                nu = conn["I"]
                                if not nu in user_list:
                                    user_list.append(nu)
        return user_list

    def check_systems(self, rfc_conn_list):
        for conn in rfc_conn_list:
            if conn[RFCTYPE_COLUMN] == "3":
                if "I" in conn.keys():
                    if conn["I"] not in self.sid_list:
                        conn["UNKNOWN_DSTSID"] = True