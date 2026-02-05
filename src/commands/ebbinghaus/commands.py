import discord
from discord.ext import commands

from src.services.scheduler import (
    get_all_courses, get_upcoming_reviews, get_review_stats, mark_review_done
)
from .utils import create_course_embed, chunk_courses


async def clear_messages(interaction: discord.Interaction, amount: int = 10):
    """Supprime un nombre spécifié de messages (par défaut 10, max 100)"""
    
    print(f"🗑️ Commande /clear utilisée par {interaction.user.name} - amount: {amount}")
    
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ Vous n'avez pas la permission de gérer les messages.", ephemeral=True)
        print("❌ Permission refusée")
        return
    
    if amount > 100:
        amount = 100
    elif amount < 1:
        amount = 1
    
    try:
        await interaction.response.send_message(f"🔄 Suppression de {amount} message(s) en cours...", ephemeral=False)
        
        deleted = await interaction.channel.purge(limit=amount)
        print(f"✅ {len(deleted)} messages supprimés")
        
        confirmation = await interaction.channel.send(f"🗑️ {len(deleted)} message(s) supprimé(s) par {interaction.user.mention}")
        await confirmation.delete(delay=5)
        
    except discord.Forbidden:
        await interaction.edit_original_response(content="❌ Le bot n'a pas les permissions pour supprimer les messages.")
        print("❌ Bot permissions insuffisantes")
    except discord.HTTPException as e:
        await interaction.edit_original_response(content=f"❌ Erreur lors de la suppression: {str(e)}")
        print(f"❌ Erreur HTTP: {e}")
    except Exception as e:
        await interaction.edit_original_response(content=f"❌ Erreur inattendue: {str(e)}")
        print(f"❌ Erreur inattendue: {e}")


async def show_courses(interaction: discord.Interaction):
    """Affiche la liste complète des cours avec leurs statistiques"""
    
    courses = get_all_courses()
    
    if not courses:
        embed = discord.Embed(
            title="📚 Cours enregistrés",
            description="❌ Aucun cours trouvé dans le système.",
            color=0xe74c3c
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Créer plusieurs embeds si nécessaire (limite Discord : 25 champs par embed)
    embeds = []
    course_chunks = chunk_courses(courses)
    
    for i, chunk in enumerate(course_chunks):
        embed = discord.Embed(
            title=f"📚 Cours enregistrés",
            color=0x3498db,
            description=f"**{len(courses)}** cours dans votre système de révision\n\u200b"
        )
        
        for course in chunk:
            field_data = create_course_embed(course)
            embed.add_field(**field_data)
        
        # Footer avec navigation si plusieurs pages
        if len(course_chunks) > 1:
            embed.set_footer(text=f"📄 Page {i + 1}/{len(course_chunks)}")
        
        embeds.append(embed)
    
    # Envoyer le premier embed
    await interaction.response.send_message(embed=embeds[0], ephemeral=True)
    
    # Envoyer les embeds suivants si nécessaire
    for embed in embeds[1:]:
        await interaction.followup.send(embed=embed, ephemeral=True)


async def show_reminders(interaction: discord.Interaction):
    """Affiche la liste des rappels à venir"""
    
    upcoming = get_upcoming_reviews()
    
    if not upcoming:
        embed = discord.Embed(
            title="📅 Rappels de révision",
            description="✅ Aucun rappel en attente !",
            color=0x00ff00
        )
    else:
        embed = discord.Embed(
            title="📅 Rappels de révision à venir",
            color=0x3498db
        )
        
        for i, (review_id, title, stage, review_date) in enumerate(upcoming[:10]):  # Limiter à 10
            embed.add_field(
                name=f"📘 {title}",
                value=f"🔄 Étape {stage} • 📅 {review_date}",
                inline=False
            )
        
        if len(upcoming) > 10:
            embed.set_footer(text=f"... et {len(upcoming) - 10} autres rappels")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


async def show_stats(interaction: discord.Interaction):
    """Affiche les statistiques du système de révision"""
    
    stats = get_review_stats()
    
    embed = discord.Embed(
        title="📊 Statistiques de révision",
        color=0xe74c3c
    )
    
    embed.add_field(
        name="📚 Cours total",
        value=f"{stats['total_courses']}",
        inline=True
    )
    embed.add_field(
        name="✅ Révisions terminées",
        value=f"{stats['completed_reviews']}",
        inline=True
    )
    embed.add_field(
        name="⏳ Révisions en attente",
        value=f"{stats['pending_reviews']}",
        inline=True
    )
    embed.add_field(
        name="🔥 Série actuelle",
        value=f"{stats['current_streak']} jours",
        inline=True
    )
    embed.add_field(
        name="🎯 Taux de réussite",
        value=f"{stats['success_rate']:.1f}%",
        inline=True
    )
    embed.add_field(
        name="📈 Prochaines 24h",
        value=f"{stats['due_today']} rappels",
        inline=True
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


async def mark_done(interaction: discord.Interaction, cours: str):
    """Marque une révision comme terminée"""
    
    success, message = mark_review_done(cours)
    
    if success:
        embed = discord.Embed(
            title="✅ Révision terminée !",
            description=f"📘 **{cours}**\n{message}",
            color=0x00ff00
        )
    else:
        embed = discord.Embed(
            title="❌ Erreur",
            description=message,
            color=0xe74c3c
        )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


def setup_commands(bot):
    """Configure toutes les commandes slash du bot"""
    
    @bot.tree.command(name="clear", description="Supprime un nombre spécifié de messages")
    @discord.app_commands.describe(amount="Nombre de messages à supprimer (1-100, défaut: 10)")
    async def clear_command(interaction: discord.Interaction, amount: int = 10):
        await clear_messages(interaction, amount)

    @bot.tree.command(name="cours", description="Affiche tous les cours enregistrés dans le système")
    async def courses_command(interaction: discord.Interaction):
        await show_courses(interaction)

    @bot.tree.command(name="rappels", description="Affiche tous les rappels de révision à venir")
    async def reminders_command(interaction: discord.Interaction):
        await show_reminders(interaction)

    @bot.tree.command(name="stats", description="Affiche les statistiques de révision")
    async def stats_command(interaction: discord.Interaction):
        await show_stats(interaction)

    @bot.tree.command(name="marquer_fait", description="Marque un rappel de révision comme terminé")
    @discord.app_commands.describe(cours="Nom du cours à marquer comme fait")
    async def mark_done_command(interaction: discord.Interaction, cours: str):
        await mark_done(interaction, cours)