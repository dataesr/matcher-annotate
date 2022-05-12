import os

DATA_URL = os.getenv('DATA_URL')
LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', 'data/logs-examples.jsonl')
MATCHER_URL = os.getenv('MATCHER_URL', 'http://localhost:5004')
