import sqlite3

conn = sqlite3.connect("movies.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS movies (
    code TEXT PRIMARY KEY,
    file_id TEXT
)
""")
conn.commit()

def add_movie(code, file_id):
    cursor.execute("INSERT OR REPLACE INTO movies VALUES (?, ?)", (code, file_id))
    conn.commit()

def get_movie(code):
    cursor.execute("SELECT file_id FROM movies WHERE code=?", (code,))
    result = cursor.fetchone()
    return result[0] if result else None

def delete_movie(code):
    cursor.execute("DELETE FROM movies WHERE code=?", (code,))
    conn.commit()

def get_all_movies():
    cursor.execute("SELECT code FROM movies")
    return [row[0] for row in cursor.fetchall()]