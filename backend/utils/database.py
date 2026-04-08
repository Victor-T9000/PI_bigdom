import mysql.connector
from config import Config

def get_db_connection():
    return mysql.connector.connect(**Config.DB_CONFIG)

def execute_query(query, params=None, commit=False, fetch_one=False, fetch_all=False):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(query, params or ())

        if commit:
            conn.commit()
            return cursor.lastrowid

        if fetch_one:
            return cursor.fetchone()

        if fetch_all:
            return cursor.fetchall()

        return cursor.rowcount
    finally:
        cursor.close()
        conn.close()