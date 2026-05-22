from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

# DATABASE
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'student'
    )
    """)

    cursor.execute("""
CREATE TABLE IF NOT EXISTS quizzes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    option1 TEXT,
    option2 TEXT,
    option3 TEXT,
    option4 TEXT,
    answer TEXT
)
""")

    conn.commit()
    conn.close()

init_db()

# HOME
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/quiz")
def quiz():

    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM quizzes")

    quizzes = cursor.fetchall()

    conn.close()

    return render_template(
        "quiz.html",
        quizzes=quizzes
    )

@app.route("/add_quiz", methods=["GET", "POST"])
def add_quiz():

    if "user" not in session:
        return redirect("/login")

    if session["role"] != "admin":
        return "Yetkisiz erişim"

    if request.method == "POST":

        question = request.form["question"]
        option1 = request.form["option1"]
        option2 = request.form["option2"]
        option3 = request.form["option3"]
        option4 = request.form["option4"]
        answer = request.form["answer"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO quizzes(
            question,
            option1,
            option2,
            option3,
            option4,
            answer
        )
        VALUES(?,?,?,?,?,?)
        """, (
            question,
            option1,
            option2,
            option3,
            option4,
            answer
        ))

        conn.commit()
        conn.close()

        return redirect("/admin")

    return render_template("add_quiz.html")

# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (username, hashed_password)
            )

            conn.commit()

        except:
            return "Kullanıcı zaten mevcut"

        conn.close()

        return redirect("/login")

    return render_template("register.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )

        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[2], password):

            session["user"] = user[1]
            session["role"] = user[3]

            if user[3] == "admin":
                return redirect("/admin")

            return redirect("/student")

        else:
            return "Hatalı kullanıcı adı veya şifre"

    return render_template("login.html")

# STUDENT PANEL
@app.route("/student")
def student():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "student_dashboard.html",
        username=session["user"]
    )

# ADMIN PANEL
@app.route("/admin")
def admin():

    if "user" not in session:
        return redirect("/login")

    if session["role"] != "admin":
        return "Yetkisiz erişim"

    return render_template(
        "admin_dashboard.html",
        username=session["user"]
    )

# LOGOUT
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

@app.route("/chatbot")
def chatbot():

    if "user" not in session:
        return redirect("/login")

    return render_template("chatbot.html")

if __name__ == "__main__":
    app.run(debug=True)
