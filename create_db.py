import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS shipments(
id INTEGER PRIMARY KEY AUTOINCREMENT,
tracking TEXT UNIQUE,
status TEXT,
location TEXT,
sender TEXT,
receiver TEXT,
weight TEXT,
fee TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS admin(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
password TEXT
)
""")

# CREATE ADMIN SAFELY
c.execute("SELECT * FROM admin WHERE username='admin'")
if not c.fetchone():
    c.execute("INSERT INTO admin(username,password) VALUES('admin','1974')")

conn.commit()
conn.close()
