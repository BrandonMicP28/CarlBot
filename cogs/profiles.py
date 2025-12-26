import discord
from discord import app_commands
from discord.ext import commands

from utils.database import get_user


class Profiles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='profile', description='Shows your profile!')
    async def profile(self, interaction: discord.Interaction):
        user = get_user(interaction.user.id)
        em = discord.Embed(title=f"{interaction.user.name}'s profile!")
        em.add_field(name="Money", value=f"${user.money}", inline=False)
        em.add_field(name="Experience", value=f"${user.experience}", inline=False)
        em.set_thumbnail(url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=em)

async def setup(bot):
    await bot.add_cog(Profiles(bot))