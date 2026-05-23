from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)
app.secret_key = "secretkey"


# DATABASE
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# QUIZ TABLOSU OLUŞTUR
def create_quiz_table():
    conn = get_db()
    cursor = conn.cursor()

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


create_quiz_table()


# ÖRNEK SORULAR EKLE
def insert_sample_questions():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM quizzes")
    count = cursor.fetchone()[0]

    if count == 0:

        questions = [

            (
                "Python hangi programlama dilidir?",
                "Frontend",
                "Backend",
                "Database",
                "Design",
                "Backend"
            ),

            (
                "HTML ne için kullanılır?",
                "Veritabanı",
                "Web sayfası yapısı",
                "Sunucu",
                "Oyun motoru",
                "Web sayfası yapısı"
            ),

            (
                "CSS ne işe yarar?",
                "Stil tasarımı",
                "Veritabanı",
                "API",
                "Sunucu",
                "Stil tasarımı"
            )

        ]

        cursor.executemany("""
        INSERT INTO quizzes(
            question,
            option1,
            option2,
            option3,
            option4,
            answer
        )
        VALUES(?,?,?,?,?,?)
        """, questions)

        conn.commit()

    conn.close()


insert_sample_questions()


# QUIZ SAYFASI
@app.route("/quiz")
def quiz():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM quizzes")

    questions = cursor.fetchall()

    conn.close()

    return render_template(
        "quiz.html",
        questions=questions
    )


# QUIZ SONUÇ
@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM quizzes")

    questions = cursor.fetchall()

    score = 0

    for question in questions:

        user_answer = request.form.get(
            f"question_{question['id']}"
        )

        if user_answer == question["answer"]:
            score += 1

    total = len(questions)

    conn.close()

    return render_template(
        "result.html",
        score=score,
        total=total
    )

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        return redirect("/login") # pyright: ignore[reportUndefinedVariable]

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        return redirect("/student_dashboard") # pyright: ignore[reportUndefinedVariable]

    return render_template("login.html")


@app.route("/student_dashboard")
def student_dashboard():
    return render_template("student_dashboard.html")


@app.route("/video_lessons")
def video_lessons():

    videos = [
        {
            "title": "Python Ders 1",
            "url": "https://www.youtube.com/embed/kqtD5dpn9C8"
        },
        {
            "title": "Flask Dersleri",
            "url": "https://www.youtube.com/embed/Z1RJmh_OqeA"
        }
    ]

    return render_template(
        "video_lessons.html",
        videos=videos
    )