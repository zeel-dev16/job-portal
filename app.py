from flask import Flask, render_template, request, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

#Function 
def init_db():
    conn = sqlite3.connect("job.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            password TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            description TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,
            job_id INTEGER
        )
    """)

    conn.commit()
    conn.close()

#step 2 : Function Call here
init_db()

#Step 3 : Start route for HOME

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    message = ""

    if request.method == "POST":
        print("FORM SUBMITTED")

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        hashed_password = generate_password_hash(password)

        if not name or not email or not password:
            message = "⚠️ All fields are required"
        else:
            conn = sqlite3.connect("job.db")
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, hashed_password)
            )

            conn.commit()
            conn.close()

            return redirect("/login") 

    return render_template("register.html", message=message)

@app.route("/login",methods=["GET","POST"])
def login():

    message = ""

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            message = "Fill all fields"
        else:
            conn = sqlite3.connect("job.db")
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM users WHERE email=?",
                (email,)
            )

            user = cursor.fetchone()
            conn.close()

            if user and check_password_hash(user[3],password):
                session["user"]=user[1] #name store kar raha hai 
                return redirect("/dashboard")
            else:
                return "Invalid Email or Password"
        
    return render_template("login.html", message=message)

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("job.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM jobs")
    jobs = cursor.fetchall()

    conn.close()

    return render_template("dashboard.html", jobs=jobs, user=session["user"])

@app.route("/add-job", methods=["GET","POST"])
def add_job():
    if request.method == "POST":
        title = request.form.get("title")
        company = request.form.get("company")
        description = request.form.get("description")

        conn = sqlite3.connect("job.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO jobs (title, company, description) VALUES (?, ?, ?)",
            (title, company, description)
        )

        conn.commit()
        conn.close()

        return redirect("/dashboard")
    
    return render_template("add-job.html")

@app.route("/apply/<int:job_id>")
def apply(job_id):
    if "user" not in session:
        return redirect("/login")
    
    user = session["user"]

    conn = sqlite3.connect("job.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO applications (user_name, job_id) VALUES (?, ?)",
        (user, job_id)
        )
    
    conn.commit()
    conn.close()

    return "Applied Successfully 🎉"

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

#Step 4 : App RUN
if __name__ == "__main__":
    app.run(debug=True)