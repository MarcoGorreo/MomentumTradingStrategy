import pandas as pd
import sqlite3

def create_and_load_db(excel_path):

    df = pd.read_excel(excel_path)

    conn = sqlite3.connect('sqlitedb.db')

    table_name = 'dati'
    df.to_sql(table_name, conn, if_exists='replace', index=False)
