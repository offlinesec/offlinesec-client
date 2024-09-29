# How to request ABAP report
1. Copy data transport files (R files) to the local directory on your laptop
2. Run the script
```sh
offlinesec_abap_rep -p "<directory_with_transport files>" -s "Demo System"
```
The script will compress the files and send it to the server. 

Run the offlinesec_get_reports script in 5-10 minutes.
```sh
offlinesec_get_reports
```