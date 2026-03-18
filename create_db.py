import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
email TEXT,
password TEXT,
role TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS shipments(
id INTEGER PRIMARY KEY AUTOINCREMENT,
tracking TEXT,
status TEXT,
location TEXT,
lat TEXT,
lng TEXT
)
""")

conn.commit()
conn.close()
