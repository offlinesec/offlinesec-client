# Offline Security Client

Offline Security is new IT Security Project like no other. It based on client-server model. You collect yourself all the necessary data for analysis, send it to server and get the report.
Analysis is performed on the server side.<br />
We don't require any client-specific information (email, company, ip address). That's why we can't link the analysis results with particular company or particular SAP system. The Analysis performed fully anonymously! <br />
All sensitive information like SAPSIDs, ip addresses, server names, role names, and so on will be masked. That's why we need client software.

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

### Installation last version from repository on [github.com](https://github.com/offlinesec/offlinesec-client)
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
2. Send prepared file to server (optional you can set SAP system name):
```sh
offlinesec_sap_notes -f "software_components.txt" -s "Demo System"
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

2. Profile Parameters/Compliance Analysis (SAP Security Baseline Checks)
   (Available since version 1.0.12)
* [How to generate report](./docs/how_to_prepare_sap_params.md)
* [Report Example](./docs/sap_params_report.md)
* All sensitive information is excluded from the upload file (SAPSIDs, server names, ...)
* Please remember you can create your own check variants. The details are available [here](https://github.com/offlinesec/offlinesec-knowledgebase)

3. Role/Privilege Analysis
* Will be available in next releases

4. Transport Request Analysis
* Will be available in next releases

5. SAP Security Audit Log Analysis
* Will be available in next releases

If you need more  - email me info@offlinesec.com.

## Important Notes:
1. We don't collect any client identity like email address, SAP SIDs, company, ip addresses. All Checks are performed fully anonymously.
2. The reports aren't stored on server side. Once you have downloaded the report it's deleted.
3. All data transferred to server are encrypted with HTTPS protocol. 
4. The report could download only the person who has token (Random String generated on first start).
5. You can download reports within 10 days after it was requested.
6. Review the source code. You can be 100% confident what happening on client side with your data and how it is processed.

Additional documentation is available [here](./docs/README.md)