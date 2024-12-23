# Offline Security Client
You definitely haven't seen such approach before! Suitable for those who would like to protect his SAP systems and don’t want to pay a lot. Or maybe you are only interested in Compliance topic.
So, Offline Security is cloud based application which is intended to assess security aspects of SAP systems. All needed information for our security reports/analytics you gather yourself (or you can easily automate it using any RPA solution). Then you send us all gathered information (using cli tool). Important: All sensitive information (SAPSIDs, IP addresses, server names, and so on) is masked. And we don’t request any identity data of our clients.  It means that NOBODY – our administrators, developers or external hacker can’t link this information with particular client, particular system or particular company.
Finally, we produce analysis on server side and issue for you report which can download only you (client application that sent all data).   

# Advantages

* Quick start: Only you need to install client tool using one cli command
* Full Transparency. All configurations files are open. The source code of client application is available to read as well
* You don't need to invest money to SAP Solution Manager consultants or buy expensive products like Onapsis or SecurityBridge
* Don't need to create user account in target SAP systems. Don't need to install any ABAP code
* Possibility of customisation. Based on predefined check list you can create your own checks (probably even not related to Information Security)
* Our database is regularly updated. Always base checks are available out-of-box. Even you can see what configurations are used by other clients
* Cool reports, easy to use with predefined filter options 

## Table of contents

* [Installation](#installation)
* [Quick Start](#quick-start)
* [Use Cases](#use-cases)
* [Important Notes](#important-notes)

## Installation

### Python installation
Install last version of Python 3.x [from here](https://www.python.org/downloads/)<br />
We support only Python 3.x!

### Published version installation (recommended)
```sh
pip3 install offlinesec_client
```
or
```sh
python3 -m pip install offlinesec_client
```

Check the installation script output. if you see the following message:
WARNING: The scripts offlinesec_get_reports, offlinesec_inverse_transform, offlinesec_sap_notes, offlinesec_sap_params and offlinesec_sap_roles are installed in '/Users/<username>/Library/Python/3.8/bin' which is not on PATH.

Then add Python folder to the PATH variable:
```sh
export PATH="$PATH:/Users/<username>/Library/Python/3.8/bin"
```

### Installation last version from the repository on [github.com](https://github.com/offlinesec/offlinesec-client)
```sh
git clone https://github.com/offlinesec/offlinesec-client.git
python3 -m pip install --upgrade pip
pip3 install setuptools wheel
python3 setup.py bdist_wheel
python3 -m pip install dist\offlinesec_client-1.0.8-py3-none-any.whl
```
The Version could be different! Please verify generated wheel name. 

### Upgrade to last published version
```sh
pip3 install --upgrade offlinesec_client
```

### Check what version is installed
```sh
pip3 show offlinesec_client
```

## Quick Start

How to discovery missed SAP Security Notes:
1. Prepare text file with installed SAP software component versions ([details](./docs/how_to_prepare_sap_softs.md))
2. Download CWBNTCUST table ([details](./docs/how_to_prepare_sap_softs.md))
3. Check kernel version and kernel patch
4. Send files to the server (optional you can set SAP system name):
```sh
offlinesec_sap_notes -f "software_components.txt" -s "Demo System" -k 721 -p 402 -c "cwbntcust.xlsx"
```
3. Wait aprox 5 minutes (Depends on server load)
4. Download your report:
```sh
offlinesec_get_reports
```
5. Find your downloaded report in Downloads folder. Enjoy.

## Use Cases
1. SAP Security Notes Analysis (Vulnerabilities Check)
* [How to prepare data and request report](./docs/how_to_prepare_sap_softs.md)
* [Report example](./docs/sap_security_notes_report.md)
* Our knowledge base is constantly updated and contain all SAP security notes released in 2015-2023. You can find the date of last loaded SAP Security Note in your report.
* since version 1.0.29 SAP Business Object systems are supported
* since version 1.0.30 SAP JAVA systems are supported
* since version 1.1.0 Offlinsec tool supports multi-system scan
* since version 1.1.0 Offlinesec tool supports last patch day scan
* since version 1.1.2 the API to integrate with SIEM or VM is available in Offlinesec tool

2. Profile Parameters/Compliance Analysis (SAP Security Baseline Checks)
   (Available since version 1.0.12)
* [How to generate report](./docs/how_to_prepare_sap_params.md)
* [Report Example](./docs/sap_params_report.md)
* All sensitive information is excluded from the upload file (SAPSIDs, server names, ...)
* Please remember you can create your own check variants. The details are available [here](https://github.com/offlinesec/offlinesec-knowledgebase)

3. Roles/Critical Privileges Analysis (Available since version 1.0.15)
* [How to generate report](./docs/how_to_prepare_sap_roles.md)
* [Report Example](./docs/sap_roles_report.md)
* All sensitive information is excluded from the upload file (Role names)
* Please remember you can create your own check variants. The details are available [here](https://github.com/offlinesec/offlinesec-knowledgebase)

4. Transport Request Analysis (Available since version 1.1.8)
* [How to generate report](./docs/how_to_prepare_abap_report.md)

5. Insecure RFC Connections (Available since version 1.1.20): RFC connections without encryption, RFC connection with SAP_ALL, RFC connections from development to production and other use cases.
* [How to generate report](./docs/how_to_request_rfc_report.md)

6. SAP Security Audit Log Analysis, ICF services, Users with critical authorizations
* Will be available in next releases

Each time do not forget to download your report from the server:
```sh
offlinesec_get_reports
```

If you need more  - email me info@offlinesec.com.

## Important Notes:
1. We don't collect any client identity like email address, SAP SIDs, company, ip addresses. All Checks are performed fully anonymously.
2. The reports aren't stored on server side. Once you have downloaded the report it's deleted.
3. All data transferred to server are encrypted with HTTPS protocol. 
4. The report could download only the person who has token (Random String generated on first start).
5. You can download reports within 10 days after it was requested.
6. Review the source code. You can be 100% confident what happening on client side with your data and how it is processed.

Additional documentation is available [here](./docs/README.md)

## Known Issues
1. SSL issue when communicate with the server
NotOpenSSLWarning: urllib3 v2.0 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'.

```sh
pip3 install urllib3==1.26.15
```

2. During installation
WARNING: The scripts offlinesec_get_reports, offlinesec_inverse_transform, offlinesec_sap_notes, offlinesec_sap_params and offlinesec_sap_roles are installed in '/Users/<username>/Library/Python/3.8/bin' which is not on PATH.

```sh
export PATH="$PATH:/Users/<username>/Library/Python/3.8/bin"
```

## Uninstall
```sh
python3 -m pip uninstall offlinesec_client
```