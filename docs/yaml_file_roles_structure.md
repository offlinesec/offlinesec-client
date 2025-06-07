# The YAML file structure for roles report

* root_dir (optional):
```sh
root_dir: "D:\\offlinesec\\Test\\1\\"
```
The folder with table files for the report

* ff_masks (optional):
```sh
ff_masks: ["_FF_", "-FF-"]
```
A sign that the role is FireFighter role

* systems (required)
```sh
sap_systems:
```
Starts system definitions

* name (required)
```sh
name: "SAP Demo System" 
```
or SID:
```sh
name: "DEV"
```
System name

* agr_1251 (required)
```sh
agr_1251: ["ECC_020_AGR_1251.txt", "ECC_030_AGR_1251.txt"] 
```
or a single table:
```sh
agr_1251: "ECC_020_AGR_1251.txt"
```
The AGR_1251 table. One table (single client) or many tables (many clients) 

* agr_users (optional)
```sh
agr_users: ["ECC_020_AGR_USERS.txt", "ECC_030_AGR_USERS.txt"] 
```
or a single table:
```sh
agr_users: "ECC_020_AGR_USERS.txt"
```
The AGR_USERS table. One table (single client) or many tables (many clients) 

* usr02 (optional)
```sh
agr_1251: ["ECC_020_USR02.txt", "ECC_030_USR02.txt"] 
```
or a single table
```sh
agr_1251: "ECC_020_USR02.txt"
```
The USR02 table. One table (single client) or many tables (many clients) 

The config file example you can find [here](./yaml_roles_example.yaml).