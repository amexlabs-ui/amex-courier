import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

# USERS
c.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
email TEXT,
password TEXT,
role TEXT
)
""")

# SHIPMENTS
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

# 🔥 CREATE ADMIN USER (IMPORTANT)
c.execute("SELECT * FROM users WHERE username='admin'")
if not c.fetchone():
    c.execute("""
    INSERT INTO users(username,email,password,role)
    VALUES('admin','admin@amex.com','1778','admin')
    """)

conn.commit()
conn.close()
