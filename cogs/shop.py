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
    
    @app_commands.command(name="shop", description="Consultez la boutique de pioches")
    async def shop(self, interaction: discord.Interaction):
        """Affiche les pioches disponibles à l'achat."""
        await interaction.response.defer()
        
        archaeologist = self._get_or_create_archaeologist(interaction)
        current_pickaxe = archaeologist.pickaxe
        
        # Crée une description des pioches
        pickaxes_text = ""
        for pickaxe_key, pickaxe_info in PICKAXES.items():
            name = pickaxe_info["name"]
            cost = pickaxe_info["cost"]
            legendary_chance = pickaxe_info["legendary_chance"]
            current_marker = " ✅ (Pioche actuelle)" if pickaxe_key == current_pickaxe else ""
            
            pickaxes_text += f"**{name}** ({pickaxe_key})\n"
            pickaxes_text += f"  💰 Coût: {cost} 🪙\n"
            pickaxes_text += f"  ⭐ Chance Légendaire: {legendary_chance}%\n"
            pickaxes_text += f"  {current_marker}\n"
        
        embed = create_embed(
            title="🛒 Boutique de Pioches",
            description=pickaxes_text,
            color=discord.Colour.from_rgb(218, 165, 32)
        )
        
        embed.add_field(
            name="💰 Votre Portefeuille",
            value=f"{archaeologist.coins} 🪙",
            inline=False
        )
        
        embed.set_footer(text=f"Utilisez /buy_pickaxe <nom> pour acheter | Votre pioche: {PICKAXES[current_pickaxe]['name']}")
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="buy_pickaxe", description="Achetez une pioche")
    @app_commands.describe(pickaxe="Nom de la pioche à acheter (basic, bronze, silver, gold, diamond)")
    async def buy_pickaxe(self, interaction: discord.Interaction, pickaxe: str):
        """Achète une pioche à la boutique."""
        await interaction.response.defer()
        
        # Convertir en minuscules pour la flexibilité
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
