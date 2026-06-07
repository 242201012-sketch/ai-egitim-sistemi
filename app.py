import json

import requests
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash
)
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user
)
from werkzeug.security import (
    check_password_hash
)

from game_db import configure_database
from models import (
    db,
    User,
    Score,
    Quiz
)

import os

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434"
)

# =========================================================
# APP
# =========================================================

app = Flask(__name__)

configure_database(app)

app.secret_key = "super-secret-key-123"

# =========================================================
# LOGIN
# =========================================================

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# =========================================================
# USER LOADER
# =========================================================

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    return render_template("index.html")

# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:
            flash("Bu kullanıcı zaten var.")
            return redirect(url_for("register"))

        new_user = User(
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Kayıt başarılı.")
        return redirect(url_for("login"))

    return render_template("register.html")

# =========================================================
# LOGIN
# =========================================================

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
            login_user(user)

            return redirect(
                url_for("leaderboard")
            )

        flash("Hatalı giriş.")

    return render_template("login.html")

# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("home"))

# =========================================================
# LEADERBOARD
# =========================================================

@app.route("/leaderboard")
def leaderboard():

    leaderboard_data = (
        db.session.query(
            User.username,
            Score.subject,
            Score.score,
            Score.created_at
        )
        .join(Score)
        .order_by(Score.score.desc())
        .all()
    )

    return render_template(
        "leaderboard.html",
        leaderboard=leaderboard_data
    )

# =========================================================
# MY SCORES
# =========================================================

@app.route("/my_scores")
@login_required
def my_scores():

    scores = (
        Score.query
        .filter_by(user_id=current_user.id)
        .order_by(Score.created_at.desc())
        .all()
    )

    total_quizzes = len(scores)

    best_score = max(
        [s.score for s in scores],
        default=0
    )

    average_score = (
        sum(s.score for s in scores) / total_quizzes
        if total_quizzes > 0
        else 0
    )

    return render_template(
        "my_scores.html",
        scores=scores,
        total_quizzes=total_quizzes,
        best_score=best_score,
        average_score=round(average_score, 2)
    )

# =========================================================
# ADD QUIZ
# =========================================================

@app.route("/add_quiz", methods=["GET", "POST"])
@login_required
def add_quiz():

    if request.method == "POST":

        quiz = Quiz(
            question=request.form["question"],
            option_a=request.form["a"],
            option_b=request.form["b"],
            option_c=request.form["c"],
            option_d=request.form["d"],
            correct_answer=request.form["correct"].upper()
        )

        db.session.add(quiz)
        db.session.commit()

        flash("Soru eklendi.")

        return redirect(url_for("add_quiz"))

    return render_template("add_quiz.html")

# =========================================================
# QUIZ
# =========================================================

@app.route("/quiz")
@login_required
def quiz():

    quizzes = Quiz.query.all()

    return render_template(
        "quiz.html",
        quizzes=quizzes
    )

# =========================================================
# SUBMIT QUIZ
# =========================================================

@app.route("/submit_quiz", methods=["POST"])
@login_required
def submit_quiz():

    quizzes = Quiz.query.all()

    score = 0
    results = []

    for quiz in quizzes:

        user_answer = request.form.get(
            f"question_{quiz.id}"
        )

        is_correct = (
            user_answer == quiz.correct_answer
        )

        if is_correct:
            score += 10

        results.append({
            "question": quiz.question,
            "user_answer": user_answer,
            "correct_answer": quiz.correct_answer,
            "is_correct": is_correct
        })

    new_score = Score(
        user_id=current_user.id,
        subject="Quiz",
        score=score
    )

    db.session.add(new_score)
    db.session.commit()

    return render_template(
        "quiz_result.html",
        score=score,
        results=results
    )

# =========================================================
# GENERATE QUIZ (OLLAMA)
# =========================================================

@app.route("/generate_quiz", methods=["GET", "POST"])
@login_required
def generate_quiz():

    if request.method == "POST":

        topic = request.form["topic"]

        prompt = f"""
{topic} konusunda 5 adet çoktan seçmeli soru üret.

JSON formatında dön.

SADECE JSON döndür.
"""

        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
        )

        try:

            start = result.find("[")
            end = result.rfind("]") + 1

            questions = json.loads(
                result[start:end]
            )

            for q in questions:

                quiz = Quiz(
                    question=q["question"],
                    option_a=q["a"],
                    option_b=q["b"],
                    option_c=q["c"],
                    option_d=q["d"],
                    correct_answer=q["correct"].upper()
                )

                db.session.add(quiz)

            db.session.commit()

            flash("Quiz oluşturuldu.")

            return redirect(url_for("quiz"))

        except Exception as e:
            return f"HATA: {e}"

    return render_template(
        "generate_quiz.html"
    )

# =========================================================
# AI TEACHER
# =========================================================

@app.route("/ai_teacher", methods=["GET", "POST"])
@login_required
def ai_teacher():

    answer = None

    if request.method == "POST":

        question = request.form["question"]

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": "llama3",
            "prompt": question,
            "stream": False
        }
    )

    return render_template(
        "ai_teacher.html",
        answer=answer
    )

# =========================================================
# INIT DB
# =========================================================

with app.app_context():
    db.create_all()

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    print("FLASK STARTING...")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )