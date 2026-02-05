import discord
from discord.ext import tasks

from config import DISCORD_CHANNEL_ID
from src.services.scheduler import get_due_reviews, mark_review_sent
from .utils import get_study_tip


def setup_tasks(bot):
    """Configure les tâches en arrière-plan du bot"""
    
    @tasks.loop(minutes=30)
    async def reminder_loop():
        """Vérifie et envoie les rappels de révision toutes les 30 minutes"""
        
        channel = bot.get_channel(DISCORD_CHANNEL_ID)
        if not channel:
            print("❌ Channel Discord introuvable")
            return

        for review_id, course_name, stage, professor in get_due_reviews():
            embed = discord.Embed(
                title="⏰ Rappel de révision",
                description=f"📖 **{course_name}**",
                color=0xf39c12
            )
            embed.add_field(
                name="👨‍🏫 Professeur",
                value=professor,
                inline=True
            )
            embed.add_field(
                name="🔄 Étape",
                value=f"Révision #{stage}/4",
                inline=True
            )
            embed.add_field(
                name="💡 Conseil",
                value=get_study_tip(stage),
                inline=False
            )
            embed.set_footer(text="Utilisez /marquer_fait <nom_du_cours> quand c'est terminé !")
            
            await channel.send(embed=embed)
            mark_review_sent(review_id)
    
    return reminder_loop