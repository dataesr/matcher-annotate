# matcher-annotate
UI to parse and annotate the results of the matcher-affiliation

## Logs
The input log format should be in JSONL format.
Each JSON object should contain 5 attributes : "type", "query", "strategy", "expected" and "matched".
Type is a string, either "grid" or "rnsr".
Query is a string.
Strategy is a string containing the strategy that matched.
Expected is a string containing the id expected. If multiple ids, they are comma delimited.
Matched is a string containing the id matched. If multiple ids, they are comma delimited.

An example file, can be found in the repo under `data/logs-examples.jsonl`.

## Config
Create a `.env` file at the root of the project.
Set var env as :
* DATA_URL : string : url to grab the dataset to check : None
* LOG_FILE_PATH : string : path to store the logs : data/logs-examples.jsonl
* MATCHER_URL : string : url to query the matcher : http://localhost:5004

## Start app
`make start`

## Requirements
python-dotenv

## API

| endpoint | method |   args   | description |
| -------- | ------ | -------- | ----------- |
| / | GET | None | Display the homepage |
| /navigate | GET | None | Navigate through the logs |
| /logs | GET | None | Return list of logs as array |
| /grid/GRID_ID | GET | None | Get all Grid info for a given GRID_ID in JSON |
| /rnsr/RNSR_ID | GET | None | Get all RNSR info for a given RNSR_ID in JSON |
| /matcher_check_strategies | GET | None | Execute the matcher against our reference file |
