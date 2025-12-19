#Fonctions utilitaires pour le bot.

import random
import discord
from datetime import timedelta
import config


def get_random_artifact_name() -> str:
    #Génère un nom d'artefact aléatoire.
    prefixes = ["Ancient", "Mystical", "Golden", "Sacred", "Lost", "Hidden"]
    items = ["Amulet", "Scroll", "Sword", "Crown", "Chalice", "Tome", "Statue"]
    return f"{random.choice(prefixes)} {random.choice(items)}"


def get_random_artifact_description() -> str:
    #Génère une description d'artefact aléatoire.
    descriptions = [
        "Un objet énigmatique aux origines perdues.",
        "Gravé avec des symboles anciens indéchiffrés.",
        "Dégageant une aura mystérieuse.",
        "Rarissime et d'une grande valeur historique.",
        "Porteur de secrets d'une civilisation oubliée.",
        "D'une beauté et d'une finesse exceptionnelles.",
    ]
    return random.choice(descriptions)


def get_rarity_color(rarity: str) -> discord.Color:
    #Retourne la couleur correspondant à la rareté.
    colors = {
        "common": discord.Color.greyple(),
        "uncommon": discord.Color.green(),
        "rare": discord.Color.blue(),
        "epic": discord.Color.purple(),
        "legendary": discord.Color.gold(),
    }
    return colors.get(rarity, discord.Color.default())


def get_rarity_emoji(rarity: str) -> str:
    #Retourne l'emoji correspondant à la rareté.
    emojis = {
        "common": "⚪",
        "uncommon": "🟢",
        "rare": "🔵",
        "epic": "🟣",
        "legendary": "⭐",
    }
    return emojis.get(rarity, "❓")


def generate_excavation_reward(pickaxe: str = "basic") -> tuple[int, str]:
    #Génère une récompense aléatoire pour une fouille selon la pioche.
    legendary_chance = config.PICKAXES.get(pickaxe, {}).get("legendary_chance", 0)
    
    # Si pioche basic, pas de légendaire
    if pickaxe == "basic":
        weights = [50, 25, 15, 10, 0]
    else:
        # Réduit les autres raretés pour augmenter les chances supérieures
        base_weights = [50, 25, 15, 7, 3]
        legendary_weight = legendary_chance
        common_weight = max(0, base_weights[0] - (legendary_weight - 3))
        weights = [common_weight, base_weights[1], base_weights[2], base_weights[3], legendary_weight]
    
    rarity = random.choices(
        config.RARITY_LEVELS,
        weights=weights,
        k=1
    )[0]
    
    reward_multiplier = {
        "common": 50,
        "uncommon": 150,
        "rare": 300,
        "epic": 500,
        "legendary": 1000,
    }
    
    base_reward = reward_multiplier[rarity]
    coins = random.randint(int(base_reward * 0.8), int(base_reward * 1.2))
    
    return coins, rarity


def format_duration(minutes: int) -> str:
    #Formate une durée en minutes en format lisible.
    return str(timedelta(minutes=minutes))


def create_embed(title: str, description: str = "", color: discord.Color = None) -> discord.Embed:
    #Crée un embed Discord formaté.
    if color is None:
        color = discord.Color.blue()
    
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    return embed
