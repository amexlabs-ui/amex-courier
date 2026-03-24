import sqlite3

conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

# ADMIN TABLE
c.execute("""
CREATE TABLE admin(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
password TEXT
)
""")

# DEFAULT ADMIN LOGIN
c.execute("INSERT INTO admin(username,password) VALUES('admin','admin123')")


# SHIPMENTS TABLE (UPDATED STRUCTURE)
c.execute("""
CREATE TABLE IF NOT EXISTS shipments (
    id INTEGER PRIMARY KEY,
    tracking TEXT UNIQUE,
    status TEXT,
    location TEXT,
    lat REAL,
    lng REAL,
    sender TEXT,
    receiver TEXT,
    weight TEXT,
    fee TEXT,
    description TEXT,
    delivery_address TEXT
)
""")

# HISTORY TABLE
c.execute("""
CREATE TABLE history(
id INTEGER PRIMARY KEY AUTOINCREMENT,
tracking TEXT,
status TEXT,
location TEXT,
date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("Database created successfully")
