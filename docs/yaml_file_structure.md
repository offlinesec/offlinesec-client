First of all you need to set root dir which contains all sap files (software components) that can be referenced in this file.
```sh
root_dir: "D:\\offlinesec\\Test\\1\\"
```
Then you need to define all sap systems:
```sh
sap_systems:
```

General attributes (for all system types):
1. Name - not required attribute, but it can help you to interpret the scan results.
```sh
name: "SAP Demo System"
```
2. Type - mandatory attribute. Please set it to one of the following values: ABAP, JAVA, BO, HANA.
```sh
type: "ABAP"
```
3. Exclude - note exclusions file (to exclude false positives) in yaml format. Please find more details [here](./exclude_file_structure.md).
```sh
exclude: "exclude.yaml"
```

ABAP specific attributes:
1. softs - software components file (txt format). The details are available [here](./how_to_prepare_sap_softs.md).
```sh
softs: "softs.txt"
```
2. cwbntcust - the CWBNTCUST table content in txt or xlsx format. The details are available [here](./how_to_prepare_sap_softs.md).
```sh
cwbntcust: "cwbntcust.txt"
```
3. krnl_version - The Kernel version in the following format  "7.53"
```sh
krnl_version: "7.53"
```
4. krnl_patch - Installed kernel patch number
```sh
krnl_patch: 1101
```
5. cwbntcust form the dev system - the CWBNTCUST table content in txt or xlsx format. The details are available [here](./how_to_prepare_sap_softs.md).
```sh
cwbntcust_dev: "dev_cwbntcust.txt"
```
6. cwbnthead - the CWBNTHEAD table (to check for obsoleted SAP security notes)
```sh
cwbnthead: "cwbnthead.txt"
```
7. sapui5 - sapui5 version
```sh
sapui5: "1.84.56"
```
8. hana - HANA DB version
```sh
hana: "2.00.033.00.1571350"
```

JAVA specific attributes:
1. Softs - Installed JAVA software components and their versions file (csv format). More details are available [here](./how_to_prepare_java_softs.md).
```sh
softs: "java_softs.csv"
```
2. krnl_version - The Kernel version in the following format  "7.53"
```sh
krnl_version: "7.53"
```
3. krnl_patch - Installed kernel patch number
```sh
krnl_patch: 1101
```

BO specific attributes:
1. Version - The BO version in the following format - 14.1.4.1655
```sh
version: 14.1.4.1655
```

You can find entire yaml file example [here](./yaml_fil_example.yaml).