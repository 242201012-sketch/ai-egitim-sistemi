import sqlite3

from flask import Flask, render_template_string, request, redirect, session
import werkzeug.security # pyright: ignore[reportMissingImports]


app = Flask(__name__)
app.secret_key = "supersecretkey"

# DATABASE
def connect_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# TABLOLARI OLUŞTUR
def create_tables():
    conn = connect_db()
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

create_tables()

# ANA SAYFA
@app.route("/")
def home():
    return render_template_string("""
    <html>
    <head>
        <title>AI Eğitim Platformu</title>
        <style>
            body{
                font-family:Arial;
                background:#0f172a;
                color:white;
                text-align:center;
                padding-top:100px;
            }

            h1{
                font-size:50px;
            }

            a{
                text-decoration:none;
                background:#2563eb;
                color:white;
                padding:12px 25px;
                border-radius:10px;
                margin:10px;
                display:inline-block;
            }

            a:hover{
                background:#1d4ed8;
            }
        </style>
    </head>
    <body>

        <h1>AI Eğitim Platformu</h1>

        <a href="/register">Kayıt Ol</a>
        <a href="/login">Giriş Yap</a>

    </body>
    </html>
    """)

# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed_password = werkzeug.security.generate_password_hash(password)

        conn = connect_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (username, hashed_password)
            )

            conn.commit()

            return redirect("/login")

        except:
            return "Bu kullanıcı zaten var."

    return render_template_string("""
    <h1>Kayıt Ol</h1>

    <form method="POST">
        <input type="text" name="username" placeholder="Kullanıcı Adı"><br><br>
        <input type="password" name="password" placeholder="Şifre"><br><br>

        <button>Kayıt Ol</button>
    </form>
    """)

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )

        user = cursor.fetchone()

        if user and werkzeug.security.check_password_hash(user["password"], password):

            session["user"] = user["username"]
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect("/admin")

            return redirect("/student")

        else:
            return "Hatalı giriş."

    return render_template_string("""
    <h1>Giriş Yap</h1>

    <form method="POST">
        <input type="text" name="username" placeholder="Kullanıcı Adı"><br><br>
        <input type="password" name="password" placeholder="Şifre"><br><br>

        <button>Giriş Yap</button>
    </form>
    """)

# STUDENT PANEL
@app.route("/student")
def student():

    if "user" not in session:
        return redirect("/login")

    return render_template_string("""
    <h1>Öğrenci Paneli</h1>

    <p>Hoş geldin {{user}}</p>

    <a href="/quiz">Quiz Çöz</a><br><br>

    <a href="/logout">Çıkış Yap</a>
    """, user=session["user"])

# ADMIN PANEL
@app.route("/admin")
def admin():

    if "user" not in session:
        return redirect("/login")

    if session["role"] != "admin":
        return "Yetkisiz erişim"

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    html = "<h1>Admin Paneli</h1>"

    html += "<h3>Kullanıcılar</h3>"

    for user in users:
        html += f"<p>{user['username']} - {user['role']}</p>"

    html += """
    <br>
    <a href="/add_quiz">Quiz Ekle</a><br><br>
    <a href="/logout">Çıkış Yap</a>
    """

    return html

# QUIZ EKLE
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

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO quizzes(question,option1,option2,option3,option4,answer)
        VALUES(?,?,?,?,?,?)
        """, (question, option1, option2, option3, option4, answer))

        conn.commit()

        return redirect("/admin")

    return render_template_string("""
    <h1>Quiz Ekle</h1>

    <form method="POST">

        <input name="question" placeholder="Soru"><br><br>

        <input name="option1" placeholder="Şık 1"><br><br>
        <input name="option2" placeholder="Şık 2"><br><br>
        <input name="option3" placeholder="Şık 3"><br><br>
        <input name="option4" placeholder="Şık 4"><br><br>

        <input name="answer" placeholder="Doğru Cevap"><br><br>

        <button>Kaydet</button>

    </form>
    """)

# QUIZ SAYFASI
@app.route("/quiz")
def quiz():

    if "user" not in session:
        return redirect("/login")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM quizzes")
    quizzes = cursor.fetchall()

    html = "<h1>Quizler</h1>"

    for q in quizzes:

        html += f"""
        <div style='border:1px solid gray;padding:20px;margin:20px'>
            <h3>{q['question']}</h3>

            <p>A) {q['option1']}</p>
            <p>B) {q['option2']}</p>
            <p>C) {q['option3']}</p>
            <p>D) {q['option4']}</p>
        </div>
        """

    html += "<a href='/student'>Panele Dön</a>"

    return html

# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ÇALIŞTIR
if __name__ == "__main__":
    app.run(debug=True)

