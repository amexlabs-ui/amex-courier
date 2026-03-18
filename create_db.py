import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS shipments(
id INTEGER PRIMARY KEY AUTOINCREMENT,
tracking TEXT UNIQUE,
status TEXT,
location TEXT
)
""")

# CREATE DEFAULT ADMIN
c.execute("""
CREATE TABLE IF NOT EXISTS admin(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
password TEXT
)
""")

c.execute("SELECT * FROM admin WHERE username='admin'")
if not c.fetchone():
    c.execute("INSERT INTO admin(username,password) VALUES('admin','1234')")

conn.commit()
conn.close()
