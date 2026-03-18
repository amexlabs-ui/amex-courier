from flask import Flask, render_template, request, redirect, session
import sqlite3, random, os

app = Flask(__name__)
app.secret_key = "secret123"

# AUTO CREATE DB
if not os.path.exists("database.db"):
    import create_db

def gen_tracking():
    return "AMX" + str(random.randint(1000000,9999999))


@app.route("/")
def home():
    return render_template("index.html")


# -------- AUTH --------

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
            return redirect("/")

    return render_template("login.html")


# -------- ADMIN --------

@app.route("/dashboard")
def dashboard():
    if session.get("role") != "admin":
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM shipments")
    data = c.fetchall()
    conn.close()

    return render_template("dashboard.html", data=data)


@app.route("/create", methods=["GET","POST"])
def create():
    if session.get("role") != "admin":
        return redirect("/login")

    if request.method == "POST":
        tracking = gen_tracking()

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute("INSERT INTO shipments VALUES(NULL,?,?,?,?)",
                  (tracking,
                   "In Transit",
                   request.form["location"],
                   0))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("create.html")


# EDIT LOCATION (IMPORTANT FEATURE YOU ASKED)

@app.route("/update/<tracking>", methods=["POST"])
def update(tracking):
    if session.get("role") != "admin":
        return redirect("/login")

    new_location = request.form["location"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("UPDATE shipments SET location=? WHERE tracking=?",
              (new_location, tracking))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# -------- TRACKING --------

@app.route("/track", methods=["POST"])
def track():
    code = request.form["tracking"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM shipments WHERE tracking=?", (code,))
    data = c.fetchone()

    conn.close()

    return render_template("tracking.html", data=data)


if __name__ == "__main__":
    app.run()
