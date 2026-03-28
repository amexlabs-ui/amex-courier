from flask import Flask, render_template, request, redirect
import sqlite3
import random

app = Flask(__name__)

DB = "database.db"

# ---------- DATABASE INIT ----------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS shipments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking TEXT,
        sender TEXT,
        receiver TEXT,
        address TEXT,
        weight TEXT,
        fee TEXT,
        status TEXT,
        location TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------- HOME ----------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        code = request.form.get("tracking", "").strip().upper()
        return redirect(f"/track/{code}")

    return render_template("index.html")

# ---------- TRACK ----------
@app.route("/track/<code>")
def track(code):
    code = code.strip().upper()

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM shipments WHERE tracking=?", (code,))
    data = c.fetchone()

    conn.close()

    return render_template("track.html", data=data)

# ---------- ADMIN DASHBOARD ----------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if request.method == "POST":
        tracking = "AMX" + str(random.randint(100000, 999999))
        sender = request.form["sender"]
        receiver = request.form["receiver"]
        address = request.form["address"]
        weight = request.form["weight"]
        fee = request.form["fee"]
        status = request.form["status"]
        location = request.form["location"]

        c.execute("""
        INSERT INTO shipments 
        (tracking, sender, receiver, address, weight, fee, status, location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (tracking, sender, receiver, address, weight, fee, status, location))

        conn.commit()

    c.execute("SELECT * FROM shipments ORDER BY id DESC")
    shipments = c.fetchall()

    conn.close()

    return render_template("admin.html", shipments=shipments)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
