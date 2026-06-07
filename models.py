from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model, UserMixin):
    query = None
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

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
        default=lambda: datetime.now(timezone.utc)
    )

    scores = db.relationship(
        "Score",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Score(db.Model):
    query = None
    __tablename__ = "scores"

    id = db.Column(db.Integer, primary_key=True)

    subject = db.Column(
        db.String(100),
        nullable=False
    )

    score = db.Column(
        db.Integer,
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


class Quiz(db.Model):
    __tablename__ = "quizzes"

    id = db.Column(db.Integer, primary_key=True)

    question = db.Column(
        db.Text,
        nullable=False
    )

    option_a = db.Column(
        db.String(255),
        nullable=False
    )

    option_b = db.Column(
        db.String(255),
        nullable=False
    )

    option_c = db.Column(
        db.String(255),
        nullable=False
    )

    option_d = db.Column(
        db.String(255),
        nullable=False
    )

    correct_answer = db.Column(
        db.String(1),
        nullable=False
    )