from offlinesec_client.yaml_cfg import YamlCfg, DEF_SYSTEM_NAME

CFG_STRUCTURE = {
    "root_dir" : {"required": False, "desc": "A folder name with all files", "value_type": "string"},
    "sap_systems": {"required": True, "desc": "SAP System list", "sub_keys": {
        "name": {"required": False, "desc": "SAP System name", "value_type": "string"},
        "icfservice": {"required": True, "desc": "The ICFSERVICE table"},
        "icfservloc": {"required": True, "desc": "The ICFSERVLOC table"},
    }}
}

class YamlICFCfg(YamlCfg):
    def __init__(self, file_name, yaml_structure=None):
        if yaml_structure is None:
            yaml_structure = CFG_STRUCTURE
        super().__init__(file_name=file_name, yaml_structure=yaml_structure)

    @staticmethod
    def resolve_service_name(serv_name, par_guid, icf_parents, icf_aliases, icf_names):
        cur_service_name = "?"

        if par_guid in icf_aliases and serv_name in icf_aliases[par_guid]:
            cur_service_name = icf_aliases[par_guid][serv_name]

        if par_guid == "0000000000000000000000000":
            return cur_service_name

        if par_guid in icf_parents:
            new_parent_guid = icf_parents[par_guid]
            new_serv_name = icf_names[par_guid]

            return YamlICFCfg.resolve_service_name(serv_name=new_serv_name,
                                        par_guid=new_parent_guid,
                                        icf_parents=icf_parents,
                                        icf_aliases=icf_aliases,
                                        icf_names=icf_names) + "/" + cur_service_name

        return "??" + "/" + cur_service_name

    @staticmethod
    def compress_list(service_list):
        out_list = dict()
        for service in service_list:
            split_service = service["name"].split("/")

            cur_item = out_list
            for item in split_service:
                if item not in cur_item:
                    cur_item[item] = dict()
                cur_item = cur_item[item]
        return out_list

    @staticmethod
    def get_user_list(services):
        out_list = list()
        for service in services:
            if "user" in service:
                out_list.append(service["name"])

        return out_list

    def get_data(self):
        out_data = list()
        user_list = list()
        for i, system_def in enumerate(self):
            sys_name = system_def["name"] if "name" in system_def else DEF_SYSTEM_NAME % (str(i), )
            if "icfservice" in system_def and "icfservloc" in system_def:
                icfservice = self.read_tables_from_file(file_name_list=system_def["icfservice"],
                                                        table_name="ICFSERVICE",
                                                        system_desc=sys_name)
                icfservloc = self.read_tables_from_file(file_name_list=system_def["icfservloc"],
                                                        table_name="ICFSERVLOC",
                                                        system_desc=sys_name)

                if icfservloc and icfservice:
                    active_serv_list = dict()
                    for table in icfservloc:
                        if len(table.err_list):
                            print(table.err_list)
                            continue
                        for line in table:
                            active_status = line["ICFACTIVE"].strip()
                            par_guid = line["ICFPARGUID"].strip()
                            name = line["ICF_NAME"].strip().lower()

                            if active_status == "X":
                                if par_guid not in active_serv_list:
                                    active_serv_list[par_guid] = list()
                                if name not in active_serv_list[par_guid]:
                                    active_serv_list[par_guid].append(name)

                    icf_parents = dict()
                    icf_aliases = dict()
                    icf_names = dict()
                    icf_users = dict()

                    for table in icfservice:
                        if len(table.err_list):
                            print(table.err_list)
                            continue
                        for line in table:
                            name = line["ICF_NAME"].strip().lower()
                            nod_guid = line["ICFNODGUID"].strip().upper()
                            par_guid = line["ICFPARGUID"].strip().upper()
                            user = line["ICF_USER"].strip().upper()
                            alias = line["ICFALTNME"].strip().lower()

                            icf_parents[nod_guid] = par_guid
                            icf_names[nod_guid] = name

                            if not par_guid in icf_aliases:
                                icf_aliases[par_guid] = dict()

                            if user is not None and user != "":
                                if not par_guid in icf_users:
                                    icf_users[par_guid] = dict()
                                icf_users[par_guid][name] = user

                            icf_aliases[par_guid][name] = alias if alias is not None and alias != "" else name

                    services = list()
                    for par_guid in active_serv_list:
                        for name in active_serv_list[par_guid]:
                            new_serv = dict()
                            new_serv["name"] = YamlICFCfg.resolve_service_name(serv_name=name,
                                                                    par_guid=par_guid,
                                                                    icf_parents=icf_parents,
                                                                    icf_aliases=icf_aliases,
                                                                    icf_names=icf_names)

                            if par_guid in icf_users:
                                if name in icf_users[par_guid]:
                                    new_serv["user"] = icf_users[par_guid][name]

                            services.append(new_serv)

                    new_list = YamlICFCfg.compress_list(services)
                    user_list = YamlICFCfg.get_user_list(services)
                    if new_list:
                        new_item = dict()
                        new_item["sid"] = sys_name
                        new_item["services"] = new_list
                        new_item["hardcoded_users_in_services"] = user_list
                        out_data.append(new_item)

        return out_data

def do_test():

    file_name2 = "..//tests//files/not_exists.yaml"
    test2 = YamlICFCfg(file_name=file_name2)
    assert len(test2.errors) == 1, "Test 2. Should be one error message. Current value: %s" % (len(test2.errors),)
    assert len(test2.warnings) == 0, "Test 2. Should be no warning messages. Current value: %s" % (len(test2.warnings),)

    file_name3 = "../../tests/files/only_systems.yaml"
    test3 = YamlICFCfg(file_name=file_name3)
    assert len(test3.errors) == 1, "Test 3. Should be one error message. Current value: %s" % (len(test3.errors),)
    assert len(test3.warnings) == 0, "Test 3. Should be no warning messages. Current value: %s" % (len(test3.warnings),)

    file_name4 = "../../tests/files/icf/icf_cfg_1.yaml"
    test4 = YamlICFCfg(file_name=file_name4)
    assert len(test4.errors) == 0, "Test 4. Should be one error message. Current value: %s" % (len(test4.errors),)
    assert len(test4.warnings) == 2, "Test 4. Should be no warning messages. Current value: %s" % (len(test4.warnings),)

    file_name5 = "../../tests/files/icf/icf_cfg_2.yaml"
    test5 = YamlICFCfg(file_name=file_name5)
    assert len(test5.errors) == 0, "Test 4. Should be one error message. Current value: %s" % (len(test5.errors),)
    assert len(test5.warnings) == 1, "Test 4. Should be no warning messages. Current value: %s" % (len(test5.warnings),)

    file_name6 = "../../tests/files/icf/icf_cfg_3.yaml"
    test6 = YamlICFCfg(file_name=file_name6)
    assert len(test6.errors) == 0, "Test 4. Should be one error message. Current value: %s" % (len(test6.errors),)
    assert len(test6.warnings) == 0, "Test 4. Should be no warning messages. Current value: %s" % (len(test6.warnings),)

    file_name7 = "../../tests/files/icf/icf_cfg_4.yaml"
    test7 = YamlICFCfg(file_name=file_name7)
    assert len(test7.errors) == 0, "Test 4. Should be one error message. Current value: %s" % (len(test7.errors),)
    assert len(test7.warnings) == 1, "Test 4. Should be no warning messages. Current value: %s" % (len(test7.warnings),)

def main():
    file_name = "../tests/files/icf/icf_cfg_3.yaml"
    test = YamlICFCfg(file_name=file_name)
    data = test.get_data()
    print(test.errors, test.warnings)
    print(data)

if __name__ == "__main__":
    #do_test()
    main()