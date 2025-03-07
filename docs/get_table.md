# How to extract table from SAP
When logging into SAP, select English.

* Go to transaction SE16
* Set the name of the table you wish to export (For inst. CWBNTCUST, RFCDES, UST04).  In order to download all data from RFCDES table (for Insecure RFC Connections Report) you need to choose ALV List Mode in Settings -> User Parameters... It allows you to extract more data from long column RFCOPTIONS.
![Screenshot](./img/se16_tablename.png)
* On next screen extend Maximum No. of Hits (For inst. set it to 1000000, to extract all rows from the table)
![Screenshot](./img/se16_second_screen.png)
* If you'd like to exclude some columns (For inst. with sensitive info) go to menu Settings -> Format List -> Choose Fields... and unselect columns which you going to exlude
* Press F8 (or click on Execute button).
* To extract table content in XLSX format go to menu Table Entry -> List -> Export -> Spreadsheet...
![Screenshot](./img/se16_xlsx.png)
* To extract table content in text format go to menu System -> List -> Save -> Local file. Then choose Unconverted format
![Screenshot](./img/se16_unconverted_choose.png)
![Screenshot](./img/se16_unconverted.png)

Also, you can extract table content via HANA DB (HANA STUDIO).
<br/> ![Screenshot](./img/hana_table.png)

Important note: To extract data from all clients at once (for inst. tables USR02, UST04) you can use HANA DB Studio or ST04 transaction. You can use the following queries:
* SELECT MANDT, BNAME, UFLAG, CLASS, USTYP FROM USR02
* SELECT MANDT, BNAME, PROFILE FROM UST04 WHERE PROFILE LIKE 'S%'
