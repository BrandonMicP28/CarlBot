import discord
from discord import app_commands
from discord.ext import commands

from cogs.games.finish_menu import generate_xp_bar
from utils.database import get_user
from utils.leveling import get_level, level_to_xp


class Profiles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='profile', description='Shows your profile!')
    async def profile(self, interaction: discord.Interaction, target: discord.Member=None):
        if target is None:
            target = interaction.user
        user = get_user(target.id)
        level = get_level(user.experience)
        em = discord.Embed(title=f"{target.name}'s profile!")
        em.add_field(name="Money:", value=f"${user.money}", inline=False)
        em.add_field(name="Experience Till Next Level:", value=f"{level_to_xp(level + 1) - user.experience}", inline=False)
        em.add_field(name=f"{generate_xp_bar(user.experience)}", value=f"", inline=False)

        em.set_thumbnail(url=target.display_avatar.url)

        await interaction.response.send_message(embed=em)

async def setup(bot):
    await bot.add_cog(Profiles(bot))