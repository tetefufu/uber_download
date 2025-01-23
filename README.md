## Uber Downloader

Ability to download Uber reports automatically

### Commands to Build Executables

```bash
pyinstaller --onefile download_report.py
pyinstaller --onefile download_report_careem.py
```

### Instructions

config.yml

For careem - start from number

- 1 is min
- 3 to go back 3 weeks

## Yango

- Generates rolling 30 days
- Reads creds from `curl_yango.txt`
- Reads output folder from `config.yml`
- Reads from x days (eg 30 or 60) from `yango_start_from` in `config.yml`

## Zed

- Generates rolling 30 days
- Reads creds from `curl.txt`
- Reads output folder from `config.yml`
- Reads from x days (eg 30 or 60) from `report_start_from` in `config.yml`

## Uber

- Generates multiple reports
- Can read `reports` (see below). If missing, generates only REPORT_TYPE_PAYMENTS_ORDER

```
reports:
  - REPORT_TYPE_PAYMENTS_ORDER
  - REPORT_TYPE_PAYMENTS_ORGANIZATION
```
