import discord
from discord import app_commands
from discord.ext import commands

class Profiles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='profile', description='Shows your profile!')
    async def profile(self, interaction: discord.Interaction):
        em = discord.Embed(title=f"{interaction.user.name}'s profile!")
        em.add_field(name="dude bro", value="$-1", inline=True)
        em.set_thumbnail(url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=em)

async def setup(bot):
    await bot.add_cog(Profiles(bot))