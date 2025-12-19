import discord
from discord import app_commands
from discord.ext import commands

from database.db_manager import DatabaseManager
from utils.helpers import create_embed


class PlayerCog(commands.Cog):
    #Commandes liées au profil du joueur.
    
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
    
    @app_commands.command(name="profile", description="Affiche votre profil d'archéologue")
    async def profile(self, interaction: discord.Interaction):
        #Affiche le profil de l'utilisateur.
        archaeologist = self._get_or_create_archaeologist(interaction)
        
        embed = create_embed(
            title=f"📜 Profil de {archaeologist.username}",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Niveau", value=str(archaeologist.level), inline=True)
        embed.add_field(name="Expérience", value=f"{archaeologist.experience} XP", inline=True)
        embed.add_field(name="Pièces", value=f"💰 {archaeologist.coins}", inline=True)
        embed.add_field(
            name="Artefacts découverts",
            value=str(len(archaeologist.artifacts)),
            inline=True
        )
        embed.add_field(
            name="Fouilles totales",
            value=str(archaeologist.total_excavations),
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="level", description="Affiche votre niveau et progression d'XP")
    async def level(self, interaction: discord.Interaction):
        #Affiche le niveau et la progression XP du joueur.
        archaeologist = self._get_or_create_archaeologist(interaction)
        xp_needed = archaeologist.level * 100
        embed = create_embed(
            title=f"🎯 Niveau de {archaeologist.username}",
            description=(
                f"Niveau actuel: **{archaeologist.level}**\n"
                f"XP: **{archaeologist.experience}/{xp_needed}**"
            ),
            color=discord.Color.green()
        )
        embed.add_field(name="Pièces", value=f"💰 {archaeologist.coins}", inline=True)
        embed.add_field(name="Artefacts", value=str(len(archaeologist.artifacts)), inline=True)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    #Charge le cog.
    await bot.add_cog(PlayerCog(bot))
