from pysapgui.sapexistedsession import SAPExistedSession
from pysapgui.software_components import SAPSoftwareComponents
from pysapgui.transaction_se16 import TCodeSE16
from offlinesec_client.const import SUBDIR, TEMPDIR
from offlinesec_client.func import get_file_name
import datetime
import os
from pathlib import Path


class SAPConnection:
    @staticmethod
    def sap_notes_report(system_name=None, wait=False, exclude=None):
        try:
            sap_sessions = SAPExistedSession.get_multi_sap_session_with_info()
        except RuntimeError as error:
            print(str(error))
        else:
            if not len(sap_sessions):
                print(' * Active SAP sessions not found. Do not forget to enable SAP GUI scripting')
                return

            for sap_session, sap_info in sap_sessions:
                out_dict = dict()
                print("[GUI Scripting] Connected to sapsid:{sid}, server:{app_server}, user:{user} ".format(
                    sid=sap_info["sid"],
                    app_server=sap_info["app_server"],
                    user=sap_info["user"]))
                try:
                    result = SAPConnection.load_software_components(sap_session)
                except Exception as err:
                    print(" * Software Components -")
                    print("[ERROR] " + str(err))
                else:
                    if result:
                        filename = SAPConnection.save_software_components(result)
                        if filename:
                            out_dict["softs"] = filename
                            print(" * Software Components +")
                try:
                    result = SAPSoftwareComponents.load_sap_core_info(sap_session)
                except Exception as err:
                    print(" * Kernel Version & Kernel Patch Release -")
                    print("[ERROR] " + str(err))
                else:
                    if result:
                        out_dict.update(result)
                        print(" * Kernel Version & Kernel Patch Release +")

                try:
                    tbl = TCodeSE16("CWBNTCUST", sap_session=sap_session)
                    filename = SAPConnection.__choose_filename("cwbntcust_{date}.txt")
                    tbl.save_table_content(os.path.dirname(filename), os.path.basename(filename))
                except Exception as err:
                    print(" * The CWBNTCUST table -")
                    print("[ERROR] " + str(err))

                else:
                    if os.path.exists(filename):
                        out_dict["cwbntcust"] = filename
                        print(" * The CWBNTCUST table +")

                if len(out_dict):
                    SAPConnection.send_it_to_server(out_dict, system_name, wait)

    @staticmethod
    def load_software_components(sap_session):
        data = SAPSoftwareComponents.load_software_components(sap_session)
        if data:
            return data

    @staticmethod
    def __choose_filename(fileformat):
        filepath = os.path.join(Path.home(), SUBDIR)
        if not os.path.exists(filepath):
            os.makedirs(filepath)

        filepath = os.path.join(filepath, TEMPDIR)
        if not os.path.exists(filepath):
            os.makedirs(filepath)

        filename = fileformat.format(date=datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
        return get_file_name(filename, filepath)

    @staticmethod
    def save_software_components(data):
        if not data:
            return

        filename = SAPConnection.__choose_filename("softs_{date}.txt")

        with open(filename, "w") as f:
            for line in data:
                f.write("\t".join(line)+"\n")

        return filename

    @staticmethod
    def send_it_to_server(data, system_name, wait):
        if not data or not len(data):
            return

        cmd_command = list()
        files_to_delete = list()
        cmd_command.append("offlinesec_sap_notes")

        if "softs" in data.keys():
            cmd_command.append('-f "%s"' % (data["softs"],))
            files_to_delete.append(data["softs"])
        else:
            return

        if "krnl_version" in data.keys() and "krnl_patch_level" in data.keys():
            cmd_command.append('-k %s -p %s' % (data["krnl_version"], data["krnl_patch_level"]))

        if "cwbntcust" in data.keys():
            cmd_command.append('-c "%s"' % (data["cwbntcust"],))
            files_to_delete.append(data["cwbntcust"])

        if system_name:
            cmd_command.append('-s "%s"' % (system_name,))

        if wait:
            cmd_command.append('--wait')

        os.system(" ".join(cmd_command))

        for file in files_to_delete:
            if os.path.exists(file):
                os.remove(file)


def main():
    SAPConnection.sap_notes_report()


if __name__ == '__main__':
    main()
