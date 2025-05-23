# How to generate SAP Security Note Report

Single system mode (quickly scan one system): 
* [SAP Businees Objects](./how_to_prepare_bo_version.md)
* [SAP NetWeaver JAVA](./how_to_prepare_java_softs.md)
* [Patch Day Scan](./how_to_request_patch_day_scan.md)

Multi system mode (more features, recommended):
* [Multi-system Scan](./how_to_request_multi_system_scan.md)

## Data preparation
Whatever script you are going to use, you need to prepare the input data first.

### ABAP Software Components
To collect information about installed software components in ABAP system do the following:
1. Log in SAP System using SAP GUI software
2. Go to System -> Status (Menu)
3. Open the Installed Software window<br />
![Screenshot](./img/softs_button.png)
4. You can see the window with installed software components and their versions.<br />
![Screenshot](./img/installed_softs.png)
5. Now you need to copy all information to text file(utf-8 coding). Please highlight first line then press Ctrl+A (select all) and Ctrl+C (copy to clipboard).
Create new text file (.txt extension) and insert all data from the buffer. The file should look like this:<br />
![Screenshot](./img/text_softs.png)

* Important Note: if you encounter the following error message<br />
![Screenshot](./img/error1.jpg)

You should do the following:
* Highlight first line in the table
* Slowly scroll down the table until the end
* Press Ctrl+A, Ctrl+C. Now All information from the table will be copied to the buffer.

### ABAP Kernel version and kernel patch
(If you want to see missed SAP Security Notes related to Kernel)
1. Log in SAP System using SAP GUI software
2. Go to System -> Status (Menu)
3. Open Kernel Information Window<br />
![Screenshot](./img/kernel_button.png)
4. Save Kernel Version and Kernel Patch<br />
![Screenshot](./img/kernel.png)
5. Append this information to server request:
```sh
offlinesec_sap_notes -f "software_components.txt" -s "Demo System" -k 721 -p 402
```

### Installed SAP Security note versions (only for [Multi-system Scan](./how_to_request_multi_system_scan.md))
(it helps to identify obosleted note versions)
1. Log in SAP System using SAP GUI software
2. Go to the transaction SE16
3. Download the CWBNTHEAD table according to [this manual](./get_table.md)

### Implemented sap notes (without package) - information from the SNOTE transaction
(it helps to reduce false positive number)
1. Log in SAP System using SAP GUI software
2. Go to the transaction SE16
3. Download the CWBNTCUST table according to [this manual](./get_table.md)
```sh
offlinesec_sap_notes -f "software_components.txt" -s "Demo System" -k 721 -p 402 -c "cwbntcust.xlsx"
```

### VBS script on ABAP platform (only on Windows)
(It help automatically export required data)
For those who installed offlinesec_client on Windows platform it's available gui scripting option.
1. Login to SAP system
2. Enable SAP GUI scripting (Transaction RZ11 and the sapgui/user_scripting parameter)
3. Run the script

```sh
offlinesec_sap_notes --guiscript -s "SID"
```
where 'SID' - the system name

## Script Usage Options
1. To send software component list to the Offline Security server (required argument) please run
```sh
offlinesec_sap_notes -f "software_components.txt"
```

2. Set the system name to improve results (It helps you to interpreter the results). A System name - optional parameter.
```sh
offlinesec_sap_notes -f "software_components.txt" -s "Demo System"
```

3. Choose kernel patch and kernel release (It adds vulnerabilities regarding kernel to the final report). Kernel info - optional parameter. It helps discover missed SAP security notes related to Kernel.
```sh
offlinesec_sap_notes -f "software_components.txt" -s "Demo System" -k 721 -p 402
```

4. Add information about implemented notes (It excludes possible false positives from the report). An optional parameter. It helps to exclude already implemented notes.
```sh
offlinesec_sap_notes -f "software_components.txt" -s "Demo System" -k 721 -p 402 -c "cwbntcust.xlsx"
```

5. Add information on Host Agent version and patch (It adds vulnerabilities regarding host agent to the final report). An optional parameter. If you want to include missed SAP security notes related to Host Agent to the report.
```sh
offlinesec_sap_notes -f "software_components.txt" -s "Demo System" -k 721 -p 402 --host-agent-ver "7.22" --host-agent-patch 11
```

6. Add information about exclusions (false positive and workaround implementation). Example is available [here](./yaml_exclude_example.yaml). It can exclude false positives from the report.
```sh
offlinesec_sap_notes -f "software_components.txt" -s "Demo System" -k 721 -p 402 -e "exclude.yaml"
```

7. Explicitly set check variant. 1 - only hotnews and high priority notes, 2 - only hotnews, high priority and medium priority notes.
```sh
offlinesec_sap_notes -f "software_components.txt" -s "Demo System" -k 721 -p 402 -v 1
```

8. Set SLA rules. An example is available [here](./yaml_sla_example.yaml).
```sh
offlinesec_sap_notes -f "software_components.txt" -s "Demo System" -k 721 -p 402 -l "sla_rules.yaml"
```

9. If you want to get the report on specific date in past (without recently released notes) 
```sh
offlinesec_sap_notes -f "software_components.txt" -s "Demo System" -k 721 -p 402 -d "25-11-2024"
```

10. Don't send all information to the server. Review the info first
```sh
offlinesec_sap_notes -f "software_components.txt" -s "Demo System" -k 721 -p 402 --do-not-sent
```
and then repeat the command without the "--do-not-send" option
```sh
offlinesec_sap_notes -f "software_components.txt" -s "Demo System" -k 721 -p 402
```

11. Add CWBNTCUST table from development system
```sh
offlinesec_sap_notes -f "software_components.txt" -s "Demo System" -k 721 -p 402 -c "cwbntcust.xlsx" -cd "dev_cwbntcust.xlsx"
```

Note: Not to forget to download your Offline Security report
```sh
offlinesec_get_reports
```

12. Keep notes marked as 'Not Relevant' (option -nr) in the SNOTE transaction
```sh
offlinesec_sap_notes -f "software_components.txt" -s "Demo System" -k 721 -p 402 -nr
```



