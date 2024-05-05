# How to use Offlinesec API SAP Security Notes
API Use Cases:
Integration with SIEMs, VMs, Ticket systems, Custom dashboards or Visualisation software.

1. Example of API call - please find the api_sec_notes.py script.
Examlpe of calling via cmd:
```commandline
offlinesec_api_secnotes -f systems.yaml -i "Scan Number 1" 
```
2. Works in asynchronous mode
3. To get the result please have a look at the get_reports script. Example of calling via cmd:
```commandline
offlinesec_get_reports
```