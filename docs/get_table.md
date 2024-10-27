# How to extract table from SAP
* Go to transaction SE16
* Set the name of the table you wish to export (For inst. CWBNTCUST, RFCDES, UST04)
![Screenshot](./img/se16_tablename.png)
* On next screen extend Maximum No. of Hits (For inst. set it to 1000000, to extract all rows from the table)
![Screenshot](./img/se16_second_screen.png)
* If you'd like to exclude some columns (For inst. with sensitive info) go to menu Settings -> Format List -> Choose Fields... and unselect columns which you going to exlude
* Press F8 (or click on Execute button)
* To extract table content in XLSX format go to menu Table Entry -> List -> Export -> Spreadsheet...
![Screenshot](./img/se16_xlsx.png)
* To extract table content in text format go to menu System -> List -> Save -> Local file. Then choose Unconverted format
![Screenshot](./img/se16_unconverted_choose.png)
![Screenshot](./img/se16_unconverted.png)

Also you can extract table content via HANA DB (HANA STUDIO).
![Screenshot](./img/hana_table.png)