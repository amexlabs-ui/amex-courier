from flask import Flask, render_template, request, redirect, session
import sqlite3, random, os

app = Flask(__name__)
app.secret_key = "amex_secure_key"


# ---------- DATABASE INIT ----------
if not os.path.exists("database.db"):
    import create_db


def generate_tracking():
    return "AMX" + str(random.randint(100000,999999))


# ---------- DB HELPER ----------
def get_db():
    return sqlite3.connect("database.db")


# ---------- HOME ----------
@app.route("/")
def home():
    return render_template("index.html")


# ---------- LOGIN ----------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
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

    conn = get_db()
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

    conn = get_db()
    c = conn.cursor()

    c.execute("""
    INSERT INTO shipments(tracking,status,location,sender,receiver,weight,fee)
    VALUES(?,?,?,?,?,?,?)
    """,
    (
        tracking,
        request.form.get("status"),
        request.form.get("location"),
        request.form.get("sender"),
        request.form.get("receiver"),
        request.form.get("weight"),
        request.form.get("fee")
    ))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ---------- UPDATE ----------
@app.route("/update/<tracking>", methods=["POST"])
def update(tracking):
    if not session.get("admin"):
        return redirect("/login")

    conn = get_db()
    c = conn.cursor()

    c.execute("""
    UPDATE shipments
    SET status=?, location=?, fee=?
    WHERE tracking=?
    """,
    (
        request.form.get("status"),
        request.form.get("location"),
        request.form.get("fee"),
        tracking
    ))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ---------- TRACK ----------
@app.route("/track", methods=["POST"])
def track():
    code = request.form.get("tracking")

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM shipments WHERE tracking=?", (code,))
    result = c.fetchone()
    conn.close()

    return render_template("tracking.html", result=result)


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run()
