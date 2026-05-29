
from __future__ import annotations

import os
from datetime import datetime, UTC
from typing import Optional

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
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)

from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.exc import SQLAlchemyError

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

# =========================================================
# APP
# =========================================================

app = Flask(__name__)

# =========================================================
# CONFIG
# =========================================================

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "supersecretkey"
)

database_url = os.getenv("DATABASE_URL")

if database_url and database_url.strip() != "":

    if database_url.startswith("postgres://"):

        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url

else:

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///database.db"
    )

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# =========================================================
# DATABASE
# =========================================================

db = SQLAlchemy(app)

# =========================================================
# LOGIN MANAGER
# =========================================================

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"

login_manager.login_message = (
    "Bu sayfaya erişmek için giriş yapmalısınız."
)

# =========================================================
# MODELS
# =========================================================

class User(db.Model, UserMixin):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    def __repr__(self) -> str:

        return f"<User {self.username}>"


class Score(db.Model):

    __tablename__ = "scores"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        nullable=False
    )

    score = db.Column(
        db.Integer,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    def __repr__(self) -> str:

        return f"<Score {self.username}: {self.score}>"

# =========================================================
# USER LOADER
# =========================================================

@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:

    try:

        return db.session.get(User, int(user_id))

    except (ValueError, SQLAlchemyError):

        return None

# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    top_scores = (
        db.session.query(Score)
        .order_by(Score.score.desc())
        .limit(10)
        .all()
    )

    return render_template(
        "index.html",
        scores=top_scores
    )

# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = (
            request.form.get("username", "")
            .strip()
        )

        password = (
            request.form.get("password", "")
            .strip()
        )

        if not username or not password:

            flash("Tüm alanları doldurun.")

            return redirect(
                url_for("register")
            )

        existing_user = (
            db.session.query(User)
            .filter_by(username=username)
            .first()
        )

        if existing_user:

            flash("Bu kullanıcı adı zaten mevcut.")

            return redirect(
                url_for("register")
            )

        hashed_password = (
            generate_password_hash(password)
        )

        new_user = User(
            username=username,
            password=hashed_password
        )

        try:

            db.session.add(new_user)

            db.session.commit()

            flash("Kayıt başarılı.")

            return redirect(
                url_for("login")
            )

        except SQLAlchemyError:

            db.session.rollback()

            flash("Veritabanı hatası oluştu.")

            return redirect(
                url_for("register")
            )

    return render_template("register.html")

# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = (
            request.form.get("username", "")
            .strip()
        )

        password = (
            request.form.get("password", "")
            .strip()
        )

        if not username or not password:

            flash("Tüm alanları doldurun.")

            return redirect(
                url_for("login")
            )

        user = (
            db.session.query(User)
            .filter_by(username=username)
            .first()
        )

        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            flash("Giriş başarılı.")

            return redirect(
                url_for("home")
            )

        flash("Kullanıcı adı veya şifre yanlış.")

    return render_template("login.html")

# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Çıkış yapıldı.")

    return redirect(url_for("home"))

# =========================================================
# ADD SCORE
# =========================================================

@app.route("/add_score", methods=["POST"])
@login_required
def add_score():

    score_raw = (
        request.form.get("score", "")
        .strip()
    )

    try:

        score_value = int(score_raw)

    except ValueError:

        flash("Geçersiz skor.")

        return redirect(
            url_for("home")
        )

    new_score = Score(
        username=current_user.username,
        score=score_value
    )

    try:

        db.session.add(new_score)

        db.session.commit()

        flash("Skor kaydedildi.")

    except SQLAlchemyError:

        db.session.rollback()

        flash("Skor kaydedilemedi.")

    return redirect(url_for("home"))

# =========================================================
# TEST DATABASE
# =========================================================

@app.route("/test_db")
def test_db():

    try:

        users = (
            db.session.query(User)
            .all()
        )

        scores = (
            db.session.query(Score)
            .all()
        )

        return {
            "database": "connected",
            "users": len(users),
            "scores": len(scores)
        }

    except Exception as error:

        return {
            "database": "error",
            "message": str(error)
        }

# =========================================================
# CREATE DATABASE
# =========================================================

with app.app_context():

    db.create_all()

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
