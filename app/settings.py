import os


api_local_ip_address = os.environ['API_LOCAL_IP_ADDRESS']
api_local_ip_port = int(os.environ['API_LOCAL_IP_PORT'])
workers_count = int(os.environ['WORKERS_COUNT'])
logging_level = os.environ['LOGGING_LEVEL']
api_domain = os.environ['API_DOMAIN']
api_path = os.environ['API_PATH']
db_min_connections = os.environ['DB_MIN_CONNECTIONS']
db_max_connections = os.environ['DB_MAX_CONNECTIONS']
dbusr = os.environ['DB_USER_NAME']
dbpwd = os.environ['DB_USER_PASSWORD']
dbip = os.environ['DB_IP_ADDRESS']
dbport = os.environ['DB_IP_PORT']
dbname = os.environ['DB_NAME']
auth_private_key_file = os.environ['AUTH_PRIVATE_KEY_FILE']
