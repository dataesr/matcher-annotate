# matcher-annotate
UI to parse and annotate the results of the matcher-affiliation

## Config
Create a `.env` file at the root of the project.
Set var env as :
* DATA_URL : string : url to grab the dataset to check : None
* LOG_FILE_PATH : string : path to store the logs : data/logs.jsonl
* MATCHER_URL : string : url to query the matcher : http://localhost:5004

## Start app
`make start`

## Requirements
python-dotenv

## API

| endpoint | method |   query params   | description |
| -------- | ------ | ---------------- | ----------- |
| / | GET | None | Display the homepage |
| /check | GET | type ('grid') | Execute the matcher against our reference data file |
| /logs | GET | None | Return list of logs as array |
| /annotate | GET | None | Annotate matcher errors |
| /grid/GRID_ID | GET | None | Get all Grid info for a given GRID_ID in JSON |
| /rnsr/RNSR_ID | GET | None | Get all RNSR info for a given RNSR_ID in JSON |
