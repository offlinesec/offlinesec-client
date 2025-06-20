# Offline Security Client
The Offline Security is cloud based application which is intended to assess security aspects of SAP systems. All needed information for our security reports/analytics you gather yourself (or you can use [Offline Security Connector](https://github.com/offlinesec/offlinesec-connector)). Then you send us all gathered information (using cli tool) to the cloud server. Important: All sensitive information (SAPSIDs, IP addresses, server names, usernames and so on) is masked on client side and doesn't leave your laptop (that's why we need client software). Also we don’t collect any identity data of our users (for instance IPs, emails and company name). So it can provide additional level of security.
Finally, we produce analysis on server side and issue for you report which can download only you.   
So, Offline Security is the perfect tool for SAP penetration test and SAP Security audit. It provides completely independent view on your security status of your SAP landscape. Ypu can easily check how your security department is doing.   

# Advantages

* Quick start: Only you need to install client tool on ANY LAPTOP with Python using one cli command
* Full Transparency. All configurations files are open. The source code of client application is available to read as well (open source)
* You don't need to invest money to SAP Solution Manager consultants or buy expensive products for SAP Security
* Don't need to create user account in target SAP systems (The user is needed only for Offline Security Connector). Don't need to install any ABAP code on your systems!
* Possibility of customisation. Based on predefined check list you can create your own checks (probably even not related to Information Security)
* Our database is regularly updated. Always base checks are available out-of-box
* Excellent reports in Excel spreadsheet format, easy to use, share and filter 

## Table of contents

* [Installation](#installation)
* [Quick Start](#quick-start)
* [Use Cases](#use-cases)
* [Important Notes](#important-notes)

## Installation

### Python installation
Install the last version of Python 3.x [from here](https://www.python.org/downloads/)<br />
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

If you need full automatic process please install [Offline Security Connector](https://github.com/offlinesec/offlinesec-connector) - RFC connector

### Upgrade to the latest published version
```sh
pip3 install --upgrade offlinesec_client
```

### Check what version is installed right now on your laptop
```sh
pip3 show offlinesec_client
```

## Quick Start
How to discovery missed SAP Security Notes:
1. Prepare a text file with installed SAP software component versions ([details](./docs/how_to_prepare_sap_softs.md))
2. Download CWBNTCUST table content ([details](./docs/how_to_prepare_sap_softs.md))
3. Check kernel version and kernel patch
4. Send all prepared files to the server (optionally you can set the SAP system name):
```sh
offlinesec_sap_notes -f "software_components.txt" -s "Demo System" -k 721 -p 402 -c "cwbntcust.xlsx"
```
The report will be automatically downloaded in few seconds.
5. Find your report in Downloads folder. Enjoy.

## Use Cases
### Missed SAP Security Notes (Unpatched SAP security vulnerabilities)
Installing security patches on the SAP platform is critical for ensuring the integrity, confidentiality, and availability of your SAP environment. Here are the main reasons why security patches are essential for SAP systems:
* Protection from cyberattacks. Mitigating the Risk of Exploitation of Known Vulnerabilities
* Compliance with industry regulations (GDPR, HIPAA, SOX, ...)
* Safeguarding sensitive business data in SAP (financial records, customer information, intellectual property, ...)
* Preventing downtime and system disruptions. Sometimes it helps maintain System Stability and Performance
* Protecting Against Data Breaches

The following report options are available: 
* one system - offlinesec_sap_notes (ABAP), offlinesec_java_notes, offlinesec_bo_notes
* multi systems - offlinesec_sec_notes

The report (excel spreadsheet) will contain:
* Information about missed sap security notes for SAP systems. Our knowledge base is constantly updated and contain all SAP security notes released since 2015. The Offline Security Knowledgebase contains definitions for ABAP, JAVA, Kernel(ABAP,JAVA,WD), Business Object, Host Agent software.
* Charts about the most critical findings and general statistic
* The implementation status and progress status from the SNOTE transaction (if the note was downloaded to the system)
* The implementation status and progress status from the SNOTE transaction on development system (if the note was downloaded to the system)
* The info about available workaround and public exploits for security notes
* SLA violation for system patching if the note was released a long time ago (need to set SLA rules)
* Information about patching progress (historical data from previous scans)

Anonymised on the client side (the info doesn't leave your laptop):
* System Names (SIDs)

Available additional options:
* Manage exclusions (exclude some notes from the report)
* Exclude SAP Notes marked as "Not Relevant"
* Attach information from DEV environment
* Define SLA rules for Note Implementation (How quick BASIS must install security patches)
* Add Host Agent version and Patch
* Add Kernel version and Patch
* VBS automation (gui script) to collect all required data (only for Windows laptops)
* the API to integrate with SIEM or VM is already available

What else:
* [How to prepare data and request report](./docs/how_to_prepare_sap_softs.md)
* [Report example](./docs/sap_security_notes_report.md)

### System Parameters Report (SAP Security Baseline Checks, DSAG, SAP Notes and Documentation)
Configuring SAP systems according to the SAP Security Baseline is essential for ensuring that your SAP environment is secure, compliant, and protected from various internal and external threats. The SAP Security Baseline is a set of recommended security configurations and best practices designed by SAP (or someone else) to minimize risks, enhance system integrity, and protect sensitive business data. Here are key reasons why SAP systems need to be configured according to the SAP Security Baseline:
* Mitigating Security Risks
* Standardization of Security Measures in Companies
* Compliance with Regulatory Requirements (GDPR, HIPAA, SOX, ...)
* Protecting Sensitive Business Data
* Improving Incident Detection and Response
* Preventing Unauthorized Access and Insider Threats

The following report options are available:
* multi systems - offlinesec_sap_params

The report (excel spreadsheet) will contain:
* Information about baseline violations
* Charts about the most critical findings and general statistic
* Three baselines are already available by default: SAP Security Baseline, DSAG Recommendation, Recommendations from SAP notes and documentation
* You can register some exclusions for parameters
* Parameter Discrepancies (if you have different values for security parameters on different application servers) 
* You can register your personal custom baseline and check if your SAP meet your custom requirements
* Information on remediation progress (historical data from previous scans)

Anonymised on the client side (the info doesn't leave your laptop):
* System Names (SIDs)
* File paths with SID

What else:
* [How to generate report](./docs/how_to_prepare_sap_params.md)
* [Report Example](./docs/sap_params_report.md)

### Roles/Critical Privileges Analysis (Available since version 1.0.15)
In any SAP environment, roles define what users can do and what they shouldn’t be able to do. When roles contain critical authorizations, they can pose serious risks if not properly managed.
Here’s why it’s crucial to identify them:
* Prevent Fraud and Misuse. Critical authorizations (like unrestricted access to financial transactions or user management) can be exploited for fraudulent activity if assigned to the wrong users.
* Protect Sensitive Data. SAP systems often hold business-critical and personal data. Uncontrolled access can lead to data breaches or violations of data protection laws (e.g., GDPR).
* Pass Internal and External Audits. Auditors frequently review access rights. Roles with unchecked critical permissions can trigger audit findings, penalties, or even project delays.
* Reduce Attack Surface. Insecure authorizations increase the likelihood of cyberattacks or insider threats. Minimizing critical permissions limits potential damage.
* Comply with Best Practices and Standards. Standards like the SAP Security Baseline and DSAG recommendations emphasize the need for strict control over critical authorizations. Following them improves your overall security posture.
* Avoid SoD (Segregation of Duties) Violations. Some critical combinations of permissions (e.g., create and approve payments) lead to SoD conflicts. These must be identified and remediated to maintain internal control integrity.

The report (excel spreadsheet) will contain:
* Critical authorisations in roles
* Information about users (how many users have this role)
* Sign if role is FireFighter or not
* Critical authorisation definitions are based on SAP Security Baseline, DSAG, best practises 

Anonymised on the client side (the info doesn't leave your laptop):
* System Names (SIDs)
* Role names

What else:
* [How to generate report](./docs/how_to_prepare_sap_roles.md)
* [Report Example](./docs/sap_roles_report.md)

### Transport Request Analysis (Available since version 1.1.8)
* [How to generate report](./docs/how_to_prepare_abap_report.md)

### Insecure RFC Connections 
Securing RFC (Remote Function Call) connections between SAP systems is crucial for several reasons. RFC is a protocol used by SAP systems to enable communication between different systems, whether within the same landscape or across different environments. If these connections are not secured, it could lead to a variety of security risks, including unauthorized access, data theft, and system vulnerabilities. Here's why securing RFC connections is essential:
* Protection Against Unauthorized Access
* Preventing Man-in-the-Middle Attacks
* Preventing Privilege Escalation Techniques
* Compliance and Regulatory Requirements

The report (excel spreadsheet) will contain:
* List of all RFC and HTTP connections between SAP systems
* Charts about the most critical findings and general statistic
* RFC connections without encryption
* RFC connections under dialog user
* RFC connections with critical authorizations
* RFC connections to production systems from non-production

Anonymised on the client side (the info doesn't leave your laptop):
* System Names (SIDs)
* RFC Destinations
* Usernames
* Hostnames, Proxies and IP addresses
* URLs

What else:
* [How to generate report](./docs/how_to_request_rfc_report.md)

### SAP Security Audit Log Analysis, ICF services, Users with critical authorizations
* Will be available in next releases

If the report was not downloaded automatically, please download it manually:
```sh
offlinesec_get_reports
```

If you need more  - please email me info@offlinesec.com.

## Important Notes (security measures):
1. We don't collect any client identity like email address, SAP SIDs, company, ip addresses. All Checks are performed fully anonymously.
2. The reports aren't stored on server side. Once you have downloaded the report it's deleted.
3. All data transferred to server is encrypted with HTTPS protocol. 
4. The report could download only the person who has token (Random String generated on first start).
5. Review the source code. You can be 100% confident what happening on client side with your data, how it is processed and which information will be sent to the server

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