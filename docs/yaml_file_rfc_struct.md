First of all you need to set root dir which contains all sap files (rfcdes, usr02, ust04 tables) that can be referenced in this file.
```sh
root_dir: "D:\\offlinesec\\Test\\1\\"
```
Then you need to define all sap systems:
```sh
sap_systems:
```

General attributes (for all systems):
1. name - here please type real SID (will be anonymised)
```sh
name: "TST"
```
2. role - mandatory attribute. Please set system role (development, test, production). Choose one of the following:
```sh
role: "sndbox" # for sandbox systems
role: "dev" # for development systems
role: "prd" # for production systems
role: "qa" # for qa/test systems
role: "pre-prod" # for pre-production systems
```
3. rfcdes - file name of RFCDES table which was extracted from this SID.
```sh
rfcdes: "TST_RFCDES.txt"
```

4. ust04  - file name(s) of UST04 table(s) which was extracted from this SID.
```sh
ust04: "TST_UST04.txt"
ust04: ["TST_000_UST04.txt", "TST_001_UST04.txt", "TST_100_UST04.txt"]
```

5. usr02  - file name(s) of USR02 table(s) which was extracted from this SID.
```sh
usr02: "TST_USR02.txt"
usr02: ["TST_000_USR02.txt", "TST_001_USR02.txt", "TST_100_USR02.txt"]
```

You can find entire yaml file example [here](./yaml_rfc_file_example.yaml).