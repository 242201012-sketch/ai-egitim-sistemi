from flask import Flask
import sqlite3
import os

app = Flask(__name__)

DATABASE = "database.db"


# DATABASE OLUŞTUR
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        score INTEGER DEFAULT 0,
        xp INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1
    )
    """)

    conn.commit()
    conn.close()


# XP KOLONU YOKSA EKLE
def fix_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]

    if "xp" not in columns:
        cursor.execute(
            "ALTER TABLE users ADD COLUMN xp INTEGER DEFAULT 0"
        )

    if "level" not in columns:
        cursor.execute(
            "ALTER TABLE users ADD COLUMN level INTEGER DEFAULT 1"
        )

    conn.commit()
    conn.close()


@app.route("/")
def home():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # KULLANICI VAR MI?
    cursor.execute("SELECT * FROM users LIMIT 1")
    user = cursor.fetchone()

    # YOKSA OLUŞTUR
    if user is None:
        cursor.execute("""
        INSERT INTO users (username, score, xp, level)
        VALUES (?, ?, ?, ?)
        """, ("Efe", 0, 0, 1))

        conn.commit()

        cursor.execute("SELECT * FROM users LIMIT 1")
        user = cursor.fetchone()

    username = user[1]
    score = user[2]
    xp = user[3]
    level = user[4]

    conn.close()

    return f"""
    <h1>AI Eğitim Sistemi</h1>

    <h2>Kullanıcı: {username}</h2>

    <h3>Score: {score}</h3>

    <h3>XP: {xp}</h3>

    <h3>Level: {level}</h3>

    <br>

    <a href='/addxp'>
        <button>+50 XP</button>
    </a>
    """


@app.route("/addxp")
def add_xp():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET xp = xp + 50
    """)

    # LEVEL SISTEMI
    cursor.execute("""
    UPDATE users
    SET level = (xp / 100) + 1
    """)

    conn.commit()
    conn.close()

    return """
    <h1>50 XP Eklendi!</h1>
    <a href='/'>
        <button>Ana Sayfa</button>
    </a>
    """


if __name__ == "__main__":

    init_db()
    fix_database()

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )