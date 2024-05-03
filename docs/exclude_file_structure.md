In the exclusion file you can specify the notes that will be excluded from the results.
Why?
* In case of false positives
* You implemented workaround
* You are confident that the note not applicable for your system (Profile parameter set or service disabled)
* You need much time to implement the note

Possible attributes:
1. Note - SAP Security Note number (mandatory attribute).
```sh
note: "1111111"
```
2. Until - The date until which the note will be excluded from the results
```sh
until: "10.05.2022"
```
3. Comment - Why this note excluded from the results
```sh
comment: "Due to false positive"
```

The example of exclude file you can find [here](./exclude_file_example.yaml) 