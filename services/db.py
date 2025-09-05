import sqlite3
from datetime import date
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "spotify_data.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    return conn


def create_tables():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Criação da tabela users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        spotify_user_id TEXT NOT NULL,
        access_token TEXT NOT NULL,
        refresh_token TEXT NOT NULL,
        token_expiry INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS top_tracks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        track_data TEXT NOT NULL,
        collected_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS top_artists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        artist_data TEXT NOT NULL,
        collected_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    cursor.execute("""CREATE TABLE IF NOT EXISTS recently_played (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    spotify_user_id TEXT NOT NULL,
    track_name TEXT NOT NULL,
    duration_ms INTEGER,
    played_at TEXT NOT NULL
)"""
                   )


    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("Tabelas criadas com sucesso!")


def insert_user(spotify_user, access_token, refresh_token, token_expiry):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE spotify_user_id = ?", (spotify_user,))
    existing = cursor.fetchone()
    

    if existing:

        cursor.execute("""
        UPDATE users
        SET access_token = ?, refresh_token = ?, token_expiry = ?
        WHERE spotify_user_id = ?

    """, (access_token, refresh_token, token_expiry, spotify_user))
    else:
        cursor.execute("""
            INSERT INTO users (spotify_user_id, access_token, refresh_token, token_expiry)
            VALUES (?, ?, ?, ?)
        """, (spotify_user, access_token, refresh_token, token_expiry))


    conn.commit()
    conn.close()

def insert_toptracks(user_id, track, collected_at):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    track_json = json.dumps(track)  # transforma dict em string
    track_id = track["id"]

    cursor.execute("""
        INSERT INTO top_tracks(user_id, track_data, collected_at, track_id)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id, track_id) 
        DO UPDATE SET track_data = excluded.track_data,
            collected_at = excluded.collected_at
    """, (user_id, track_json, collected_at, track_id))

    conn.commit()
    conn.close()

def insert_topartists(user_id, artist, collected_at):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    artist_id = artist["id"]
    artist_json = json.dumps(artist)
    
    cursor.execute("""
        INSERT INTO top_artists(user_id, artist_data, collected_at) 
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, artist_data)
        DO UPDATE SET collected_at = excluded.collected_at
        """,
        (user_id, artist_json, collected_at)
    )
    
    conn.commit()
    conn.close()

def get_user_tokens(spotify_user):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT access_token, refresh_token, token_expiry FROM users
        WHERE spotify_user_id = ?
    """, (spotify_user,))
    row = cursor.fetchone()
    conn.close()
    result = dict(row) if row else None
    
    return result

def update_user_token(spotify_user, access_token, token_expiry):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET access_token = ?, token_expiry = ?
        WHERE spotify_user_id = ?
    """, (access_token, token_expiry, spotify_user))
    conn.commit()
    conn.close()

def track_exists_today(user_id, track_name, dia):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 1 from top_tracks
        WHERE user_id = ?
                   AND track_name = ?
                   AND date(collected_at) = ?
                   LIMIT 1
    """, (user_id, track_name, dia))

    result = cursor.fetchone()
    conn.close()
    return result is not None

def insert_recently_played(spotify_user, track):
    conn = get_db_connection()
    cursor = conn.cursor()
   
    cursor.execute("""
        SELECT 1 from recently_played
        WHERE spotify_user_id = ?
            AND track_name = ?
            AND played_at = ?
        LIMIT 1

""", (spotify_user, track["name"], track["played_at"]))
    
    if cursor.fetchone() is None:
        cursor.execute("""
            INSERT INTO recently_played (spotify_user_id, track_name, duration_ms, played_at)
            VALUES (?, ?, ?, ?)
        """, (spotify_user, track["name"], track["duration_ms"], track["played_at"]))

    conn.commit()
    conn.close()

def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT spotify_user_id FROM users")
    rows = cursor.fetchall()
    conn.close()
    return[row["spotify_user_id"]for row in rows]

