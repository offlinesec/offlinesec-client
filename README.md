#Offline Security Client

Offline Security is 

## Table of contents

* [Installation](#installation)
* [Quick Start](#quick-start)
* [Use Cases](#use-cases)
* [Important Notes](#important-notes)

## Installation

### Python installation
Install last version of Python [from here](https://www.python.org/downloads/)

### Published version installation (recommended)
```sh
pip install offlinesec_client
```

### Installation from repository on [github.com](https://github.com/offlinesec/offlinesec-client)
```sh
git clone git@github.com:offlinesec/offlinesec-client.git
python -m pip install --upgrade pip
pip install setuptools wheel
python setup.py bdist_wheel
python3 -m pip install dist\offlinesec_client-1.0.1-py3-none-any.whl
```
The Version could be different. Please verify generated wheel name. 

## Quick Start

To check your SAP system against SAP Security Notes:
1. Prepare text file with installed software component versions ([details](./docs/how_to_prepare_sap_softs.md))
2. Send prepared file to server (optional you can set SAP system name):
```sh
offlinesec_sap_notes -f "software_components.txt" -s "Demo System"
```
3. Wait aprox 5 minutes (Depends on server load)
4. Download report:
```sh
offlinesec_get_reports
```
5. Find your report in Downloads folder. Enjoy.

## Use Cases

1. SAP Security Notes Analysis (Vulnerabilities Check)
* [How to prepare data and request report](./docs/how_to_prepare_sap_softs.md)
* [Report example](./docs/sap_security_notes_report.md)
* Our knowledge base is constantly updated. You can find the date of last loaded SAP Security Note in your report.

## Important Notes:
1. We don't collect any client identity like email address, SAP SIDs, ip addresses. All Checks are performed fully anonymously.
2. The reports aren't stored on server side. Once you have downloaded the report it's deleted.
3. The report could download only the person who has token (Random String generated on first start).
4. You can download reports within 10 days after it was requested.

Additional information is available [here](./docs/README.md)