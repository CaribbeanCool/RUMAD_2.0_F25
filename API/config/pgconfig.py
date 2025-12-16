import os
from dotenv import load_dotenv

load_dotenv()

pg_config = {
    "host": os.environ.get("DB_HOST"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "dbname": os.environ.get("DB_NAME"),
    "port": int(os.environ.get("DB_PORT")),
}
