import sqlite3

def create_database():
    with sqlite3.connect('database.db') as connection:
        c = connection.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS members (
                     id INTEGER PRIMARY KEY,
                     money INTEGER DEFAULT 0,
                     experience INTEGER DEFAULT 0,)''')
