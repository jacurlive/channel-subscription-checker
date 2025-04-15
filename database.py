import sqlite3


# This function initializes the SQLite database and creates a table for storing video information.
def init_video_table():
    conn = sqlite3.connect('videos.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            file_id_or_path TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# This function insert a new video into the database.
# It takes a code and a file ID or path as parameters.
def add_video(code: str, file_id_or_path: str):
    conn = sqlite3.connect('videos.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO videos (code, file_id_or_path)
            VALUES (?, ?)
        """, (code, file_id_or_path))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


# This function retrieves a video from the database using its code.
# It returns the file ID or path associated with the code.
def get_video(code: str):
    conn = sqlite3.connect('videos.db')
    cursor = conn.cursor()
    cursor.execute("SELECT file_id_or_path FROM videos WHERE code = ?", (code,))
    result = cursor.fetchone()
    conn.close()
    return result
