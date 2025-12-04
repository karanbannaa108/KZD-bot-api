import sqlite3

def init_db():
    conn = sqlite3.connect("db.sqlite3")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            data TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_log(action, data):
    conn = sqlite3.connect("db.sqlite3")
    cur = conn.cursor()
    cur.execute("INSERT INTO logs (action, data) VALUES (?, ?)", (action, data))
    conn.commit()
    conn.close()
