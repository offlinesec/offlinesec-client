# Single-mode script usage (ABAP)(outdated)

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

13. VBS script on ABAP platform (only on Windows)
(It help automatically export required data)
For those who installed offlinesec_client on Windows platform it's available gui scripting option.
* Login to SAP system 
* Enable SAP GUI scripting (Transaction RZ11 and the sapgui/user_scripting parameter)
* Run the script

```sh
offlinesec_sap_notes --guiscript -s "SID"
```
where 'SID' - the system name

