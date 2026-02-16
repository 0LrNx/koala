from discord.ext import tasks
from datetime import datetime, timedelta
from config import DISCORD_CHANNEL_ID
from src.database.connection import cursor, conn
from .utils import (
    fetch_upcoming_matches,
    fetch_running_matches,
    fetch_past_matches,
    fetch_match_by_id,
    filter_matches_by_teams,
    format_match_info,
    create_upcoming_match_notification_embed,
    create_result_embed,
    extract_match_result
)


TRACKED_TEAMS = ["KC", "Karmine", "Karmine Corp", "Karmine Corps"]


def setup_tasks(bot):
    """Configure les tâches planifiées pour les notifications esport."""
    
    @tasks.loop(hours=1)
    async def check_matches():
        """Vérifie les matchs à venir et les résultats toutes les heures."""
        print("🔍 Vérification des matchs esport...")
        
        channel = bot.get_channel(DISCORD_CHANNEL_ID)
        if not channel:
            print(f"❌ Canal {DISCORD_CHANNEL_ID} introuvable")
            return
        
        # Partie 1 : Vérifier les matchs à venir (notification 1h avant)
        await check_upcoming_matches(channel)
        
        # Partie 2 : Vérifier les résultats des matchs en cours/terminés
        await check_match_results(channel)
    
    return check_matches


async def check_upcoming_matches(channel):
    """Vérifie les matchs à venir dans les prochaines 24h et notifie 1h avant."""
    matches = fetch_upcoming_matches()
    
    if not matches:
        return
    
    # Filtrer pour les équipes suivies
    team_matches = filter_matches_by_teams(matches, TRACKED_TEAMS)
    
    now = datetime.now()
    
    for match in team_matches:
        match_id = match.get('id')
        scheduled_at = match.get('scheduled_at')
        
        if not match_id or not scheduled_at:
            continue
        
        # Vérifier si déjà notifié
        cursor.execute(
            "SELECT notified_upcoming FROM esport_matches WHERE match_id = ?",
            (match_id,)
        )
        result = cursor.fetchone()
        
        if result and result[0] == 1:
            continue  # Déjà notifié
        
        # Calculer le temps avant le match
        try:
            match_time = datetime.fromisoformat(scheduled_at.replace('Z', '+00:00'))
            time_until_match = match_time - now.replace(tzinfo=match_time.tzinfo)
            
            # Notifier si le match est dans moins d'1h30 et plus de 30 min
            if timedelta(minutes=30) <= time_until_match <= timedelta(hours=1, minutes=30):
                # Récupérer les infos de l'équipe
                team_name = None
                opponent_name = None
                
                for opponent in match.get('opponents', []):
                    opp_data = opponent.get('opponent', {})
                    opp_name = opp_data.get('name', '')
                    
                    # Vérifier si c'est notre équipe
                    if any(team.lower() in opp_name.lower() for team in TRACKED_TEAMS):
                        team_name = opp_name
                    else:
                        opponent_name = opp_name
                
                # Sauvegarder dans la base
                cursor.execute("""
                    INSERT OR REPLACE INTO esport_matches 
                    (match_id, team_name, opponent_name, game, scheduled_at, status, notified_upcoming)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                """, (
                    match_id,
                    team_name,
                    opponent_name,
                    match.get('videogame', {}).get('name', 'Unknown'),
                    scheduled_at,
                    match.get('status', 'upcoming')
                ))
                conn.commit()
                
                # Envoyer la notification
                match_info = format_match_info(match)
                embed = create_upcoming_match_notification_embed(match_info)
                await channel.send(f"@everyone Un match de **{team_name}** commence bientôt !", embed=embed)
                print(f"✅ Notification envoyée pour le match {match_id}")
        
        except Exception as e:
            print(f"❌ Erreur lors du traitement du match {match_id}: {e}")
            continue


async def check_match_results(channel):
    """Vérifie les matchs en cours et terminés pour afficher les résultats."""
    
    # Récupérer les matchs de la BDD qui n'ont pas encore de résultat notifié
    cursor.execute("""
        SELECT match_id, team_name, opponent_name, game
        FROM esport_matches
        WHERE notified_result = 0
    """)
    
    tracked_matches = cursor.fetchall()
    
    if not tracked_matches:
        return
    
    print(f"📊 Vérification des résultats pour {len(tracked_matches)} match(s)...")
    
    for match_data in tracked_matches:
        match_id = match_data[0]
        
        # Récupérer les détails actuels du match
        match = fetch_match_by_id(match_id)
        
        if not match:
            continue
        
        status = match.get('status')
        
        # Si le match est terminé
        if status == 'finished':
            # Extraire le résultat
            result_info = extract_match_result(match)
            match_info = format_match_info(match)
            
            # Créer et envoyer l'embed
            embed = create_result_embed(match_info, result_info)
            await channel.send(f"🏁 Le match de **{match_data[1]}** est terminé !", embed=embed)
            
            # Marquer comme notifié
            cursor.execute("""
                UPDATE esport_matches
                SET notified_result = 1, status = ?, result = ?
                WHERE match_id = ?
            """, (status, result_info.get('score'), match_id))
            conn.commit()
            
            print(f"✅ Résultat notifié pour le match {match_id}")
