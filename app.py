from flask import Flask, render_template, request, redirect, session
import sqlite3
import random
import string

app = Flask(__name__)
app.secret_key = "secret123"

DB = "database.db"

# ---------------- DB INIT ----------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS shipments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking TEXT UNIQUE,
        sender TEXT,
        receiver TEXT,
        address TEXT,
        status TEXT,
        location TEXT,
        weight TEXT,
        fee TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- HOME ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        code = request.form["tracking"]
        return redirect(f"/track/{code}")
    return render_template("index.html")

# ---------------- TRACK ----------------
@app.route("/track/<code>")
def track(code):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT * FROM shipments WHERE tracking=?", (code,))
    data = c.fetchone()
    conn.close()

    return render_template("track.html", data=data)

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin123":
            session["admin"] = True
            return redirect("/dashboard")
    return render_template("login.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "admin" not in session:
        return redirect("/login")

    if request.method == "POST":
        tracking = "AMX" + ''.join(random.choices(string.digits, k=6))

        conn = sqlite3.connect(DB)
        c = conn.cursor()

        c.execute("""
        INSERT INTO shipments (tracking, sender, receiver, address, status, location, weight, fee)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tracking,
            request.form["sender"],
            request.form["receiver"],
            request.form["address"],
            request.form["status"],
            request.form["location"],
            request.form["weight"],
            request.form["fee"]
        ))

        conn.commit()
        conn.close()

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM shipments")
    shipments = c.fetchall()
    conn.close()

    return render_template("dashboard.html", shipments=shipments)

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
