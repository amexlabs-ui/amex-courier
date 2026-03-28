from flask import Flask, render_template, request, redirect, session
import sqlite3
import random
import string

app = Flask(__name__)
app.secret_key = "secret123"
DB = "database.db"

# ---------------- DB ----------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS shipments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking TEXT UNIQUE,
        user_id INTEGER,
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
        return redirect(f"/track/{request.form['tracking']}")
    return render_template("index.html")

# ---------------- TRACK ----------------
@app.route("/track/<code>")
def track(code):
    try:
        code = code.strip().upper()

        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row  # ✅ prevents index crashes
        c = conn.cursor()

        c.execute("SELECT * FROM shipments WHERE tracking=?", (code,))
        data = c.fetchone()

        conn.close()

        return render_template("track.html", data=data)

    except Exception as e:
        return f"ERROR: {str(e)}"

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                      (request.form["username"], request.form["password"]))
            conn.commit()
        except:
            pass
        conn.close()
        return redirect("/login")
    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect("/dashboard")

        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            return redirect("/user-dashboard")

    return render_template("login.html")

# ---------------- USER DASHBOARD ----------------
@app.route("/user-dashboard")
def user_dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM shipments WHERE user_id=?", (session["user_id"],))
    shipments = c.fetchall()
    conn.close()

    return render_template("user_dashboard.html", shipments=shipments)

# ---------------- ADMIN DASHBOARD ----------------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "admin" not in session:
        return redirect("/login")

    if request.method == "POST":
        tracking = "AMX" + ''.join(random.choices(string.digits, k=6))

        conn = sqlite3.connect(DB)
        c = conn.cursor()

        c.execute("""
        INSERT INTO shipments (tracking, user_id, sender, receiver, address, status, location, weight, fee)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tracking,
            request.form["user_id"],
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
