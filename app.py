from flask import Flask, render_template, request, redirect, session
import sqlite3
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"


# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS shipments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking TEXT,
        status TEXT,
        location TEXT,
        sender TEXT,
        receiver TEXT,
        weight TEXT,
        fee TEXT,
        description TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking TEXT,
        status TEXT,
        location TEXT,
        time TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------- TRACK ----------------
@app.route("/track", methods=["POST"])
def track():
    code = request.form["tracking"]

    conn = get_db()
    shipment = conn.execute("SELECT * FROM shipments WHERE tracking=?", (code,)).fetchone()
    history = conn.execute("SELECT * FROM history WHERE tracking=? ORDER BY id DESC", (code,)).fetchall()
    conn.close()

    return render_template("track.html", shipment=shipment, history=history)


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        password = request.form["password"]

        if user == "admin" and password == "admin123":
            session["admin"] = True
            return redirect("/admin")
        else:
            return "Wrong login"

    return render_template("login.html")


# ---------------- ADMIN ----------------
@app.route("/admin")
def admin():
    if "admin" not in session:
        return redirect("/login")

    conn = get_db()
    shipments = conn.execute("SELECT * FROM shipments").fetchall()
    conn.close()

    return render_template("admin.html", shipments=shipments)


# ---------------- CREATE ----------------
@app.route("/create", methods=["POST"])
def create():
    if "admin" not in session:
        return redirect("/login")

    tracking = "AMX" + str(random.randint(100000, 999999))

    status = request.form["status"]
    location = request.form["location"]
    sender = request.form["sender"]
    receiver = request.form["receiver"]
    weight = request.form["weight"]
    fee = request.form["fee"]
    description = request.form["description"]

    conn = get_db()

    conn.execute("""
    INSERT INTO shipments (tracking, status, location, sender, receiver, weight, fee, description)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (tracking, status, location, sender, receiver, weight, fee, description))

    conn.execute("""
    INSERT INTO history (tracking, status, location, time)
    VALUES (?, ?, ?, ?)
    """, (tracking, status, location, datetime.now()))

    conn.commit()
    conn.close()

    return redirect("/admin")


# ---------------- UPDATE ----------------
@app.route("/update/<tracking>", methods=["POST"])
def update(tracking):
    if "admin" not in session:
        return redirect("/login")

    status = request.form["status"]
    location = request.form["location"]

    conn = get_db()

    conn.execute("""
    UPDATE shipments SET status=?, location=? WHERE tracking=?
    """, (status, location, tracking))

    conn.execute("""
    INSERT INTO history (tracking, status, location, time)
    VALUES (?, ?, ?, ?)
    """, (tracking, status, location, datetime.now()))

    conn.commit()
    conn.close()

    return redirect("/admin")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
