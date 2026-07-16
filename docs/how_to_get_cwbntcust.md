# How to export the CWBNTCUST table

This guide explains how to export the CWBNTCUST table content (SAP Note status) from ABAP system, so this data can be reviewed for missing SAP Security Notes.

## Prerequisites

- Access to SAP GUI
- A user account with authorization to view table content 
  - S_TCODE:TCD=SE16 (transaction SE16)
  - S_TABU_NAM:TABLE=CWBNTCUST, ACTVT=03 (access to the table, read-only)
  - S_GUI:ACTVT=61 (export capabilities)

---

## Exporting CWBNTCUST Table
1. Log in to the SAP system using SAP GUI.
2. Go to transaction SE16 (Data Browser). Enter the transaction code "/nSE16" in the command field on the SAP GUI and press Enter.
3. On the next screen set the name of the table you wish to export - CWBNTCUST. Press Enter.
4. On next screen extend Maximum No. of Hits (For inst. set it to 50000, to extract all rows from the CWBNTCUST table).
5. Press F8 (or click on Execute button).
6. To extract table content in text format go to menu System -> List -> Save -> Local file. Then choose **Unconverted** format.
7. Save file to local disk.