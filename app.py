import sqlite3
from flask import Flask, render_template, request, redirect, session, url_for

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