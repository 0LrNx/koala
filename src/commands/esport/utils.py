import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


def fetch_upcoming_matches():
    """Récupère tous les matchs à venir depuis PandaScore API."""
    url = f"https://api.pandascore.co/matches/upcoming?token={os.getenv('PANDASCORE_ACCESS_TOKEN')}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        return []
    except Exception as e:
        print(f"Error fetching matches: {e}")
        return []


def fetch_running_matches():
    """Récupère tous les matchs en cours depuis PandaScore API."""
    url = f"https://api.pandascore.co/matches/running?token={os.getenv('PANDASCORE_ACCESS_TOKEN')}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        return []
    except Exception as e:
        print(f"Error fetching running matches: {e}")
        return []


def fetch_past_matches():
    """Récupère les matchs récents (dernières 24h) depuis PandaScore API."""
    url = f"https://api.pandascore.co/matches/past?token={os.getenv('PANDASCORE_ACCESS_TOKEN')}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        return []
    except Exception as e:
        print(f"Error fetching past matches: {e}")
        return []


def fetch_match_by_id(match_id):
    """Récupère les détails d'un match spécifique par son ID."""
    url = f"https://api.pandascore.co/matches/{match_id}?token={os.getenv('PANDASCORE_ACCESS_TOKEN')}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        return None
    except Exception as e:
        print(f"Error fetching match {match_id}: {e}")
        return None


def filter_matches_by_teams(matches, team_names):
    """
    Filtre les matchs pour ne garder que ceux où au moins une des équipes spécifiées joue.
    
    Args:
        matches: Liste des matchs
        team_names: Liste des noms d'équipes à rechercher (insensible à la casse)
    
    Returns:
        Liste des matchs filtrés
    """
    filtered = []
    team_names_lower = [name.lower() for name in team_names]
    
    for match in matches:
        if not match.get('opponents'):
            continue
            
        for opponent in match['opponents']:
            if opponent.get('opponent') and opponent['opponent'].get('name'):
                opponent_name = opponent['opponent']['name'].lower()
                if any(team_name in opponent_name for team_name in team_names_lower):
                    filtered.append(match)
                    break
    
    return filtered


def format_match_info(match):
    """
    Formate les informations d'un match pour l'affichage.
    
    Returns:
        Dictionnaire avec les informations formatées du match
    """
    # Extraction des équipes
    teams = []
    if match.get('opponents'):
        for opponent in match['opponents']:
            if opponent.get('opponent') and opponent['opponent'].get('name'):
                teams.append(opponent['opponent']['name'])
    
    team_names = " vs ".join(teams) if teams else "TBD"
    
    # Date et heure du match
    scheduled_at = match.get('scheduled_at', 'Date TBD')
    if scheduled_at != 'Date TBD':
        try:
            match_date = datetime.fromisoformat(scheduled_at.replace('Z', '+00:00'))
            formatted_date = match_date.strftime('%d/%m/%Y %H:%M UTC')
        except:
            formatted_date = scheduled_at
    else:
        formatted_date = scheduled_at
    
    # Informations sur le tournoi/série
    league_name = match.get('league', {}).get('name', 'Unknown League')
    serie_name = match.get('serie', {}).get('full_name', '')
    
    # Jeu
    videogame = match.get('videogame', {}).get('name', 'Unknown Game')
    
    # Streams
    streams = []
    if match.get('streams_list'):
        for stream in match['streams_list']:
            if stream.get('raw_url'):
                streams.append(stream['raw_url'])
    
    return {
        'name': match.get('name', team_names),
        'teams': team_names,
        'date': formatted_date,
        'league': league_name,
        'serie': serie_name,
        'game': videogame,
        'streams': streams,
        'status': match.get('status', 'upcoming')
    }


def create_match_embed(match_info):
    """Crée un embed Discord pour un match."""
    import discord
    
    embed = discord.Embed(
        title=f"🎮 {match_info['teams']}",
        description=f"**{match_info['game']}**",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="📅 Date", value=match_info['date'], inline=False)
    embed.add_field(name="🏆 Compétition", value=match_info['league'], inline=True)
    
    if match_info['serie']:
        embed.add_field(name="📊 Série", value=match_info['serie'], inline=True)
    
    if match_info['streams']:
        streams_text = "\n".join(match_info['streams'][:3])  # Limiter à 3 streams
        embed.add_field(name="📺 Streams", value=streams_text, inline=False)
    
    return embed


def create_upcoming_match_notification_embed(match_info):
    """Crée un embed Discord pour notifier d'un match à venir."""
    import discord
    
    embed = discord.Embed(
        title=f"⚠️ Match à venir !",
        description=f"**{match_info['teams']}**\n{match_info['game']}",
        color=discord.Color.gold()
    )
    
    embed.add_field(name="📅 Début du match", value=match_info['date'], inline=False)
    embed.add_field(name="🏆 Compétition", value=match_info['league'], inline=True)
    
    if match_info['serie']:
        embed.add_field(name="📊 Série", value=match_info['serie'], inline=True)
    
    if match_info['streams']:
        streams_text = "\n".join(match_info['streams'][:3])
        embed.add_field(name="📺 Streams", value=streams_text, inline=False)
    
    return embed


def create_result_embed(match_info, result_info):
    """Crée un embed Discord pour afficher le résultat d'un match."""
    import discord
    
    # Déterminer le gagnant pour la couleur
    color = discord.Color.green() if result_info['winner'] else discord.Color.red()
    
    embed = discord.Embed(
        title=f"🏁 Match terminé !",
        description=f"**{match_info['teams']}**\n{match_info['game']}",
        color=color
    )
    
    embed.add_field(name="🏆 Compétition", value=match_info['league'], inline=True)
    
    if match_info['serie']:
        embed.add_field(name="📊 Série", value=match_info['serie'], inline=True)
    
    # Score
    if result_info['score']:
        embed.add_field(name="📊 Score", value=result_info['score'], inline=False)
    
    # Gagnant
    if result_info['winner']:
        embed.add_field(name="🎉 Vainqueur", value=result_info['winner'], inline=False)
    
    return embed


def extract_match_result(match):
    """
    Extrait le résultat d'un match terminé.
    
    Returns:
        Dictionnaire avec winner, score, et status
    """
    result = {
        'winner': None,
        'score': None,
        'status': match.get('status', 'unknown')
    }
    
    # Trouver le gagnant
    if match.get('winner'):
        result['winner'] = match['winner'].get('name', 'Unknown')
    
    # Construire le score
    if match.get('results'):
        scores = []
        for res in match['results']:
            team_name = res.get('team_id', 'Team')
            score = res.get('score', 0)
            scores.append(f"{score}")
        
        # Associer aux équipes
        if match.get('opponents') and len(match['opponents']) >= 2:
            team1 = match['opponents'][0].get('opponent', {}).get('name', 'Team 1')
            team2 = match['opponents'][1].get('opponent', {}).get('name', 'Team 2')
            
            if len(scores) >= 2:
                result['score'] = f"{team1} {scores[0]} - {scores[1]} {team2}"
            else:
                result['score'] = " - ".join(scores)
        else:
            result['score'] = " - ".join(scores)
    
    return result
