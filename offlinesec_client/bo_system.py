from offlinesec_client.sap_system import SimpleSystem


BO = "BO"


class BOSystem (SimpleSystem):
    def __init__(self, **args):
        root_dir = args["root_dir"] if "root_dir" in args else None
        if "version" in args.keys():
            super().__init__(args["name"], version=BOSystem.check_version(args["version"], args["name"]))
        else:
            raise ValueError("You must specify 'version' key")
        self.type = BO
        self.exclude = BOSystem.parse_exclude_file(args["exclude"], root_dir, self.system_name) \
            if "exclude" in args.keys() else list()

    @staticmethod
    def check_version(v, system_name):
        splitted_ver = str(v).strip('"').split(".")
        if not len(splitted_ver) == 4:
            raise ValueError("Bad SAP BO version format '{}'. Expected format: 14.1.4.1655".format(str(v)))

        if not int(splitted_ver[0]) == 14:
            raise ValueError("Bad SAP BO version format '{}'. Expected format: 14.1.4.1655".format(str(v)))
        try:
            for item in splitted_ver:
                s = int(item)
        except:
            raise ValueError(" Bad SAP BO version format '{}'. Expected format: 14.1.4.1655".format(str(v)))
        return v
