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

    tracking = "AMX" + str(random.randint(100000, 999999))

    data = (
        tracking,
        request.form["status"],
        request.form["location"],
        float(request.form["lat"]),
        float(request.form["lng"]),
        request.form["sender"],
        request.form["receiver"],
        request.form["weight"],
        request.form["fee"],
        request.form["description"]
    )

    conn = get_db()

    conn.execute("""
    INSERT INTO shipments (tracking, status, location, lat, lng, sender, receiver, weight, fee, description)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

    conn.execute("""
    INSERT INTO history (tracking, status, location, lat, lng, time)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (tracking, data[1], data[2], data[3], data[4], datetime.now()))

    conn.commit()
    conn.close()

    return redirect("/admin")


# ---------- UPDATE ----------
@app.route("/update/<tracking>", methods=["POST"])
def update(tracking):
    if not session.get("admin"):
        return redirect("/login")

    status = request.form["status"]
    location = request.form["location"]
    lat = float(request.form["lat"])
    lng = float(request.form["lng"])

    conn = get_db()

    conn.execute("""
    UPDATE shipments SET status=?, location=?, lat=?, lng=? WHERE tracking=?
    """, (status, location, lat, lng, tracking))

    conn.execute("""
    INSERT INTO history (tracking, status, location, lat, lng, time)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (tracking, status, location, lat, lng, datetime.now()))

    conn.commit()
    conn.close()

    return redirect("/admin")


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run()
