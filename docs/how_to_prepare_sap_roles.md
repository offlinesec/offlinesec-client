# How to generate SAP Critical Authorizations in Roles Report

## Supported system types:
* SAP NetWeaver ABAP

## Required information
* (required) Assigned authorization objects to roles: table AGR_1251. [How to get info](./get_table.md)
* (highly recommended) Roles assigned to users: table AGR_USERS. [How to get info](./get_table.md)
* (highly recommended) User settings and statuses: table USR02. [How to get info](./get_table.md)

## Script usage
1. Prepare all required data (tables AGR_1251, AGR_USERS, USR02)
2. Create a new configuration file for the report (yaml file) [YAML file structure](./yaml_file_roles_structure.md)
3. Run the script and get your report automatically in a few seconds:
```sh
offlinesec_sap_roles -f "cfg_roles_report.yaml"
```

4. (optionally) you can additionally set in the script:
   * "-na" Exclude roles that are not assigned to any user (Required AGR_USERS and USR02 tables)
   * "-ff" Exclude FireFighter roles from the check. (In YAML file you need to set masks for FF roles)
   * "--do-not-send" if you want to check the information transmitted first (the data won't leave your laptop)
   * "-v" if you know a specific variant for your check

