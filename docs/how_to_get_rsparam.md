# How to Download RSPARAM Report from SAP

This guide explains how to export the list of profile parameter values from an ABAP system, so this data can be reviewed for SAP Security Baseline Report.

## Prerequisites

- Access to SAP GUI
- A user account with authorization to run RSPARAM report
  - S_TCODE:TCD=SE38 or SA38 (transactions SE38 or SA38)
  - S_PROGRAM:P_ACTION:SUBMIT,P_GROUP=<space> (to execute RSPARAM report)
  - S_GUI:ACTVT=61 (export capabilities)

---

## Exporting Profile Parameter Values

1. Log in to the SAP system using SAP GUI
2. Run transaction SA38 or SE38
3. Enter program name: RSPARAM (Display Profile Parameter). And click **Execute (F8)**
4. Skip the next screen and click again **Execute (F8)**
5. The report output contains SAP profile parameters and their values
   - Parameter Name
   - User-Defined Value
   - System Default Value
   - Comment
6. Download RSPARAM Report
    - Choose in the menu Parameters->Export->Spreadsheet
    - Select the Export icon from the toolbar (Spreadsheet ^&#8679;F7)
7. Enter a file name, for example:
    RSPARAM_<sid>.xlsx
