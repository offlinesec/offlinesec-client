from offlinesec_client.cmd_user_input import OfflineSecRequest
from offlinesec_client.icf.yaml_cfg_icf import YamlICFCfg
from offlinesec_client.masking import Masking, SAPSID_MASK

REQUEST_ICF_TYPE = "icf"

class RequestICF(OfflineSecRequest):
    def __init__(self, upload_url=None):
        super().__init__(request_type=REQUEST_ICF_TYPE, upload_url=upload_url)

    def get_data(self):
        if "file" in self.inargs.keys() and self.inargs["file"]:
            config_file = self.inargs["file"]
            cfg = YamlICFCfg(file_name=config_file)
            data = cfg.get_data()
            if data:
                if not OfflineSecRequest.is_error_in_yaml(cfg):
                    return data

    def do_masking(self, data):
        sapsid_masking = Masking(SAPSID_MASK)
        for sys_definition in data:
            if "sid" in sys_definition:
                sys_definition["sid"] = sapsid_masking.do_mask(sys_definition["sid"])
        sapsid_masking.save_masking()

def main():
    req = RequestICF()
    req.process()

if __name__ == "__main__":
    main()
