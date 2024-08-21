# How to generate SAP BO Security Note Report
1. Log In SAP Business Object system
2. Find SAP BO version according to [Note 1945588](https://launchpad.support.sap.com/#/notes/1945588) (CMC -> About)
3. Run in command line interface:
```sh
offlinesec_bo_notes -ver "14.3.2.4169" -s "System 1"
```
