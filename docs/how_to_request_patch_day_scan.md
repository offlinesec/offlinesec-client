# How to generate Patch Day Report

1. Define Yaml file with your SAP systems. The details are [here](./yaml_file_structure.md)
2. Run offlinsec tool:
```sh
offlinesec_patch_day -f "sapsystems.yaml"
```
or (if you'd like to wait 5 minutes and download the report)
```sh
offlinesec_patch_day -f "sapsystems.yaml" -w
```