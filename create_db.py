import sqlite3


conn = sqlite3.connect("game.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    score INTEGER DEFAULT 0
)
""")

conn.commit()
conn.close()

print("game.db oluşturuldu!")

