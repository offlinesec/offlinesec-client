import os.path
from datetime import datetime
import json
import zipfile

from offlinesec_client.func import get_file_name
from offlinesec_client.sap_table import SAPTable
from offlinesec_client.yaml_cfg_read import YamlCfgFile
from offlinesec_client.masking import Masking, ROLE_MASK, SAPSID_MASK

class RolesCfgFile:
    def __init__(self,
                 file_name,
                 ignore_na_roles=False,
                 ignore_ff_roles=False,
                 ):
        self.file_name = file_name
        self.err_list = list()
        self.err_flag = False
        self.ff_masks = list()
        self.ignore_na_roles = ignore_na_roles
        self.ignore_ff_roles = ignore_ff_roles

    def parse(self):
        if self.file_name:
            yaml_file = YamlCfgFile(file_name=self.file_name)

            if not yaml_file.check_class_item():
                print("\n".join(yaml_file.err_list))
                self.err_flag = True
                return

            if "ff_masks" in yaml_file.content:
                if isinstance(yaml_file.content["ff_masks"], list):
                    self.ff_masks = yaml_file.content["ff_masks"]
                else:
                    self.ff_masks.append(yaml_file.content["ff_masks"])

            outdict = dict()
            for system in yaml_file:
                name = system["name"]

                agr_users = dict()
                if "agr_users" in system:
                    agr_users = RolesCfgFile.read_agr_users(system["agr_users"])

                usr02 = dict()
                if "usr02" in system:
                    usr02 = RolesCfgFile.read_usr02(system["usr02"])

                agr_1251 = dict()
                if "agr_1251" in system:
                    agr_1251 = RolesCfgFile.read_agr_1251(system["agr_1251"])

                if name not in outdict:
                    # add ff flag
                    outdict[name] = RolesCfgFile.join_all_tables(
                                                agr_users=agr_users,
                                                usr02=usr02,
                                                agr_1251=agr_1251,
                                                ff_masks=self.ff_masks
                    )
                else:
                    print(" * [Warning] Duplicated name %s. Repeated definitions are ignored" % (name,))

            #Exclude not assigned roles, ff roles
            self.filter_roles(outdict)
            return outdict

    def filter_roles(self, outdict):
        for systemid in outdict:
            for clientid in outdict[systemid]:
                del_roles = list()

                for role_name in outdict[systemid][clientid]:
                    if self.ignore_ff_roles and len(self.ff_masks):
                        for mask in self.ff_masks:
                            if mask in role_name:
                                del_roles.append(role_name)
                                break
                    if self.ignore_na_roles:
                        auths, user_info, ff_role = outdict[systemid][clientid][role_name]

                        if isinstance(user_info, int):
                            if user_info == 0:
                                del_roles.append(role_name)
                        elif isinstance(user_info, tuple):
                            if user_info[0] == 0:
                                del_roles.append(role_name)

                del_roles = list(set(del_roles))
                for role_name in del_roles:
                    del outdict[systemid][clientid][role_name]

    @staticmethod
    def compare_time_stamp(today_date, from_dat, to_dat):
        cur_year = str(today_date.year)
        if from_dat[6:] < cur_year < to_dat[6:]:
            return True

        cur_month = str(today_date.month)
        cur_day = str(today_date.day)

        if from_dat[6:] > cur_year:
            return False
        if from_dat[6:] == cur_year:
            if from_dat[3:5] > cur_month:
                return False
            if from_dat[3:5] == cur_month:
                if from_dat[0:2] > cur_day:
                    return False

        if to_dat[6:] < cur_year:
            return False
        if to_dat[6:] == cur_year:
            if to_dat[3:5] < cur_month:
                return False
            if to_dat[3:5] == cur_month:
                if to_dat[0:2] < cur_day:
                    return False

        return True

    @staticmethod
    def join_tables(agr_users, usr02):
        temp_list = dict()
        for mandt in agr_users:
            if mandt not in temp_list:
                temp_list[mandt] = dict()

            if mandt in usr02:
                for role_name, users in agr_users[mandt].items():
                    assigned_to_users = 0
                    assigned_to_active_users = 0
                    assigned_to_active_dialog_users = 0
                    assigned_to_active_npa_users = 0
                    for user in users:
                        assigned_to_users += 1
                        if user in usr02[mandt]:
                            active, dialog = usr02[mandt][user]
                            if active:
                                assigned_to_active_users += 1
                                if dialog:
                                    assigned_to_active_dialog_users += 1
                                else:
                                    assigned_to_active_npa_users += 1
                    temp_list[mandt][role_name] = (assigned_to_users,
                                                   assigned_to_active_users,
                                                   assigned_to_active_dialog_users,
                                                   assigned_to_active_npa_users)
        return temp_list

    @staticmethod
    def read_agr_users(tables):
        if not isinstance(tables,list):
            new_item = tables
            tables = list()
            tables.append(new_item)

        temp_list = dict()
        for table in tables:
            if not os.path.isfile(table):
                print(" * [Warning] File %s not found" % (table,))
                continue

            tbl = SAPTable(table_name="AGR_USERS",
                           file_name=table)
            tbl_content = list(filter(lambda x: len(x["AGR_NAME"]) > 1 and x["AGR_NAME"][0].upper() in ("Z", "Y"), tbl))
            cur_date = datetime.now()
            tbl_content = list(filter(lambda x: RolesCfgFile.compare_time_stamp(cur_date, x["FROM_DAT"], x["TO_DAT"]), tbl_content))

            for item in tbl_content:
                mandt = item["MANDT"]
                if mandt not in temp_list:
                    temp_list[mandt] = dict()
                role_name = item["AGR_NAME"]
                if role_name not in temp_list[mandt]:
                    temp_list[mandt][role_name] = list()
                user = item["UNAME"]
                if user not in temp_list[mandt][role_name]:
                    temp_list[mandt][role_name].append(user)
        return temp_list

    @staticmethod
    def read_usr02(tables):
        if not isinstance(tables,list):
            new_item = tables
            tables = list()
            tables.append(new_item)

        temp_list = dict()
        for table in tables:
            if not os.path.isfile(table):
                print(" * [Warning] File %s not found" % (table,))
                continue
            tbl = SAPTable(table_name="USR02",
                           file_name=table)
            temp_list = dict()
            for item in tbl:
                mandt = item["MANDT"]
                if mandt not in temp_list:
                    temp_list[mandt] = dict()
                user_name = item["BNAME"]
                #valid from, valid to
                uflag = item["UFLAG"]
                active_user = True if (uflag.strip() == "0" or uflag.strip() == "") else False
                ustyp = item["USTYP"]
                dialog_user = True if (ustyp in ("A", "S")) else False
                if user_name not in temp_list[mandt]:
                    temp_list[mandt][user_name] = (active_user, dialog_user)
        return temp_list

    @staticmethod
    def check_auth(line):
        return line["DELETED"].strip() != "X" and line["OBJECT"].startswith("S_")

    @staticmethod
    def read_agr_1251(tables):
        if not isinstance(tables,list):
            new_item = tables
            tables = list()
            tables.append(new_item)

        temp_list = dict()
        for table in tables:
            if not os.path.isfile(table):
                print(" * [Warning] File %s not found" % (table,))
                continue

            tbl = SAPTable(table_name="AGR_1251",
                           file_name=table)

            tbl_content = list(filter(lambda x: RolesCfgFile.check_auth(x), tbl))
            for line in tbl_content:
                mandt = line["MANDT"]
                if mandt not in temp_list:
                    temp_list[mandt] = dict()
                role_name = line["AGR_NAME"]
                if role_name not in temp_list[mandt]:
                    temp_list[mandt][role_name] = list()
                item = (line["OBJECT"], line["AUTH"], line["FIELD"], line["LOW"], line["HIGH"])

                temp_list[mandt][role_name].append(item)
        return temp_list

    @staticmethod
    def get_user_info(clientid, role_name, agr_users, usr02):
        if agr_users and len(agr_users):
            if usr02 and len(usr02):
                if role_name in agr_users[clientid]:
                    user_list = agr_users[clientid][role_name]
                    if clientid in usr02:
                        assigned_to_users = 0
                        assigned_to_active_users = 0
                        assigned_to_active_dialog_users = 0
                        assigned_to_active_npa_users = 0
                        for user in usr02[clientid]:
                            if user in user_list:
                                active, dialog = usr02[clientid][user]
                                assigned_to_users += 1
                                if active:
                                    assigned_to_active_users += 1
                                    if dialog:
                                        assigned_to_active_dialog_users += 1
                                    else:
                                        assigned_to_active_npa_users += 1
                        return (
                            assigned_to_users,
                            assigned_to_active_users,
                            assigned_to_active_dialog_users,
                            assigned_to_active_npa_users)

                    else:
                        return 0
                else:
                    return 0
            else:
                if clientid in agr_users:
                    if role_name in agr_users[clientid]:
                        return len(agr_users[clientid][role_name])
                    else:
                        return 0
        else:
            return

    @staticmethod
    def join_all_tables(agr_users, usr02, agr_1251, ff_masks=list()):
        out_dict = dict()
        for clientid in agr_1251:
            if clientid not in out_dict:
                out_dict[clientid] = dict()
            for role_name in agr_1251[clientid]:
                auths = agr_1251[clientid][role_name]
                user_info = RolesCfgFile.get_user_info(
                        clientid=clientid,
                        role_name=role_name,
                        agr_users=agr_users,
                        usr02=usr02
                    )
                ff_flag = RolesCfgFile.ff_check(role_name, ff_masks)

                out_dict[clientid][role_name] = (
                        auths,
                        user_info,
                        ff_flag
                    )
        return out_dict


    @staticmethod
    def ff_check(role_name, ff_masks):
        if not len(ff_masks):
            return
        for ff_mask in ff_masks:
            if ff_mask in role_name:
                return True
        return False

    @staticmethod
    def masking(data):
        role_masking = Masking(masking_type=ROLE_MASK)
        sid_masking = Masking(masking_type=SAPSID_MASK)

        new_dict = dict()

        for systemid in data:
            new_system_id = sid_masking.do_mask(systemid)
            new_dict[new_system_id] = dict()
            for clientid in data[systemid]:
                new_dict[new_system_id][clientid] = dict()
                for role_name in data[systemid][clientid]:
                    new_role_name = role_masking.do_mask(role_name)
                    new_dict[new_system_id][clientid][new_role_name] = data[systemid][clientid][role_name]

        role_masking.save_masking()
        sid_masking.save_masking()
        return new_dict

    @staticmethod
    def save_and_zip(data):

        json_file_name = get_file_name("role_json_data.json")
        new_json = dict()
        new_json["systems"] = data

        try:
            with open(json_file_name, 'w') as f:
                json.dump(new_json, f)
        except Exception as err:
            print(" * [ERROR] " + str(err))
            return

        zipfilename = get_file_name("roles.zip")
        try:
            zipfile.ZipFile(zipfilename, mode='w', compression=zipfile.ZIP_DEFLATED, compresslevel=9).write(json_file_name)
        except Exception as err:
            print(" * [ERROR] " + str(err))
            return

        if os.path.isfile(json_file_name):
            os.remove(json_file_name)

        return zipfilename
