from flask import Flask, render_template, request, redirect, session
import sqlite3, random, os

app = Flask(__name__)
app.secret_key = "amex_secure_key"


# ✅ DATABASE PATH (PERSISTENT STORAGE)
DB_PATH = "/data/database.db"


# ---------- DATABASE CONNECTION ----------
def db():
    return sqlite3.connect(DB_PATH)


# ---------- INIT DATABASE IF NOT EXISTS ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # ADMIN TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS admin(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    # DEFAULT ADMIN
    c.execute("SELECT * FROM admin")
    if not c.fetchone():
        c.execute("INSERT INTO admin(username,password) VALUES('admin','admin123')")

    # SHIPMENTS TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS shipments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking TEXT,
        status TEXT,
        location TEXT,
        sender TEXT,
        receiver TEXT,
        sender_address TEXT,
        receiver_address TEXT,
        weight TEXT,
        size TEXT,
        description TEXT,
        fee TEXT,
        delivery_date TEXT
    )
    """)

    # HISTORY TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking TEXT,
        status TEXT,
        location TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


# RUN INIT
if not os.path.exists(DB_PATH):
    init_db()


# ---------- GENERATE TRACKING ----------
def generate_tracking():
    return "AMX" + str(random.randint(100000, 999999))


# ---------- HOME ----------
@app.route("/")
def home():
    return render_template("index.html")


# ---------- LOGIN ----------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form.get("username")
        p = request.form.get("password")

        conn = db()
        c = conn.cursor()
        c.execute("SELECT * FROM admin WHERE username=? AND password=?", (u,p))
        admin = c.fetchone()
        conn.close()

        if admin:
            session["admin"] = True
            return redirect("/dashboard")

        return render_template("admin_login.html", error="Invalid login")

    return render_template("admin_login.html")


# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/login")

    conn = db()
    c = conn.cursor()
    c.execute("SELECT * FROM shipments ORDER BY id DESC")
    data = c.fetchall()
    conn.close()

    return render_template("dashboard.html", data=data)


# ---------- CREATE SHIPMENT ----------
@app.route("/create", methods=["POST"])
def create():
    if not session.get("admin"):
        return redirect("/login")

    tracking = generate_tracking()

    status = request.form.get("status", "Processing")
    location = request.form.get("location", "Unknown")

    sender = request.form.get("sender", "")
    receiver = request.form.get("receiver", "")
    sender_address = request.form.get("sender_address", "")
    receiver_address = request.form.get("receiver_address", "")
    weight = request.form.get("weight", "")
    size = request.form.get("size", "")
    description = request.form.get("description", "")
    fee = request.form.get("fee", "")
    delivery_date = request.form.get("delivery_date", "")

    conn = db()
    c = conn.cursor()

    c.execute("""
    INSERT INTO shipments(
        tracking,status,location,sender,receiver,
        sender_address,receiver_address,
        weight,size,description,fee,delivery_date
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        tracking, status, location,
        sender, receiver,
        sender_address, receiver_address,
        weight, size, description,
        fee, delivery_date
    ))

    # HISTORY LOG
    c.execute(
        "INSERT INTO history(tracking,status,location) VALUES(?,?,?)",
        (tracking, status, location)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ---------- UPDATE ----------
@app.route("/update/<tracking>", methods=["POST"])
def update(tracking):
    if not session.get("admin"):
        return redirect("/login")

    status = request.form.get("status")
    location = request.form.get("location")

    conn = db()
    c = conn.cursor()

    c.execute(
        "UPDATE shipments SET status=?, location=? WHERE tracking=?",
        (status, location, tracking)
    )

    c.execute(
        "INSERT INTO history(tracking,status,location) VALUES(?,?,?)",
        (tracking, status, location)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ---------- TRACK ----------
@app.route("/track", methods=["POST"])
def track():
    code = request.form.get("tracking")

    conn = db()
    c = conn.cursor()

    c.execute("SELECT * FROM shipments WHERE tracking=?", (code,))
    result = c.fetchone()

    c.execute(
        "SELECT status, location, date FROM history WHERE tracking=? ORDER BY id DESC",
        (code,)
    )
    history = c.fetchall()

    conn.close()

    return render_template("tracking.html", result=result, history=history)


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run()
