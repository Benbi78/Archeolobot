import os
from dotenv import load_dotenv

load_dotenv()

# Discord
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN non défini dans le .env")

# Database
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "json").lower()
DATABASE_PATH = "data/database.json"

# Modes
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Archaeology settings
EXCAVATION_REWARD_MIN = 50
EXCAVATION_REWARD_MAX = 500
EXCAVATION_TIME_MINUTES = 5
RARITY_LEVELS = ["common", "uncommon", "rare", "epic", "legendary"]
