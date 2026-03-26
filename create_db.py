import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

# USERS TABLE (multi-admin)
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# SHIPMENTS TABLE (FULL UPDATED STRUCTURE)
c.execute("""
CREATE TABLE IF NOT EXISTS shipments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tracking_code TEXT UNIQUE,
    sender TEXT,
    receiver TEXT,
    status TEXT,
    location TEXT,
    weight TEXT,
    fee TEXT,
    description TEXT,
    delivery_address TEXT,
    lat TEXT,
    lng TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# HISTORY TABLE
c.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tracking_code TEXT,
    status TEXT,
    location TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# CREATE DEFAULT ADMIN
c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("admin", "admin123"))

conn.commit()
conn.close()

print("✅ Database created successfully")
