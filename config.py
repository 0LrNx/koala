from datetime import date
from dotenv import load_dotenv
import os

load_dotenv()

ICS_URL = os.getenv('ICS_URL')
HEADERS = {"User-Agent": "Mozilla/5.0"}

START_DATE = date(2026, 2, 2)
EXCLUDED_KEYWORDS = ["entreprise", "conférence", "examen", "travail en autonomie", "ferié", "retex", "pairse"]
EXCLUDED_PROFESSORS = ["HC"]

INTERVALS = [1, 3, 7, 21]

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

MONITORING_CHANNEL_ID = int(os.getenv('MONITORING_CHANNEL_ID', os.getenv('DISCORD_CHANNEL_ID')))

RSS_FEEDS = [
    "https://www.cert.ssi.gouv.fr/feed/",
    "https://www.cert.ssi.gouv.fr/feed/scada/",
    "https://msrc.microsoft.com/blog/categories/security-research-defense/feed",
    "https://msrc.microsoft.com/blog/categories/microsoft-threat-hunting/feed",
    "https://www.infostealers.com/info-stealers-reports/feed",
    "https://www.infostealers.com/learn-info-stealers/feed",
    "https://www.infostealers.com/info-stealers-techniques/feed"
]

BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

CSHUB_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/xml, text/xml, */*"
}

SENT_ARTICLES_FILE = os.path.join(os.path.dirname(__file__), "data", "sent_articles.txt")
