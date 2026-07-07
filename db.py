import mysql.connector
import os

def get_db_connection():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "Kasturi123#"),
        database=os.getenv("DB_NAME", "stock_project")
    )
    return conn
