# How to generate SAP JAVA Security Note Report
1. Login to SAP NetWeaver JAVA system
2. Find SAP JAVA software components according to [Note 1757810](https://launchpad.support.sap.com/#/notes/1757810)
3. Save software components list to CSV file
4. Run in command line interface:
```sh
offlinesec_java_notes -f "java_softs.csv" -s "System JAVA"
```

You can exclude some notes:
```sh
offlinesec_java_notes -f "java_softs.csv" -s "System JAVA" -e "1111111,2222222,3333333"
```
