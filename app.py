from flask import Flask, render_template, request, redirect, session
import sqlite3, random, os

app = Flask(__name__)
app.secret_key = "amex_secure_key"


# ---------- INIT DB ----------
if not os.path.exists("database.db"):
    import create_db


def db():
    return sqlite3.connect("database.db")


def generate_tracking():
    return "AMX" + str(random.randint(100000,999999))


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


# ---------- CREATE ----------
@app.route("/create", methods=["POST"])
def create():
    if not session.get("admin"):
        return redirect("/login")

    tracking = generate_tracking()

    # SAFE INPUTS (no crashes even if empty)
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

    c.execute(
        "INSERT INTO history(tracking,status,location) VALUES(?,?,?)",
        (tracking, status, location)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")

    # HISTORY
    c.execute(
        "INSERT INTO history(tracking,status,location) VALUES(?,?,?)",
        (tracking, request.form.get("status"), request.form.get("location"))
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
