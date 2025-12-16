import psycopg2
import os
from dotenv import load_dotenv

from typing import Optional

load_dotenv()


class DB:
    def __init__(self, conn_string: Optional[str] = None):
        """
        DB constructor accepts a full connection string or uses local defaults.
        """
        # local config
        pg_config = {
            "host": os.environ.get("DB_HOST"),
            "user": os.environ.get("DB_USER"),
            "password": os.environ.get("DB_PASSWORD"),
            "dbname": os.environ.get("DB_NAME"),
            "port": int(os.environ.get("DB_PORT")),
        }

        if conn_string:
            conn = conn_string
        else:
            conn = "host={host} dbname={dbname} user={user} password={password} port={port}".format(
                host=pg_config["host"],
                dbname=pg_config["dbname"],
                user=pg_config["user"],
                password=pg_config["password"],
                port=pg_config["port"],
            )

        # establish connection
        self.connection = psycopg2.connect(conn)
        self.cursors = []
        self.cursor = None
        print("Connected to database (local)")

    def query(self, query):
        self.cursor = self.connection.cursor()
        self.cursor.execute(query)
        self.connection.commit()
        self.cursors.append(self.cursor)
        return self.cursor

    def close(self):
        for cursor in self.cursors:
            cursor.close()
        self.cursors = []
        if self.connection:
            self.connection.close()
            print("Database connection closed.")
