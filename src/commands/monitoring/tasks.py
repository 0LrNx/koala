"""Tâches périodiques pour le monitoring RSS des flux de sécurité"""
import discord
from discord.ext import tasks

from config import MONITORING_CHANNEL_ID, RSS_FEEDS
from .monitoring import (
    load_sent_articles,
    save_sent_article,
    parse_rss_feed,
    create_article_embed
)


def setup_tasks(bot):
    """Configure les tâches en arrière-plan pour le monitoring RSS"""
    
    @tasks.loop(hours=2)
    async def monitoring_loop():
        """Vérifie les flux RSS et envoie les nouveaux articles dans le channel dédié"""
        
        channel = bot.get_channel(MONITORING_CHANNEL_ID)
        if not channel:
            print("❌ Channel de monitoring introuvable")
            return

        print("🔍 Début de la vérification des flux RSS...")
        sent_articles = load_sent_articles()
        total_new_articles = 0

        for rss_url in RSS_FEEDS:
            articles = parse_rss_feed(rss_url)
            
            for title, link, description, pub_date in articles:
                # Vérifier si l'article a déjà été envoyé
                if link in sent_articles:
                    print(f"⏭️ Article déjà envoyé : {title}")
                    continue
                
                try:
                    # Créer l'embed Discord
                    embed = create_article_embed(title, link, description, pub_date)
                    
                    # Envoyer le message
                    await channel.send(embed=embed)
                    
                    # Sauvegarder l'article comme envoyé
                    save_sent_article(link)
                    total_new_articles += 1
                    print(f"✅ Article envoyé : {title}")
                    
                except Exception as e:
                    print(f"❌ Erreur lors de l'envoi de l'article '{title}': {e}")

        if total_new_articles > 0:
            print(f"✅ {total_new_articles} nouvel(aux) article(s) envoyé(s)")
        else:
            print("ℹ️ Aucun nouvel article à envoyer")
    
    @monitoring_loop.before_loop
    async def before_monitoring():
        """Attend que le bot soit prêt avant de démarrer la boucle"""
        await bot.wait_until_ready()
        print("🔔 Tâche de monitoring RSS démarrée")
    
    return monitoring_loop
