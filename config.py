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
