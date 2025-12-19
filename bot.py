import discord
from discord.ext import commands
import os
import asyncio
from pathlib import Path

from dotenv import load_dotenv
import config


class ArcheoloBotClient(commands.Bot):
    # Client Discord personnalisé pour Archeolobot.
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = False  # Pas besoin pour les commandes slash
        super().__init__(command_prefix="!", intents=intents)
    
    async def setup_hook(self):
        # Charge les cogs au démarrage.
        cogs_path = Path("cogs")
        
        for cog_file in cogs_path.glob("*.py"):
            if cog_file.name.startswith("_"):
                continue
            
            cog_name = cog_file.stem
            try:
                await self.load_extension(f"cogs.{cog_name}")
                print(f"Cog chargé: {cog_name}")
            except Exception as e:
                print(f"Erreur lors du chargement du cog {cog_name}: {e}")


async def main():
    """Fonction principale."""
    bot = ArcheoloBotClient()
    
    @bot.event
    async def on_ready():
        # Événement de démarrage du bot.
        print(f"Bot connecté en tant que {bot.user}")
        print(f"Synchronisation des commandes slash...")
        await bot.tree.sync()
        print(f"Commandes synchronisées!")
    
    @bot.event
    async def on_app_command_error(
        interaction: discord.Interaction,
        error: discord.app_commands.AppCommandError
    ):
        # Gère les erreurs des commandes.
        print(f"Erreur: {error}")
        
        embed = discord.Embed(
            title="Une erreur s'est produite",
            description=f"{str(error)[:200]}",
            color=discord.Color.red()
        )
        
        try:
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.InteractionResponded:
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    try:
        async with bot:
            await bot.start(config.DISCORD_TOKEN)
    except asyncio.CancelledError:
        # Arrêt propre (Ctrl+C) sans stacktrace
        pass


if __name__ == "__main__":
    print("Démarrage d'Archeolobot...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Arrêt demandé, fermeture du bot...")