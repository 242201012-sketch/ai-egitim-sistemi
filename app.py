from __future__ import annotations


import os
from datetime import datetime, UTC

from flask import ( # pyright: ignore[reportMissingImports]
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_sqlalchemy import SQLAlchemy # pyright: ignore[reportMissingImports]

from flask_login import ( # type: ignore
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import ( # type: ignore
    generate_password_hash,
    check_password_hash
)

from sqlalchemy.orm import ( # type: ignore
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship
)

from sqlalchemy import ( # type: ignore
    String,
    Integer,
    ForeignKey,
    DateTime
)

# =========================================================
# DATABASE BASE
# =========================================================

class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

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
# INIT DATABASE
# =========================================================

db.init_app(app)

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

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    scores: Mapped[list["Score"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:

        return f"<User {self.username}>"


class Score(db.Model):

    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    subject: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    user: Mapped["User"] = relationship(
        back_populates="scores"
    )

    def __repr__(self) -> str:

        return f"<Score {self.subject}: {self.score}>"

# =========================================================
# USER LOADER
# =========================================================

@login_manager.user_loader
def load_user(user_id: str):

    return db.session.get(User, int(user_id))

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

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        ).strip()

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

        hashed_password = generate_password_hash(
            password
        )

        new_user = User(
            username=username,
            password=hashed_password
        )

        db.session.add(new_user)

        db.session.commit()

        flash("Kayıt başarılı.")

        return redirect(
            url_for("login")
        )

    return render_template("register.html")

# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        ).strip()

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
                url_for("dashboard")
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

    return redirect(
        url_for("home")
    )

# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
@login_required
def dashboard():

    user_scores = (
        db.session.query(Score)
        .filter_by(user_id=current_user.id)
        .order_by(Score.created_at.desc())
        .all()
    )

    return render_template(
        "dashboard.html",
        scores=user_scores
    )

# =========================================================
# ADD SCORE
# =========================================================

@app.route("/add_score", methods=["POST"])
@login_required
def add_score():

    subject = request.form.get("subject", "").strip()

    score_text = request.form.get("score", "").strip()

    if not subject or not score_text:

        flash("Tüm alanları doldurun.")

        return redirect(
            url_for("dashboard")
        )

    try:

        score_value = int(score_text)

    except ValueError:

        flash("Geçerli bir sayı girin.")

        return redirect(
            url_for("dashboard")
        )

    new_score = Score(
        subject=subject,
        score=score_value,
        user_id=current_user.id
    )

    db.session.add(new_score)

    db.session.commit()

    flash("Skor başarıyla eklendi.")

    return redirect(
        url_for("dashboard")
    )

# =========================================================
# TEST DATABASE
# =========================================================

@app.route("/test_db")
def test_db():

    try:

        user_count = db.session.query(User).count()

        score_count = db.session.query(Score).count()

        return {
            "database": "connected",
            "users": user_count,
            "scores": score_count
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


