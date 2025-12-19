import discord
from discord import app_commands
from discord.ext import commands

from database.db_manager import DatabaseManager
from utils.helpers import (
    get_rarity_emoji,
    create_embed,
)
import config


class CollectionCog(commands.Cog):
    #Commandes liées aux collections et classements.
    
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

    @app_commands.command(name="sell", description="Vendre vos artefacts par nom ou par rareté")
    @app_commands.describe(
        artifact_name="Nom exact de l'artefact à vendre (optionnel)",
        max_rarity="Vendre tous les artefacts jusqu'à cette rareté incluse (optionnel)"
    )
    @app_commands.choices(max_rarity=[
        app_commands.Choice(name=r.capitalize(), value=r) for r in config.RARITY_LEVELS
    ])
    async def sell(
        self,
        interaction: discord.Interaction,
        artifact_name: str | None = None,
        max_rarity: app_commands.Choice[str] | None = None,
    ):
        #Vendre un artefact par nom OU tous les artefacts jusqu'à une rareté.
        await interaction.response.defer()

        archaeologist = self._get_or_create_archaeologist(interaction)

        if artifact_name:
            coins, sold_id = self.db.sell_single_artifact(archaeologist.user_id, artifact_name)
            if coins == 0:
                await interaction.followup.send(
                    embed=create_embed(
                        title="Aucune vente",
                        description=f"Aucun artefact nommé `{artifact_name}` dans votre collection.",
                        color=discord.Color.red(),
                    ),
                    ephemeral=True,
                )
                return

            await interaction.followup.send(
                embed=create_embed(
                    title="Vente effectuée",
                    description=f"Vous avez vendu **{artifact_name}** pour **💰 {coins}**.",
                    color=discord.Color.green(),
                )
            )
            return

        if max_rarity:
            coins, count = self.db.sell_artifacts_by_rarity(
                archaeologist.user_id,
                max_rarity.value,
            )
            if count == 0:
                await interaction.followup.send(
                    embed=create_embed(
                        title="Aucune vente",
                        description="Aucun artefact ne correspond à ce critère de rareté.",
                        color=discord.Color.red(),
                    ),
                    ephemeral=True,
                )
                return

            await interaction.followup.send(
                embed=create_embed(
                    title="Vente effectuée",
                    description=(
                        f"Vous avez vendu **{count}** artefact(s) pour **💰 {coins}**\n"
                        f"Critère: rareté ≤ **{max_rarity.name}**"
                    ),
                    color=discord.Color.green(),
                )
            )
            return

        await interaction.followup.send(
            embed=create_embed(
                title="Paramètres manquants",
                description="Indiquez soit un `artifact_name`, soit un `max_rarity`.",
                color=discord.Color.orange(),
            ),
            ephemeral=True,
        )
    
    @app_commands.command(name="collection", description="Affiche vos artefacts découverts")
    async def collection(self, interaction: discord.Interaction):
        #Affiche la collection d'artefacts de l'utilisateur.
        await interaction.response.defer()
        
        archaeologist = self._get_or_create_archaeologist(interaction)
        artifacts = self.db.get_archaeologist_artifacts(str(archaeologist.user_id))
        
        if not artifacts:
            embed = create_embed(
                title="📚 Votre collection",
                description="Vous n'avez pas encore découvert d'artefacts.",
                color=discord.Color.greyple()
            )
            await interaction.followup.send(embed=embed)
            return
        
        # Crée un embed pour la collection
        embed = create_embed(
            title=f"📚 Collection de {archaeologist.username}",
            description=f"Total: {len(artifacts)} artefact(s)",
            color=discord.Color.gold()
        )
        
        # Groupe les artefacts par rareté
        for rarity in config.RARITY_LEVELS:
            rarity_artifacts = [a for a in artifacts if a.rarity == rarity]
            if rarity_artifacts:
                artifact_list = "\n".join(
                    f"• {a.name} (💰 {a.value})" for a in rarity_artifacts
                )
                embed.add_field(
                    name=f"{get_rarity_emoji(rarity)} {rarity.capitalize()} ({len(rarity_artifacts)})",
                    value=artifact_list,
                    inline=False
                )
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="leaderboard", description="Affiche le classement des archéologues")
    async def leaderboard(self, interaction: discord.Interaction):
        #Affiche le leaderboard.
        await interaction.response.defer()
        
        leaderboard_data = self.db.get_leaderboard(limit=10)
        
        if not leaderboard_data:
            embed = create_embed(
                title="🏆 Classement",
                description="Aucun archéologue pour le moment.",
                color=discord.Color.greyple()
            )
            await interaction.followup.send(embed=embed)
            return
        
        embed = create_embed(
            title="🏆 Classement des Archéologues",
            description="Les meilleurs archéologues de tous les temps",
            color=discord.Color.gold()
        )
        
        medals = ["🥇", "🥈", "🥉"]
        leaderboard_text = ""
        
        for idx, (username, level, experience, coins, artifacts) in enumerate(leaderboard_data, 1):
            medal = medals[idx - 1] if idx <= 3 else f"{idx}️⃣"
            leaderboard_text += (
                f"{medal} **{username}** | "
                f"Niveau {level} | "
                f"{experience} XP | "
                f"💰 {coins} | "
                f"{artifacts} artefacts\n"
            )
        
        embed.description = leaderboard_text
        
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    #Charge le cog.
    await bot.add_cog(CollectionCog(bot))
