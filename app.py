import datetime
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

# =========================================================
# APP
# =========================================================

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


# =========================================================
# INIT DATABASE
# =========================================================

def init_db():

    conn = get_db()

    cursor = conn.cursor()

    # USERS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT UNIQUE,

        password TEXT,

        xp INTEGER DEFAULT 0,

        level INTEGER DEFAULT 1,

        coins INTEGER DEFAULT 0
    )
    """)

    # INVENTORY

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        item_name TEXT,

        quantity INTEGER DEFAULT 1
    )
    """)

    conn.commit()

    conn.close()


init_db()


# =========================================================
# ACHIEVEMENT SYSTEM
# =========================================================

def init_achievement_system():

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS achievements(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        title TEXT,

        description TEXT,

        reward INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_achievements(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        achievement_id INTEGER
    )
    """)

    conn.commit()

    cursor.execute(
        "SELECT * FROM achievements"
    )

    achievements = cursor.fetchall()

    if len(achievements) == 0:

        default_achievements = [

            (
                "First Login",
                "İlk giriş yapıldı",
                50
            ),

            (
                "Level 5",
                "Level 5 oldun",
                250
            ),

            (
                "XP Master",
                "500 XP kazandın",
                500
            ),

            (
                "Boss Slayer",
                "Boss savaşı tamamlandı",
                300
            ),

            (
                "Rich Player",
                "1000 coin toplandı",
                400
            )

        ]

        cursor.executemany(
            """
            INSERT INTO achievements
            (
                title,
                description,
                reward
            )
            VALUES (?, ?, ?)
            """,
            default_achievements
        )

    conn.commit()

    conn.close()


init_achievement_system()


# =========================================================
# DAILY STREAK SYSTEM
# =========================================================

def init_streak_system():

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_streaks(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER UNIQUE,

        streak INTEGER DEFAULT 0,

        last_claim TEXT
    )
    """)

    conn.commit()

    conn.close()


init_streak_system()


# =========================================================
# XP SYSTEM
# =========================================================

def add_xp(user_id, amount):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE id=?
        """,
        (user_id,)
    )

    user = cursor.fetchone()

    if user is None:

        conn.close()

        return

    new_xp = user["xp"] + amount

    new_level = (new_xp // 100) + 1

    cursor.execute(
        """
        UPDATE users
        SET xp=?,
            level=?
        WHERE id=?
        """,
        (
            new_xp,
            new_level,
            user_id
        )
    )

    conn.commit()

    conn.close()

    check_achievements(user_id)


# =========================================================
# COIN SYSTEM
# =========================================================

def add_coins(user_id, amount):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users
        SET coins = coins + ?
        WHERE id=?
        """,
        (
            amount,
            user_id
        )
    )

    conn.commit()

    conn.close()


# =========================================================
# RANK SYSTEM
# =========================================================

def get_rank(level):

    if level >= 100:

        return {
            "name": "🌌 UNIVERSAL GOD",
            "color": "#ff0000"
        }

    elif level >= 75:

        return {
            "name": "👑 AI LEGEND",
            "color": "#ff9900"
        }

    elif level >= 50:

        return {
            "name": "💎 MASTER",
            "color": "#00ffff"
        }

    elif level >= 35:

        return {
            "name": "🔥 DIAMOND",
            "color": "#00aaff"
        }

    elif level >= 25:

        return {
            "name": "🥇 GOLD",
            "color": "#ffd700"
        }

    elif level >= 15:

        return {
            "name": "🥈 SILVER",
            "color": "#c0c0c0"
        }

    elif level >= 5:

        return {
            "name": "🥉 BRONZE",
            "color": "#cd7f32"
        }

    else:

        return {
            "name": "👶 BEGINNER",
            "color": "#ffffff"
        }


# =========================================================
# ACHIEVEMENT HELPERS
# =========================================================

def has_achievement(user_id, achievement_title):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT ua.id
        FROM user_achievements ua

        JOIN achievements a
        ON ua.achievement_id = a.id

        WHERE ua.user_id=? AND a.title=?
        """,
        (
            user_id,
            achievement_title
        )
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None


def give_achievement(user_id, achievement_title):

    if has_achievement(user_id, achievement_title):

        return

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM achievements
        WHERE title=?
        """,
        (achievement_title,)
    )

    achievement = cursor.fetchone()

    if achievement is None:

        conn.close()

        return

    cursor.execute(
        """
        INSERT INTO user_achievements
        (
            user_id,
            achievement_id
        )
        VALUES (?, ?)
        """,
        (
            user_id,
            achievement["id"]
        )
    )

    cursor.execute(
        """
        UPDATE users
        SET coins = coins + ?
        WHERE id=?
        """,
        (
            achievement["reward"],
            user_id
        )
    )

    conn.commit()

    conn.close()


def check_achievements(user_id):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE id=?
        """,
        (user_id,)
    )

    user = cursor.fetchone()

    conn.close()

    if user is None:

        return

    if user["level"] >= 5:

        give_achievement(
            user_id,
            "Level 5"
        )

    if user["xp"] >= 500:

        give_achievement(
            user_id,
            "XP Master"
        )

    if user["coins"] >= 1000:

        give_achievement(
            user_id,
            "Rich Player"
        )


# =========================================================
# STREAK FUNCTIONS
# =========================================================

def create_user_streak(user_id):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO daily_streaks
        (
            user_id,
            streak,
            last_claim
        )
        VALUES (?, ?, ?)
        """,
        (
            user_id,
            0,
            ""
        )
    )

    conn.commit()

    conn.close()


def get_streak(user_id):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM daily_streaks
        WHERE user_id=?
        """,
        (user_id,)
    )

    streak = cursor.fetchone()

    conn.close()

    return streak


# =========================================================
# ROUTES
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        conn = get_db()

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO users
            (
                username,
                password
            )
            VALUES (?, ?)
            """,
            (
                username,
                hashed_password
            )
        )

        conn.commit()

        new_user_id = cursor.lastrowid

        create_user_streak(new_user_id)

       
        # =========================================================
        # REGISTER İÇİNE EKLE
        # create_user_streak ALTINA
        # =========================================================

        create_player_stats(
            new_user_id
        )


        give_achievement(
            new_user_id,
            "First Login"
        )

        conn.close()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        conn = get_db()

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM users
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

            session["user_id"] = user["id"]

            return redirect("/")

        return "Hatalı giriş"

    return render_template("login.html")


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


@app.route("/boss_attack", methods=["POST"])
def boss_attack():

    if "user_id" not in session:

        return redirect("/login")

    add_xp(
        session["user_id"],
        50
    )

    add_coins(
        session["user_id"],
        25
    )

    give_achievement(
        session["user_id"],
        "Boss Slayer"
    )

    return redirect("/profile")


@app.route("/profile")
def profile():

    if "user_id" not in session:

        return redirect("/login")

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

    cursor.execute(
        """
        SELECT *
        FROM inventory
        WHERE user_id=?
        """,
        (session["user_id"],)
    )

    inventory = cursor.fetchall()

    cursor.execute(
        """
        SELECT
            a.title,
            a.description,
            a.reward

        FROM user_achievements ua

        JOIN achievements a
        ON ua.achievement_id = a.id

        WHERE ua.user_id=?
        """,
        (session["user_id"],)
    )

    achievements = cursor.fetchall()

    rank_data = get_rank(
        user["level"]
    )

    rank = rank_data["name"]

    rank_color = rank_data["color"]

    streak = get_streak(
        session["user_id"]
    )

    conn.close()

    return render_template(
        "profile.html",
        user=user,
        inventory=inventory,
        achievements=achievements,
        rank=rank,
        rank_color=rank_color,
        streak=streak
    )

# =========================================================
# PVP BATTLE SYSTEM
# app.py içine TAM ENTEGRE EKLE
# =========================================================

import random


# =========================================================
# PVP TABLE
# =========================================================

def init_pvp_system():

    conn = get_db()

    cursor = conn.cursor()

    # PLAYER STATS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS player_stats(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER UNIQUE,

        hp INTEGER DEFAULT 100,

        attack INTEGER DEFAULT 10,

        defense INTEGER DEFAULT 5,

        wins INTEGER DEFAULT 0,

        losses INTEGER DEFAULT 0
    )
    """)

    # BATTLE HISTORY

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS battle_history(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        attacker_id INTEGER,

        defender_id INTEGER,

        winner_id INTEGER,

        damage INTEGER,

        created_at TEXT
    )
    """)

    conn.commit()

    conn.close()


init_pvp_system()


# =========================================================
# CREATE PLAYER STATS
# register() ile uyumlu
# =========================================================

def create_player_stats(user_id):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO player_stats
        (
            user_id,
            hp,
            attack,
            defense,
            wins,
            losses
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            100,
            10,
            5,
            0,
            0
        )
    )

    conn.commit()

    conn.close()


# =========================================================
# GET PLAYER STATS
# =========================================================

def get_player_stats(user_id):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM player_stats
        WHERE user_id=?
        """,
        (user_id,)
    )

    stats = cursor.fetchone()

    conn.close()

    return stats


# =========================================================
# PVP ENGINE
# =========================================================

def process_pvp_battle(attacker_id, defender_id):

    conn = get_db()

    cursor = conn.cursor()

    # ATTACKER

    cursor.execute(
        """
        SELECT *
        FROM player_stats
        WHERE user_id=?
        """,
        (attacker_id,)
    )

    attacker_stats = cursor.fetchone()

    # DEFENDER

    cursor.execute(
        """
        SELECT *
        FROM player_stats
        WHERE user_id=?
        """,
        (defender_id,)
    )

    defender_stats = cursor.fetchone()

    if attacker_stats is None or defender_stats is None:

        conn.close()

        return {
            "success": False,
            "message": "Oyuncu stats bulunamadı."
        }

    # DAMAGE SYSTEM

    base_damage = random.randint(
        attacker_stats["attack"],
        attacker_stats["attack"] + 15
    )

    damage = max(
        1,
        base_damage - defender_stats["defense"]
    )

    # CRITICAL HIT

    critical = False

    if random.randint(1, 100) <= 20:

        damage *= 2

        critical = True

    # NEW HP

    new_hp = defender_stats["hp"] - damage

    # =====================================================
    # PLAYER DEAD
    # =====================================================

    if new_hp <= 0:

        new_hp = 100

        winner_id = attacker_id

        # WIN

        cursor.execute(
            """
            UPDATE player_stats
            SET wins = wins + 1
            WHERE user_id=?
            """,
            (attacker_id,)
        )

        # LOSS

        cursor.execute(
            """
            UPDATE player_stats
            SET losses = losses + 1
            WHERE user_id=?
            """,
            (defender_id,)
        )

        # REWARD

        add_xp(attacker_id, 100)

        add_coins(attacker_id, 150)

    else:

        winner_id = 0

    # UPDATE HP

    cursor.execute(
        """
        UPDATE player_stats
        SET hp=?
        WHERE user_id=?
        """,
        (
            new_hp,
            defender_id
        )
    )

    # BATTLE LOG

    cursor.execute(
        """
        INSERT INTO battle_history
        (
            attacker_id,
            defender_id,
            winner_id,
            damage,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            attacker_id,
            defender_id,
            winner_id,
            damage,
            datetime.utcnow().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
    )

    conn.commit()

    conn.close()

    return {
        "success": True,
        "damage": damage,
        "critical": critical,
        "remaining_hp": new_hp,
        "winner_id": winner_id
    }


# =========================================================
# PVP PAGE
# =========================================================

@app.route("/pvp")
def pvp():

    if "user_id" not in session:

        return redirect("/login")

    conn = get_db()

    cursor = conn.cursor()

    # PLAYERS

    cursor.execute(
        """
        SELECT
            users.id,
            users.username,
            users.level,
            player_stats.hp,
            player_stats.attack,
            player_stats.defense,
            player_stats.wins,
            player_stats.losses

        FROM users

        JOIN player_stats
        ON users.id = player_stats.user_id

        WHERE users.id != ?
        """,
        (session["user_id"],)
    )

    players = cursor.fetchall()

    # CURRENT USER STATS

    cursor.execute(
        """
        SELECT *
        FROM player_stats
        WHERE user_id=?
        """,
        (session["user_id"],)
    )

    my_stats = cursor.fetchone()

    conn.close()

    return render_template(
        "pvp.html",
        players=players,
        my_stats=my_stats
    )


# =========================================================
# ATTACK PLAYER
# =========================================================

@app.route("/attack/<int:defender_id>", methods=["POST"])
def attack_player(defender_id):

    if "user_id" not in session:

        return redirect("/login")

    result = process_pvp_battle(
        session["user_id"],
        defender_id
    )

    return render_template(
        "battle_result.html",
        result=result
    )




if __name__ == "__main__":

    app.run(debug=True)

