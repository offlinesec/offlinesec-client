First of all you need to set root dir which contains all profile files that can be referenced in this file.
```sh
root_dir: "D:\\offlinesec\\Test\\1\\"
```
Below you need to define all profile files inside the "sap_systems" key:
```sh
sap_systems:
```

1. System Name - string (or SID) which help you to interpret the scan results (will be masked on client side) 
```sh
name: "SAP Demo System" 
or
name: "DEV"
```

2. Set all param files (from all application servers) [here](./exclude_file_structure.md). List all profile files using keys which start with "params":
```sh
params_app0: "RSPARAM1.xls"
params_app1: "RSPARAM2.xls"
params_app2: "RSPARAM3.xls"
params_app3: "RSPARAM4.xls"
```

The config file example you can find [here](./yaml_params_file_example.yaml).