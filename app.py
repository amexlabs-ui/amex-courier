from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3, random, os

app = Flask(__name__)
app.secret_key = "secret123"

# ✅ AUTO CREATE DATABASE (FIXES YOUR ERROR)
if not os.path.exists("database.db"):
    import create_db


def generate_tracking():
    return "AMX" + str(random.randint(100000000,999999999))


@app.route("/")
def home():
    return render_template("index.html")


# -------- USER SYSTEM --------

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute("INSERT INTO users VALUES(NULL,?,?,?,?)",
                  (request.form["username"],
                   request.form["email"],
                   request.form["password"],
                   "customer"))

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=? AND password=?",
                  (request.form["username"], request.form["password"]))

        user = c.fetchone()

        if user:
            session["user"] = user[0]
            session["role"] = user[4]

            if user[4] == "admin":
                return redirect("/dashboard")
            else:
                return redirect("/account")

    return render_template("login.html")


@app.route("/account")
def account():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM shipments WHERE user_id=?", (session["user"],))
    shipments = c.fetchall()

    conn.close()

    return render_template("account.html", shipments=shipments)


# -------- TRACKING --------

@app.route("/track", methods=["POST"])
def track():
    tracking = request.form["tracking"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM tracking WHERE tracking=?", (tracking,))
    data = c.fetchall()

    conn.close()

    return render_template("tracking.html", data=data, tracking=tracking)


# -------- ADMIN --------

@app.route("/dashboard")
def dashboard():
    if "user" not in session or session.get("role") != "admin":
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM shipments")
    shipments = c.fetchall()

    conn.close()

    return render_template("dashboard.html", shipments=shipments)


@app.route("/create", methods=["GET","POST"])
def create():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":

        tracking = generate_tracking()

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute("INSERT INTO shipments VALUES(NULL,?,?,?,?,?,?,?)",
                  (tracking,
                   request.form["sender"],
                   request.form["receiver"],
                   request.form["origin"],
                   request.form["destination"],
                   "Pending Payment",
                   session["user"]))

        c.execute("INSERT INTO tracking VALUES(NULL,?,?,?,date('now'))",
                  (tracking,"Shipment Created",request.form["origin"]))

        conn.commit()
        conn.close()

        return redirect("/payment?tracking="+tracking)

    return render_template("create.html")


# -------- PAYMENT --------

@app.route("/payment")
def payment():
    tracking = request.args.get("tracking")
    return render_template("payment.html", tracking=tracking)


# -------- AUTO PAYMENT VERIFY --------

@app.route("/ipn", methods=["POST"])
def ipn():
    data = request.json

    if data and data.get("payment_status") == "finished":

        tracking = data.get("order_id")

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute("UPDATE shipments SET status='Paid' WHERE tracking=?", (tracking,))
        conn.commit()
        conn.close()

        print("Payment confirmed:", tracking)

    return {"status":"ok"}


# -------- API --------

@app.route("/api/track/<tracking>")
def api_track(tracking):

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT status,location,date FROM tracking WHERE tracking=?", (tracking,))
    data = c.fetchall()

    conn.close()

    return jsonify(data)


if __name__ == "__main__":
    app.run()
