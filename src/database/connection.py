import sqlite3

conn = sqlite3.connect("srs.db", check_same_thread=False)
cursor = conn.cursor()

def init_db():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        classroom_name TEXT,
        course_name TEXT,
        professor_name TEXT,
        start_time TEXT,
        ics_uid TEXT UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER,
        review_date TEXT,
        stage INTEGER,
        sent INTEGER DEFAULT 0
    )
    """)

    # Migration: ajouter les colonnes manquantes si elles n'existent pas
    try:
        cursor.execute("ALTER TABLE courses ADD COLUMN course_name TEXT")
        print("✅ Colonne course_name ajoutée")
    except sqlite3.OperationalError:
        pass  # La colonne existe déjà
    
    try:
        cursor.execute("ALTER TABLE courses ADD COLUMN classroom_name TEXT")
        print("✅ Colonne classroom_name ajoutée")
    except sqlite3.OperationalError:
        pass  # La colonne existe déjà
    
    try:
        cursor.execute("ALTER TABLE courses ADD COLUMN professor_name TEXT")
        print("✅ Colonne professor_name ajoutée")
    except sqlite3.OperationalError:
        pass  # La colonne existe déjà

    # Table pour les matchs esport
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS esport_matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER UNIQUE,
        team_name TEXT,
        opponent_name TEXT,
        game TEXT,
        scheduled_at TEXT,
        status TEXT,
        notified_upcoming INTEGER DEFAULT 0,
        notified_result INTEGER DEFAULT 0,
        result TEXT
    )
    """)

    conn.commit()
