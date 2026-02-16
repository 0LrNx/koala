import discord
from discord.ext import commands
from discord import app_commands
from .utils import (
    fetch_upcoming_matches,
    filter_matches_by_teams,
    format_match_info,
    create_match_embed
)
from src.database.connection import cursor


def setup_commands(bot):
    """Configure les commandes esport."""
    
    @bot.tree.command(name="kc_matches", description="Affiche les prochains matchs de la Karmine Corp")
    async def kc_matches(interaction: discord.Interaction):
        await interaction.response.defer()
        
        matches = fetch_upcoming_matches()
        
        if not matches:
            await interaction.followup.send("❌ Impossible de récupérer les matchs ou aucun match à venir.")
            return
        
        # Filtrer pour KC
        kc_matches = filter_matches_by_teams(matches, ["KC", "Karmine", "Karmine Corp"])
        
        if not kc_matches:
            await interaction.followup.send("Aucun match à venir pour la Karmine Corp.")
            return
        
        for match in kc_matches[:5]:
            match_info = format_match_info(match)
            embed = create_match_embed(match_info)
            await interaction.followup.send(embed=embed)
        
        if len(kc_matches) > 5:
            await interaction.followup.send(f"_... et {len(kc_matches) - 5} autre(s) match(s)_")
    
    
    @bot.tree.command(name="m8_matches", description="Affiche les prochains matchs de M8")
    async def m8_matches(interaction: discord.Interaction):
        await interaction.response.defer()
        
        matches = fetch_upcoming_matches()
        
        if not matches:
            await interaction.followup.send("❌ Impossible de récupérer les matchs ou aucun match à venir.")
            return
        
        # Filtrer pour M8
        m8_matches = filter_matches_by_teams(matches, ["M8", "M80"])
        
        if not m8_matches:
            await interaction.followup.send("Aucun match à venir pour M8.")
            return
        
        # Limiter à 5 matchs pour ne pas spam
        for match in m8_matches[:5]:
            match_info = format_match_info(match)
            embed = create_match_embed(match_info)
            await interaction.followup.send(embed=embed)
        
        if len(m8_matches) > 5:
            await interaction.followup.send(f"_... et {len(m8_matches) - 5} autre(s) match(s)_")
    
    
    @bot.tree.command(name="upcoming_matches", description="Affiche les prochains matchs de KC et M8")
    async def upcoming_matches(interaction: discord.Interaction):
        await interaction.response.defer()
        
        matches = fetch_upcoming_matches()
        
        if not matches:
            await interaction.followup.send("❌ Impossible de récupérer les matchs ou aucun match à venir.")
            return
        
        # Filtrer pour KC et M8
        team_matches = filter_matches_by_teams(matches, ["KC", "Karmine", "Karmine Corp", "M8", "M80"])
        
        if not team_matches:
            await interaction.followup.send("Aucun match à venir pour KC ou M8.")
            return
        
        await interaction.followup.send(f"📋 **{len(team_matches)} match(s) à venir pour KC et M8**\n")
        
        # Limiter à 10 matchs pour ne pas spam
        for match in team_matches[:10]:
            match_info = format_match_info(match)
            embed = create_match_embed(match_info)
            await interaction.followup.send(embed=embed)
        
        if len(team_matches) > 10:
            await interaction.followup.send(f"_... et {len(team_matches) - 10} autre(s) match(s)_")
    
    
    @bot.tree.command(name="esport_status", description="Affiche le statut du système de notifications esport")
    async def esport_status(interaction: discord.Interaction):
        await interaction.response.defer()
        
        # Compter les matchs suivis
        cursor.execute("SELECT COUNT(*) FROM esport_matches")
        total_matches = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM esport_matches WHERE notified_upcoming = 1")
        notified_upcoming = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM esport_matches WHERE notified_result = 1")
        notified_results = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM esport_matches WHERE notified_result = 0")
        pending_results = cursor.fetchone()[0]
        
        # Créer l'embed de statut
        embed = discord.Embed(
            title="📊 Statut du système de notifications esport",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="📝 Total matchs suivis", value=str(total_matches), inline=True)
        embed.add_field(name="🔔 Notifications envoyées", value=str(notified_upcoming), inline=True)
        embed.add_field(name="🏁 Résultats notifiés", value=str(notified_results), inline=True)
        embed.add_field(name="⏳ En attente de résultat", value=str(pending_results), inline=True)
        
        await interaction.followup.send(embed=embed)
