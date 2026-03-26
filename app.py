from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
import random

app = Flask(__name__)
app.secret_key = "secret123"

DB = "database.db"

# -------------------------
# DATABASE SETUP (AUTO FIX)
# -------------------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS shipments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking_code TEXT,
        status TEXT,
        location TEXT,
        sender TEXT,
        receiver TEXT,
        weight TEXT,
        fee TEXT,
        description TEXT,
        delivery_address TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking_code TEXT,
        status TEXT,
        location TEXT,
        time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

init_db()

# -------------------------
# GENERATE TRACKING CODE
# -------------------------
def generate_code():
    return "AMX" + str(random.randint(100000, 999999))

# -------------------------
# HOME
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")

# -------------------------
# LOGIN (HIDDEN ADMIN)
# -------------------------
@app.route("/secure-admin-login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect("/dashboard")

    return render_template("login.html")

# -------------------------
# DASHBOARD
# -------------------------
@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/secure-admin-login")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM shipments")
    data = c.fetchall()
    conn.close()

    return render_template("dashboard.html", shipments=data)

# -------------------------
# CREATE SHIPMENT
# -------------------------
@app.route("/create", methods=["POST"])
def create():
    try:
        conn = sqlite3.connect(DB)
        c = conn.cursor()

        code = generate_code()

        data = (
            code,
            request.form["status"],
            request.form["location"],
            request.form["sender"],
            request.form["receiver"],
            request.form["weight"],
            request.form["fee"],
            request.form["description"],
            request.form["delivery_address"]
        )

        c.execute("""
        INSERT INTO shipments 
        (tracking_code, status, location, sender, receiver, weight, fee, description, delivery_address)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data)

        c.execute("""
        INSERT INTO history (tracking_code, status, location)
        VALUES (?, ?, ?)
        """, (code, request.form["status"], request.form["location"]))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    except Exception as e:
        return f"CREATE ERROR: {e}"

# -------------------------
# UPDATE SHIPMENT
# -------------------------
@app.route("/update", methods=["POST"])
def update():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    code = request.form["code"]
    status = request.form["status"]
    location = request.form["location"]

    c.execute("UPDATE shipments SET status=?, location=? WHERE tracking_code=?",
              (status, location, code))

    c.execute("INSERT INTO history (tracking_code, status, location) VALUES (?, ?, ?)",
              (code, status, location))

    conn.commit()
    conn.close()

    return redirect("/dashboard")

# -------------------------
# TRACK PAGE
# -------------------------
@app.route("/track", methods=["POST"])
def track():
    code = request.form["code"]

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT * FROM shipments WHERE tracking_code=?", (code,))
    shipment = c.fetchone()

    c.execute("SELECT status, location, time FROM history WHERE tracking_code=?", (code,))
    history = c.fetchall()

    conn.close()

    return render_template("track.html", shipment=shipment, history=history)

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
