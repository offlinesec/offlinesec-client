
# How to request Insecure RFC Connections Report

1. Prepare all needed data for the report. You need to extract the following tables from all SAPs in the scope:
   * RFCDES table
   * USR02 table - optional. This table contains info about user status, user type, user group. You can export only the following columns: MANDT, BNAME, UFLAG, CLASS, USTYP. 
   * UST04 table - optional (only data about system profiles which starts with letter 'S'). This table contains info about critical profile assignments (SAP_ALL, SAP_NEW, ...). 

    Note: The tables USR02, UST04 are needed for all SAP clients. Use HANA DB or ST04 transaction to extract data from all client at once. 
    How to export table from system - you can read [here](./get_table.md)

2. Define Yaml file with your landscape. The details are [here](./yaml_file_rfc_struct.md)
3. Run offlinsec tool:
```sh
offlinesec_rfc_report -f "sapsystems.yaml"
```

Note: All sensitive information (RFC destination names, Usernames, Host IP Addresses and hostnames, SIDs, ...) will be automatically anonymized on client side. To check this you can run:
```sh
offlinesec_rfc_report -f "sapsystems.yaml" --do-not-send
```
It prepares all data on client side but will not send them to the server. Then when you will download the report all data will be automatically deanonymized on client side.