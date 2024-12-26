# How to generate SAP Profile Parameters Report
To collect information about current values of profile parameters in SAP System do the following:
1. Log in SAP System using SAP GUI software
2. Call SA38 or SE38 transaction
3. Perform RSPARAM report
4. Press F8 to proceed
5. Save table content to file (Excel). Format - Excel Open XML Format(XLSX)<br />
![Screenshot](./img/rsparam_save.png)

Note: You can download profile values from all application servers. The values can be different in theory.

Then you need to prepare config file in YAML format (set system names and profile files). The details are [here](./yaml_params_structure.md).
System names will be masked on the client side!

To send the data to the server run the following script:
```sh
offlinesec_sap_params -f "params_config.yaml"
```

Also you can set the file with exclusions:
```sh
offlinesec_sap_params -f "params_config.yaml" -e "exclusions.yaml"
```
The example of exclusion file:
```yaml
- system_name: "ECC"
  param_name: "login/min_password_lng"
  comment: "Too strict requirement"
- system_name: "S/4"
  param_name: "rsau/enable"
- system_name: "*"
  param_name: "login/disable_cpic"
  until: "10.05.2022"
  comment: "it takes a lot of time"
```

If you have registered the custom baseline, you can choose its identifier via -v option:
```sh
offlinesec_sap_params -f "params_config.yaml" -v 1234
```

if you would like to check if the file contains any sort of sensitive information you can split process:
```sh
offlinesec_sap_params -f "params_config.yaml" --do-not-send
```

Your report will be ready in 5 minutes. Run offlinesec_get_reports.
