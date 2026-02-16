import discord
from discord.ext import commands

from config import DISCORD_TOKEN
from src.database.connection import init_db
from src.services.ics_sync import sync_ics
from src.commands.ebbinghaus import setup_commands as setup_ebbinghaus_commands, setup_tasks
from src.commands.esport import setup_commands as setup_esport_commands, setup_tasks as setup_esport_tasks
from src.commands.monitoring import setup_tasks as setup_monitoring_tasks

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print("🤖 Bot connecté")

    init_db()
    # added = sync_ics()
    # print(f"📅 {added} nouveaux cours ajoutés")
    setup_ebbinghaus_commands(bot)
    setup_esport_commands(bot)
    reminder_loop = setup_tasks(bot)
    reminder_loop.start()
    esport_loop = setup_esport_tasks(bot)
    esport_loop.start()
    monitoring_loop = setup_monitoring_tasks(bot)
    monitoring_loop.start()

    try:
        synced = await bot.tree.sync()
        print(f"🔄 {len(synced)} slash command(s) synchronisée(s)")
    except Exception as e:
        print(f"❌ Erreur sync slash commands: {e}")

bot.run(DISCORD_TOKEN)