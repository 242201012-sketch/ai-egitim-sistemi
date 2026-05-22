import os
import sqlite3

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session
)
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

# ==================================================
# APP
# ==================================================

app = Flask(__name__)

app.secret_key = "super_secret_key"


# ==================================================
# UPLOAD
# ==================================================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "static",
    "uploads"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ==================================================
# DATABASE
# ==================================================

def get_db():

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    return conn


def create_tables():

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'student'

    )
    """)

    conn.commit()
    conn.close()


create_tables()


# ==================================================
# HOME
# ==================================================

@app.route("/")
def home():

    return render_template("index.html")


# ==================================================
# REGISTER
# ==================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        conn = get_db()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO users(username,password)
                VALUES(?,?)
                """,
                (username, hashed_password)
            )

            conn.commit()

        except:

            return "Kullanıcı zaten mevcut"

        finally:

            conn.close()

        return redirect("/login")

    return render_template("register.html")


# ==================================================
# LOGIN
# ==================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM users
            WHERE username=?
            """,
            (username,)
        )

        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user"] = user["username"]
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect("/admin_dashboard")

            return redirect("/student_dashboard")

        return "Hatalı giriş"

    return render_template("login.html")


# ==================================================
# LOGOUT
# ==================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ==================================================
# STUDENT PANEL
# ==================================================

@app.route("/student_dashboard")
def student_dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "student_dashboard.html",
        username=session["user"]
    )


# ==================================================
# ADMIN PANEL
# ==================================================

@app.route("/admin_dashboard")
def admin_dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "admin_dashboard.html",
        username=session["user"]
    )


# ==================================================
# AI QUIZ
# ==================================================

def generate_ai_questions(topic):

    topic = topic.lower()

    if topic == "python":

        return [

            {
                "question": "Python nedir?",

                "options": [
                    "Programlama Dili",
                    "Tarayıcı",
                    "Oyun",
                    "İşletim Sistemi"
                ],

                "answer": "Programlama Dili"
            },

            {
                "question": "Python hangi alanda kullanılır?",

                "options": [
                    "Web",
                    "AI",
                    "Otomasyon",
                    "Hepsi"
                ],

                "answer": "Hepsi"
            }
        ]

    elif topic == "html":

        return [

            {
                "question": "HTML ne için kullanılır?",

                "options": [
                    "Web Tasarımı",
                    "Veritabanı",
                    "Sunucu",
                    "Oyun"
                ],

                "answer": "Web Tasarımı"
            }
        ]

    return []


@app.route("/ai_quiz")
def ai_quiz():

    topic = request.args.get("topic", "python")

    questions = generate_ai_questions(topic)

    return render_template(
        "ai_quiz.html",
        questions=questions,
        topic=topic
    )


@app.route("/upload_lesson", methods=["GET", "POST"])
def upload_lesson():

    if request.method == "POST":

        title = request.form.get("title", "")

        pdf = request.files.get("pdf")

        if pdf is None:
            return "PDF bulunamadı"

        if pdf.filename is None or pdf.filename == "":
            return "Dosya seçilmedi"

        filename: str = str(pdf.filename)

        filepath: str = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        pdf.save(filepath)

        return render_template(
            "upload_success.html",
            title=title,
            filename=filename
        )

    return render_template("upload_lesson.html")


# ==================================================
# VIDEO LESSONS
# ==================================================

@app.route("/video_lessons")
def video_lessons():

    videos = [

        {
            "title": "Python Ders",
            "url": "https://www.youtube.com/embed/kqtD5dpn9C8"
        },

        {
            "title": "HTML Ders",
            "url": "https://www.youtube.com/embed/qz0aGYrrlhU"
        },

        {
            "title": "CSS Ders",
            "url": "https://www.youtube.com/embed/1PnVor36_40"
        }
    ]

    return render_template(
        "video_lessons.html",
        videos=videos
    )


# ==================================================
# RUN
# ==================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )