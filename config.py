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

# Pickaxe system
PICKAXES = {
    "basic": {"name": "Pioche de Base", "cost": 0, "legendary_chance": 0},
    "bronze": {"name": "Pioche de Bronze", "cost": 500, "legendary_chance": 5},
    "silver": {"name": "Pioche d'Argent", "cost": 1500, "legendary_chance": 15},
    "gold": {"name": "Pioche d'Or", "cost": 3000, "legendary_chance": 30},
    "diamond": {"name": "Pioche de Diamant", "cost": 6000, "legendary_chance": 50},
}
