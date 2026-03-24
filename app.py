from flask import Flask, render_template, request, redirect, session
import sqlite3
import random

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ======================
# DATABASE INIT
# ======================
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS shipments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking TEXT UNIQUE,
        status TEXT,
        location TEXT,
        fee TEXT,
        weight TEXT,
        description TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking TEXT,
        status TEXT,
        location TEXT,
        time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ======================
# GENERATE TRACKING
# ======================
def generate_tracking():
    return "AMX" + str(random.randint(100000, 999999))

# ======================
# HOME
# ======================
@app.route("/")
def home():
    return render_template("index.html")

# ======================
# TRACKING PAGE
# ======================
@app.route("/track", methods=["POST"])
def track():
    tracking = request.form["tracking"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    shipment = c.execute(
        "SELECT * FROM shipments WHERE tracking=?",
        (tracking,)
    ).fetchone()

    history = c.execute(
        "SELECT status, location, time FROM history WHERE tracking=? ORDER BY time DESC",
        (tracking,)
    ).fetchall()

    conn.close()

    return render_template("tracking.html", shipment=shipment, history=history)

# ======================
# ADMIN LOGIN
# ======================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect("/admin-dashboard")

    return render_template("login.html")

# ======================
# DASHBOARD
# ======================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect("/admin-dashboard")

    return render_template("login.html")
# ======================
# CREATE SHIPMENT
# ======================
@app.route("/create", methods=["POST"])
def create():
    if not session.get("admin"):
        return redirect("/secure-admin-login-amex")

    status = request.form["status"]
    location = request.form["location"]
    fee = request.form["fee"]
    weight = request.form["weight"]
    description = request.form["description"]

    tracking = generate_tracking()

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
        INSERT INTO shipments (tracking, status, location, fee, weight, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (tracking, status, location, fee, weight, description))

    c.execute("""
        INSERT INTO history (tracking, status, location)
        VALUES (?, ?, ?)
    """, (tracking, status, location))

    conn.commit()
    conn.close()

    return redirect("/admin-dashboard")

# ======================
# UPDATE SHIPMENT
# ======================
@app.route("/update/<tracking>", methods=["POST"])
def update(tracking):
    if not session.get("admin"):
        return redirect("/secure-admin-login-amex")

    status = request.form["status"]
    location = request.form["location"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
        UPDATE shipments
        SET status=?, location=?
        WHERE tracking=?
    """, (status, location, tracking))

    c.execute("""
        INSERT INTO history (tracking, status, location)
        VALUES (?, ?, ?)
    """, (tracking, status, location))

    conn.commit()
    conn.close()

    return redirect("/admin-dashboard")

# ======================
# RUN
# ======================
if __name__ == "__main__":
    app.run(debug=True)
