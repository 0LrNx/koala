import requests
import sqlite3
from ics import Calendar
from datetime import timedelta
from src.database.connection import cursor, conn
from config import (
    ICS_URL, HEADERS, START_DATE,
    EXCLUDED_KEYWORDS, EXCLUDED_PROFESSORS, INTERVALS
)

def sync_ics():
    print("\n" + "="*60)
    print("🔄 SYNCHRONISATION ICS")
    print("="*60)
    calendar = Calendar(requests.get(ICS_URL, headers=HEADERS).text)
    print(f"📥 {len(calendar.events)} événements récupérés depuis l'ICS\n")

    added_courses = 0
    seen_courses = set()
    filtered_date = 0
    filtered_keywords = 0
    filtered_format = 0
    filtered_duplicate = 0

    for i, event in enumerate(calendar.events):
        title = event.name.strip()

        title_parts = title.split(" - ")
        classroom_name = title_parts[0].strip() if len(title_parts) > 0 else "N/A"

        uid_parts = event.uid.split("-")
        extracted_id = uid_parts[1] if len(uid_parts) > 1 else event.uid

        event_date = event.begin.date()

        if event_date < START_DATE:
            filtered_date += 1
            continue

        if any(k in title.lower() for k in EXCLUDED_KEYWORDS):
            filtered_keywords += 1
            continue

        if len(title_parts) < 3:
            filtered_format += 1
            continue
        
        course_name = title_parts[1].strip()
        professor_name = title_parts[2].strip()
        
        if professor_name.upper() in [prof.upper() for prof in EXCLUDED_PROFESSORS]:
            filtered_keywords += 1
            continue
        
        course_key = (course_name, professor_name)
        
        if course_key in seen_courses:
            filtered_duplicate += 1
            continue
        
        seen_courses.add(course_key)
        print(f"✅ {course_name} - {professor_name} (📅 {event_date})")

        try:
            cursor.execute(
                "INSERT INTO courses (classroom_name, course_name, professor_name, start_time, ics_uid) VALUES (?, ?, ?, ?, ?)",
                (classroom_name, course_name, professor_name, event.begin.isoformat(), extracted_id)
            )
            course_id = cursor.lastrowid
            added_courses += 1

            for i, days in enumerate(INTERVALS, start=1):
                review_date = event.begin + timedelta(days=days)
                cursor.execute(
                    "INSERT INTO reviews (course_id, review_date, stage) VALUES (?, ?, ?)",
                    (course_id, review_date.isoformat(), i)
                )

        except sqlite3.IntegrityError:
            pass

    conn.commit()
    
    print(f"\n" + "-"*60)
    print(f"📊 RÉSUMÉ: {added_courses} nouveaux cours ajoutés")
    
    total_filtered = filtered_date + filtered_keywords + filtered_format + filtered_duplicate
    if total_filtered > 0:
        print(f"🔍 {total_filtered} événements filtrés:")
        if filtered_date > 0:
            print(f"   📅 {filtered_date} trop anciens")
        if filtered_keywords > 0:
            print(f"   🚫 {filtered_keywords} mots-clés/professeurs exclus")
        if filtered_format > 0:
            print(f"   ❌ {filtered_format} format invalide")
        if filtered_duplicate > 0:
            print(f"   🔄 {filtered_duplicate} doublons")
    
    print("-"*60 + "\n")
    
    return added_courses

