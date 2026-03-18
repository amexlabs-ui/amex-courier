import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

c.execute("""
CREATE TABLE users(
id INTEGER PRIMARY KEY,
username TEXT,
email TEXT,
password TEXT,
role TEXT
)
""")

c.execute("""
CREATE TABLE shipments(
id INTEGER PRIMARY KEY,
tracking TEXT,
sender TEXT,
receiver TEXT,
origin TEXT,
destination TEXT,
status TEXT,
user_id INTEGER
)
""")

c.execute("""
CREATE TABLE tracking(
id INTEGER PRIMARY KEY,
tracking TEXT,
status TEXT,
location TEXT,
date TEXT
)
""")

c.execute("INSERT INTO users VALUES (1,'admin','admin@mail.com','admin123','admin')")

conn.commit()
conn.close()
print("DB ready")
