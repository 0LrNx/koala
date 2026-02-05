from datetime import datetime, timedelta
from src.database.connection import cursor, conn


def get_due_reviews():
    """Récupère les révisions dues maintenant ou avant."""
    now = datetime.now().isoformat()

    cursor.execute("""
        SELECT 
            reviews.id, 
            courses.course_name, 
            reviews.stage, 
            courses.professor_name
        FROM reviews
        JOIN courses ON courses.id = reviews.course_id
        WHERE reviews.review_date <= ?
            AND reviews.sent = 0
    """, (now,))

    return cursor.fetchall()

def get_upcoming_reviews(limit=20):
    """Récupère les révisions à venir (non encore envoyées)."""
    now = datetime.now().isoformat()

    cursor.execute("""
        SELECT 
            reviews.id, 
            courses.course_name, 
            reviews.stage, 
            reviews.review_date, 
            courses.professor_name
        FROM reviews
        JOIN courses ON courses.id = reviews.course_id
        WHERE reviews.review_date > ?
            AND reviews.sent = 0
        ORDER BY reviews.review_date
        LIMIT ?
    """, (now, limit))

    return cursor.fetchall()

def get_review_stats():
    """Calcule les statistiques du système de révision."""
    
    # Statistiques de base
    cursor.execute("SELECT COUNT(*) FROM courses")
    total_courses = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM reviews WHERE sent = 1")
    completed_reviews = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM reviews WHERE sent = 0")
    pending_reviews = cursor.fetchone()[0]
    
    # Révisions dues aujourd'hui
    today = datetime.now().date().isoformat()
    tomorrow = (datetime.now().date() + timedelta(days=1)).isoformat()
    cursor.execute("""
        SELECT COUNT(*) 
        FROM reviews 
        WHERE sent = 0 
            AND DATE(review_date) >= ? 
            AND DATE(review_date) < ?
    """, (today, tomorrow))
    due_today = cursor.fetchone()[0]
    
    # Taux de réussite
    total_reviews = completed_reviews + pending_reviews
    success_rate = (completed_reviews / total_reviews * 100) if total_reviews > 0 else 0
    
    # Série actuelle (jours consécutifs avec des révisions)
    cursor.execute("""
        SELECT DATE(review_date) as review_day, COUNT(*) as count
        FROM reviews 
        WHERE sent = 1 
        GROUP BY DATE(review_date)
        ORDER BY review_day DESC
        LIMIT 30
    """)
    daily_reviews = cursor.fetchall()
    
    current_streak = _calculate_streak(daily_reviews)
    
    return {
        'total_courses': total_courses,
        'completed_reviews': completed_reviews,
        'pending_reviews': pending_reviews,
        'due_today': due_today,
        'success_rate': success_rate,
        'current_streak': current_streak
    }


def _calculate_streak(daily_reviews):
    """Calcule le nombre de jours consécutifs avec des révisions."""
    if not daily_reviews:
        return 0
    
    current_streak = 0
    yesterday = datetime.now().date() - timedelta(days=1)
    
    for day_str, _ in daily_reviews:
        day = datetime.fromisoformat(day_str).date()
        expected_day = yesterday - timedelta(days=current_streak)
        
        if day == expected_day:
            current_streak += 1
        else:
            break
    
    return current_streak

def mark_review_done(course_name):
    """Marque la prochaine révision d'un cours comme terminée."""
    now = datetime.now().isoformat()
    
    # Chercher la prochaine révision en attente
    cursor.execute("""
        SELECT r.id, r.stage, c.course_name, c.professor_name
        FROM reviews r
        JOIN courses c ON c.id = r.course_id
        WHERE LOWER(c.course_name) LIKE LOWER(?)
            AND r.sent = 0
            AND r.review_date <= ?
        ORDER BY r.review_date
        LIMIT 1
    """, (f"%{course_name}%", now))
    
    result = cursor.fetchone()
    
    if not result:
        similar_courses = _find_similar_courses(course_name)
        return _format_course_not_found_message(course_name, similar_courses)
    
    review_id, stage, course_title, professor_name = result
    
    # Marquer comme fait
    cursor.execute("UPDATE reviews SET sent = 1 WHERE id = ?", (review_id,))
    conn.commit()
    
    return True, f"✅ Révision étape {stage} marquée comme terminée !\n🔄 Prochaine révision programmée automatiquement"


def _find_similar_courses(course_name):
    """Trouve des cours similaires au nom donné."""
    cursor.execute("""
        SELECT DISTINCT c.course_name
        FROM courses c
        JOIN reviews r ON r.course_id = c.id
        WHERE LOWER(c.course_name) LIKE LOWER(?)
            AND r.sent = 0
        LIMIT 5
    """, (f"%{course_name}%",))
    
    return [row[0] for row in cursor.fetchall()]


def _format_course_not_found_message(course_name, similar_courses):
    """Formate le message d'erreur quand un cours n'est pas trouvé."""
    if similar_courses:
        similar_list = ', '.join(similar_courses[:3])
        return False, f"Aucun rappel trouvé pour '{course_name}'. Cours similaires : {similar_list}"
    else:
        return False, f"Aucun rappel en attente trouvé pour '{course_name}'"

def mark_review_sent(review_id):
    """Marque une révision comme envoyée."""
    cursor.execute("UPDATE reviews SET sent = 1 WHERE id = ?", (review_id,))
    conn.commit()


def get_all_courses():
    """Récupère tous les cours enregistrés avec leurs informations."""
    cursor.execute("""
        SELECT 
            courses.id, 
            courses.course_name, 
            courses.professor_name, 
            courses.classroom_name, 
            courses.start_time,
            COUNT(reviews.id) as total_reviews,
            SUM(CASE WHEN reviews.sent = 1 THEN 1 ELSE 0 END) as completed_reviews
        FROM courses 
        LEFT JOIN reviews ON courses.id = reviews.course_id
        GROUP BY 
            courses.id, 
            courses.course_name, 
            courses.professor_name, 
            courses.classroom_name, 
            courses.start_time
        ORDER BY courses.start_time DESC
    """)
    
    return [
        {
            'id': course_id,
            'name': course_name,
            'professor': professor_name,
            'classroom': classroom_name,
            'start_time': start_time,
            'total_reviews': total_reviews,
            'completed_reviews': completed_reviews,
            'progress': (completed_reviews / total_reviews * 100) if total_reviews > 0 else 0
        }
        for course_id, course_name, professor_name, classroom_name, start_time, total_reviews, completed_reviews 
        in cursor.fetchall()
    ]