"""
SQL Database
"""

import sqlite3

def connect_db():
    conn = sqlite3.connect('quotes_sql.db')
    return conn

def create_db(conn):
    conn.cursor().execute('''CREATE TABLE quotes (quote text, author text)''')

def insert_db(conn, sql_item):
    conn.cursor().execute('INSERT INTO quotes VALUEs (?,?)', sql_item)

def commit_changes(conn):
    conn.commit()
    conn.close()




