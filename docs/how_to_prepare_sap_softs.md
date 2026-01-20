# How to generate SAP Security Note Report

## Supported system types:
* SAP NetWeaver ABAP (+ Kernel, SAPUI5, HANA)
* SAP NetWeaver JAVA (+ Kernel, HANA)
* Business Object 

## Required information 
Whatever script you are going to use, you need to prepare the input data first.

### Required information from ABAP system
* (required) Installed software component list. [How to get info](./how_to_get_soft_components.md)
* (required) Installed sap note list: table CWBNBTCUST. [How to get info](./get_table.md)
* (highly recommended) Kernel version and kernel patch level. [How to get info](./how_to_get_soft_components.md). Allows you to scan kernel binaries for security vulnerabilities.
* (recommended) Installed sap note list from DEV environment: table CWBNTCUST from DEV system. [How to get info](./get_table.md). Reduces number of false positives. Shows note implementation progress.
* (optionally) Installed sap note versions: table CWBNTHEAD. [How to get info](./get_table.md). Adds sap note version checks.
* (optionally) Host agent version and patch level
* (recommended) SAPUI5 version. FIORI portal, Personal settings->About.
* (recommended) HANA DB version. Menu System:Status, Database data:Release.

### Required information from JAVA system
* (required) Installed software component list. [How to get info](./how_to_prepare_java_softs.md)
* (highly recommended) Kernel version and kernel patch level. Allows you to scan kernel binaries for security vulnerabilities.

### Required information from BO system
* (required) Installed BO version. [How to get info](./how_to_prepare_bo_version.md)

## Script usage
* [Multi-system script](./how_to_request_multi_system_scan.md) (recommended)
* Single-mode script (outdated)
  * [SAP NetWeaver ABAP](./how_to_request_single_mode_scan.md)
  * [SAP NetWeaver JAVA](./how_to_prepare_java_softs.md)
  * [SAP Businees Objects](./how_to_prepare_bo_version.md)

## Tips
* To track progress (vulnerabilities and installed patches) please every time use the same system names. This helps the engine interpret the data correctly.