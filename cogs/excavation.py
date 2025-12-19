import discord
from discord import app_commands
from discord.ext import commands
import random

from database.db_manager import DatabaseManager
from utils.helpers import (
    get_random_artifact_name,
    get_random_artifact_description,
    get_rarity_emoji,
    get_rarity_color,
    generate_excavation_reward,
    create_embed,
)


class ExcavationCog(commands.Cog):
    #Commandes liées aux fouilles archéologiques.
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = DatabaseManager()
    
    def _get_or_create_archaeologist(self, interaction: discord.Interaction):
        #Récupère ou crée un archéologue.
        archaeologist = self.db.get_archaeologist(interaction.user.id)
        
        if not archaeologist:
            archaeologist = self.db.create_archaeologist(
                interaction.user.id,
                interaction.user.name
            )
        
        return archaeologist
    
    @app_commands.command(name="excavate", description="Commencez une fouille archéologique")
    async def excavate(self, interaction: discord.Interaction):
        #Lance une fouille archéologique.
        await interaction.response.defer()
        
        archaeologist = self._get_or_create_archaeologist(interaction)
        
        # Génère un artefact aléatoire avec la pioche actuelle
        coins_reward, rarity = generate_excavation_reward(archaeologist.pickaxe)
        artifact_name = get_random_artifact_name()
        artifact_desc = get_random_artifact_description()
        
        # Crée l'artefact en base de données
        artifact = self.db.create_artifact(
            name=artifact_name,
            rarity=rarity,
            description=artifact_desc,
            value=coins_reward,
            discovered_by=str(archaeologist.user_id)
        )
        
        # Met à jour les statistiques de l'archéologue
        archaeologist.add_artifact(artifact.artifact_id)
        xp_gained = random.randint(25, 75)
        leveled_up = archaeologist.add_experience(xp_gained)
        archaeologist.total_excavations += 1
        
        self.db.save_archaeologist(archaeologist)
        
        # Crée l'embed de résultat
        embed = create_embed(
            title="⛏️ Fouille réussie!",
            color=get_rarity_color(rarity)
        )
        
        embed.add_field(
            name=f"{get_rarity_emoji(rarity)} {artifact_name}",
            value=artifact_desc,
            inline=False
        )
        embed.add_field(name="Rareté", value=rarity.capitalize(), inline=True)
        embed.add_field(name="Valeur potentielle", value=f"💰 {coins_reward}", inline=True)
        embed.add_field(name="XP gagné", value=f"⭐ +{xp_gained} XP", inline=True)
        
        if leveled_up:
            embed.add_field(
                name="🎉 Montée de niveau!",
                value=f"Vous êtes maintenant niveau {archaeologist.level}",
                inline=False
            )
        
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    #Charge le cog.
    await bot.add_cog(ExcavationCog(bot))
