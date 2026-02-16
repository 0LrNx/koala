import feedparser
import discord
import os
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import requests
from bs4 import BeautifulSoup

from config import SENT_ARTICLES_FILE, BASE_HEADERS, CSHUB_HEADERS


def load_sent_articles():
    """Charge la liste des articles déjà envoyés"""
    os.makedirs(os.path.dirname(SENT_ARTICLES_FILE), exist_ok=True)
    
    if not os.path.exists(SENT_ARTICLES_FILE):
        return set()
    
    with open(SENT_ARTICLES_FILE, "r") as f:
        return set(line.strip() for line in f)


def save_sent_article(link):
    """Sauvegarde un article comme déjà envoyé"""
    os.makedirs(os.path.dirname(SENT_ARTICLES_FILE), exist_ok=True)
    
    with open(SENT_ARTICLES_FILE, "a") as f:
        f.write(link + "\n")


def is_today(pub_date):
    """Vérifie si une date de publication correspond à aujourd'hui"""
    try:
        published_date = parsedate_to_datetime(pub_date).astimezone(timezone.utc).date()
        today = datetime.now(timezone.utc).date()
        return published_date == today
    except Exception as e:
        print(f"⚠️ Erreur lors du parsing de la date: {e}")
        return False


def create_article_embed(title, link, description, pub_date):
    """Crée un embed Discord pour un article"""
    try:
        published_date = parsedate_to_datetime(pub_date).strftime('%d/%m/%Y %H:%M')
    except:
        published_date = "Date inconnue"
    
    # Tronquer la description si elle est trop longue
    if len(description) > 500:
        description = description[:497] + "..."
    
    embed = discord.Embed(
        title=title[:256],  # Discord limite à 256 caractères
        url=link,
        description=description,
        color=0xe74c3c  # Rouge pour les alertes de sécurité
    )
    embed.set_footer(text=f"📅 Publié le {published_date}")
    embed.timestamp = datetime.now(timezone.utc)
    
    return embed


def parse_rss_feed(url):
    """Parse un flux RSS et retourne les nouveaux articles du jour
    
    Returns:
        list: Liste de tuples (title, link, description, pub_date) pour les articles du jour
    """
    print(f"🔍 Traitement du flux : {url}")
    articles = []
    
    try:
        # Traitement pour Infostealers
        if "infostealers.com/" in url:
            response = requests.get(url, headers=BASE_HEADERS, timeout=10)
            if response.status_code != 200:
                print(f"❌ Erreur lors du téléchargement du flux {url} : {response.status_code}")
                return articles
            feed = feedparser.parse(response.text)
        # Traitement pour CS Hub
        elif "cshub.com/rss/articles" in url:
            response = requests.request("POST", url, headers=CSHUB_HEADERS, timeout=10)
            if response.status_code != 200:
                print(f"❌ Erreur lors du téléchargement du flux {url} : {response.status_code}")
                return articles
            soup = BeautifulSoup(response.content, "xml")
            feed = feedparser.parse(str(soup))
        else:
            feed = feedparser.parse(url)

        if feed.bozo:
            print(f"⚠️ Erreur lors de l'analyse du flux {url} : {feed.bozo_exception}")
            return articles

        for entry in feed.entries:
            title = entry.get('title', 'Sans titre')
            link = entry.get('link', '')
            description_html = entry.get('description', 'Pas de description disponible')
            description = BeautifulSoup(description_html, 'html.parser').get_text()
            pub_date = entry.get('published', None)

            if pub_date and is_today(pub_date):
                print(f"✅ Article du jour trouvé : {title}")
                articles.append((title, link, description, pub_date))
            else:
                print(f"⏭️ Article ignoré (pas d'aujourd'hui) : {title}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur réseau lors du traitement de {url}: {e}")
    except Exception as e:
        print(f"❌ Erreur inattendue lors du traitement de {url}: {e}")
    
    return articles