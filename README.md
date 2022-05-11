# matcher-annotate
UI to parse and annotate the results of the matcher-affiliation

## Logs
The input log format should be in JSONL format.
Each JSON object should contain 5 attributes : "type", "query", "strategy", "expected" and "matched".
Type is a string between "grid" and "rnsr".
Query is a string.
Strategy is a string containing the strategy that matched.
Expected is a string containing the id expected. If multiple ids, they are comma delimited.
Matched is a string containing the id matched. If multiple ids, they are comma delimited.

## Start app
`make start`