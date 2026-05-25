import os
import sqlite3

import SQLAlchemy
from flask import Flask, render_template, request, redirect, session
from flask_login import LoginManager
from flask_sqlalchemy.model import DefaultMeta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "secretkey"

database_url = os.getenv("DATABASE_URL")

if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1
        )
else:
    database_url = "sqlite:///database.db"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url



app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

# MODELS

class User(db.Model, metaclass=DefaultMeta):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(300),
        nullable=False
    )

    role = db.Column(
        db.String(50),
        default="student"
    )


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500))
    option1 = db.Column(db.String(200))
    option2 = db.Column(db.String(200))
    option3 = db.Column(db.String(200))
    option4 = db.Column(db.String(200))
    correct_answer = db.Column(db.String(200))

class Score(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    score = db.Column(db.Integer)

# SQLITE FUNCTIONS

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


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


# SAMPLE QUESTIONS

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


# ROUTES

@app.route("/")
def home():

    scores = Score.query.order_by(
        Score.score.desc()
    ).all()

    return render_template(
        "index.html",
        scores=scores
    )


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]

        password = generate_password_hash(
            request.form["password"]
        )

        user = User()

        user.username = username
        user.password = password

        db.session.add(user)
        db.session.commit()
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            session["user"] = user.username

            return redirect("/student_dashboard")

    return render_template("login.html")


@app.route("/student_dashboard")
def student_dashboard():
    return render_template("student_dashboard.html")


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


@app.route("/ai", methods=["GET", "POST"])
def ai():

    response = ""

    if request.method == "POST":

        question = request.form["question"]

        response = f"AI cevabı: {question}"

    return render_template(
        "ai.html",
        response=response
    )


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


# CREATE TABLES

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)