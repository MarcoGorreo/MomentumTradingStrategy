import sqlite3
import pandas as pd

def read_df():

    conn = sqlite3.connect('sqlitedb.db')

    table_name = 'dati'

    query = f"SELECT * FROM {table_name};"

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df