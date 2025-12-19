import discord
from discord import app_commands
from discord.ext import commands

from database.db_manager import DatabaseManager
from config import PICKAXES
from utils.helpers import create_embed


class ShopCog(commands.Cog):
    """Commandes liées à la boutique d'équipement."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = DatabaseManager()
    
    def _get_or_create_archaeologist(self, interaction: discord.Interaction):
        """Récupère ou crée un archéologue."""
        archaeologist = self.db.get_archaeologist(interaction.user.id)
        
        if not archaeologist:
            archaeologist = self.db.create_archaeologist(
                interaction.user.id,
                interaction.user.name
            )
        
        return archaeologist
    
    @app_commands.command(name="shop", description="Achetez une pioche")
    @app_commands.describe(pickaxe="Choisissez la pioche à acheter")
    @app_commands.choices(pickaxe=[
        app_commands.Choice(name=f"{info['name']} - {info['cost']} 🪙", value=key)
        for key, info in PICKAXES.items()
    ])
    async def shop(self, interaction: discord.Interaction, pickaxe: str):
        """Achète une pioche à la boutique."""
        await interaction.response.defer()
        
        # Le pickaxe est déjà au bon format (key) grâce aux choices
        pickaxe = pickaxe.lower()
        
        success, message = self.db.buy_pickaxe(str(interaction.user.id), pickaxe)
        
        if success:
            embed = create_embed(
                title="🎉 Achat Réussi!",
                description=message,
                color=discord.Colour.green()
            )
        else:
            embed = create_embed(
                title="❌ Achat Échoué",
                description=message,
                color=discord.Colour.red()
            )
        
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    """Charge le cog Shop."""
    await bot.add_cog(ShopCog(bot))
