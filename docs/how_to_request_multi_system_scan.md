
# How to generate Multi-System Report

1. Define Yaml file with your SAP systems. The details are [here](./yaml_file_structure.md)
2. Run offlinsec tool:
```sh
offlinesec_sec_notes -f "sapsystems.yaml"
```

or add the unique identifier to the scan (to distinguish the scan results)
```sh
offlinesec_sec_notes -f "sapsystems.yaml" -i "Scan Number 14"
```

## Additional options:
1. Keep notes marked as 'Not Relevant' (option -nr)
```sh
offlinesec_sec_notes -f "sapsystems.yaml" -nr
```

2. Choose check variant (option -v)
```sh
offlinesec_sec_notes -f "sapsystems.yaml" -v 1
```
(Ignore if you don't know)

3. Specify SLA multi system file (option -l)
```sh
offlinesec_sec_notes -f "sapsystems.yaml" -l sla.yaml
```

4. If you want to get the report on specific date in past (without recently released notes)
```sh
offlinesec_sec_notes -f "sapsystems.yaml" -l sla.yaml -d "25-11-2024"
```

5. Don't send all information to the server. Review the info first
```sh
offlinesec_sec_notes -f "sapsystems.yaml" -l sla.yaml --do-not-send
```
