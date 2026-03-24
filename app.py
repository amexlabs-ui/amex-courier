from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = "change-this-secret-key"


# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect("database.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

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
        description TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY,
        tracking TEXT,
        status TEXT,
        location TEXT,
        lat REAL,
        lng REAL,
        time TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ---------- HOME ----------
@app.route("/")
def home():
    return render_template("index.html")


# ---------- TRACK ----------
@app.route("/track", methods=["POST"])
def track():
    code = request.form.get("tracking")

    conn = get_db()
    shipment = conn.execute("SELECT * FROM shipments WHERE tracking=?", (code,)).fetchone()
    history = conn.execute("SELECT * FROM history WHERE tracking=? ORDER BY id ASC", (code,)).fetchall()
    conn.close()

    return render_template("track.html", shipment=shipment, history=history)


# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    try:
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            if username == "admin" and password == "admin123":
                session["admin"] = True
                return redirect("/admin")
            else:
                return "Invalid login"

        return render_template("login.html")

    except Exception as e:
        return f"Login error: {str(e)}"


# ---------- ADMIN ----------
@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")

    conn = get_db()
    shipments = conn.execute("SELECT * FROM shipments").fetchall()
    conn.close()

    return render_template("admin.html", shipments=shipments)


# ---------- CREATE ----------
@app.route("/create", methods=["POST"])
def create():
    if not session.get("admin"):
        return redirect("/login")

    try:
        tracking = "AMX" + str(random.randint(100000, 999999))

        # SAFE INPUTS
        status = request.form.get("status", "Processing")
        location = request.form.get("location", "Unknown")
        sender = request.form.get("sender", "")
        receiver = request.form.get("receiver", "")
        weight = request.form.get("weight", "")
        fee = request.form.get("fee", "")
        description = request.form.get("description", "")
        delivery_address = request.form.get("delivery_address", "")

        # SAFE FLOAT CONVERSION
        try:
            lat = float(request.form.get("lat", 0))
            lng = float(request.form.get("lng", 0))
        except:
            lat = 0
            lng = 0

        conn = get_db()

        conn.execute("""
        INSERT INTO shipments (
            tracking, status, location, lat, lng,
            sender, receiver, weight, fee, description, delivery_address
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tracking, status, location, lat, lng,
            sender, receiver, weight, fee, description, delivery_address
        ))

        conn.execute("""
        INSERT INTO history (tracking, status, location, lat, lng, time)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (tracking, status, location, lat, lng))

        conn.commit()
        conn.close()

        return redirect("/admin")

    except Exception as e:
        return f"CREATE ERROR: {str(e)}"


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run()
