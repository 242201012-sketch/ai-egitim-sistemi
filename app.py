from flask import Flask, render_template, request, redirect, session
import sqlite3
import os


app = Flask(__name__)

app.secret_key = "SUPER_SECRET_KEY"

DATABASE = "game.db"

# =========================================================
# DATABASE
# =========================================================

def get_db():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT UNIQUE,

        password TEXT,

        score INTEGER DEFAULT 0,

        xp INTEGER DEFAULT 0,

        level INTEGER DEFAULT 1

    )
    """)

    conn.commit()

    conn.close()


init_db()

# =========================================================
# XP SYSTEM
# =========================================================

def add_xp(user_id, gained_xp):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT xp, level
        FROM users
        WHERE id=?
        """,
        (user_id,)
    )

    user = cursor.fetchone()

    if user is None:

        conn.close()

        return

    current_xp = user["xp"]

    current_level = user["level"]

    new_xp = current_xp + gained_xp

    required_xp = current_level * 100

    if new_xp >= required_xp:

        current_level += 1

    cursor.execute(
        """
        UPDATE users
        SET xp=?, level=?
        WHERE id=?
        """,
        (
            new_xp,
            current_level,
            user_id
        )
    )

    conn.commit()

    conn.close()

# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    if "user_id" not in session:

        return render_template("login.html")

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE id=?
        """,
        (session["user_id"],)
    )

    user = cursor.fetchone()

    conn.close()

    if user is None:

        session.clear()

        return redirect("/")

    xp_percent = user["xp"] % 100

    return render_template(
        "index.html",
        user=user,
        xp_percent=xp_percent
    )

# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["POST"])
def register():

    username = request.form["username"]

    password = request.form["password"]

    conn = get_db()

    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO users
            (
                username,
                password,
                score,
                xp,
                level
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                username,
                password,
                0,
                0,
                1
            )
        )

        conn.commit()

        return redirect("/")

    except Exception as e:

        return f"KAYIT HATASI: {e}"

    finally:

        conn.close()

# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]

    password = request.form["password"]

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE username=? AND password=?
        """,
        (
            username,
            password
        )
    )

    user = cursor.fetchone()

    conn.close()

    if user is None:

        return "Kullanici bulunamadi"

    session["user_id"] = user["id"]

    return redirect("/")

# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# =========================================================
# XP TEST
# =========================================================

@app.route("/gain_xp")
def gain_xp():

    if "user_id" not in session:

        return redirect("/")

    add_xp(
        session["user_id"],
        25
    )

    return redirect("/")

# =========================================================
# BOSS
# =========================================================

@app.route("/boss")
def boss():

    return """
    <h1>🔥 Boss Battle Yakında!</h1>
    """

# =========================================================
# LEADERBOARD
# =========================================================

@app.route("/leaderboard")
def leaderboard():

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
    SELECT username, xp, level
    FROM users
    ORDER BY xp DESC
    LIMIT 10
    """)

    users = cursor.fetchall()

    conn.close()

    html = """

    <h1>🏆 Leaderboard</h1>

    <hr>

    """

    for user in users:

        html += f"""
        <p>
        👤 {user['username']}
        | ⭐ Level {user['level']}
        | ⚡ {user['xp']} XP
        </p>
        """

    return html

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )

