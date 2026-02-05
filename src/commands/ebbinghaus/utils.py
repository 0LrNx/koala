def get_study_tip(stage):
    """Retourne un conseil d'étude selon l'étape de révision"""
    tips = {
        1: "🔍 Relisez vos notes rapidement",
        2: "📝 Testez-vous avec des questions", 
        3: "🎯 Focalisez sur les points difficiles",
        4: "📚 Révision finale - consolidation"
    }
    return tips.get(stage, "📖 Bonne révision !")


def create_course_embed(course):
    """Crée un embed Discord pour afficher un cours avec sa progression"""
    if course['progress'] == 100:
        progress_icon = "✅"
        progress_bar = "████████████"
    elif course['progress'] >= 80:
        progress_icon = "🔥"
        progress_bar = "██████████░░"
    elif course['progress'] >= 60:
        progress_icon = "🚀"
        progress_bar = "████████░░░░"
    elif course['progress'] >= 40:
        progress_icon = "⚡"
        progress_bar = "██████░░░░░░"
    elif course['progress'] >= 20:
        progress_icon = "🌱"
        progress_bar = "████░░░░░░░░"
    else:
        progress_icon = "🆕"
        progress_bar = "░░░░░░░░░░░░"
    
    return {
        'name': f"{progress_icon} **{course['name']}**",
        'value': (f"🎓 **{course['professor']}**\n"
                 f"📊 `{progress_bar}` **{course['progress']:.0f}%**\n"
                 f"📈 {course['completed_reviews']}/{course['total_reviews']} révisions\n"
                 f"📅 Début: **{course['start_time'][:10]}**"),
        'inline': False
    }


def chunk_courses(courses, fields_per_embed=8):
    """Divise la liste des cours en chunks pour les embeds Discord"""
    return [courses[i:i + fields_per_embed] 
            for i in range(0, len(courses), fields_per_embed)]