import discord
from discord import app_commands
from discord.ext import commands

from cogs.games.finish_menu import generate_xp_bar
from utils.database import get_user, get_leaderboard
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
        wordle_streak, _ = user.get_wordle_streak()
        em = discord.Embed(
            title=f"{target.name}'s profile!",
            description=f"{generate_xp_bar(user.experience)}")
        em.add_field(name="💵 Balance:", value=f"${user.money:,}", inline=True)
        if wordle_streak > 0:
            em.add_field(name="🔥 Wordle Streak:", value=f"{wordle_streak:,} day{'s' if wordle_streak > 1 else ''}!", inline=True)
        em.add_field(name="✨ Experience Till Next Level:", value=f"{(level_to_xp(level + 1) - user.experience):,}", inline=False)

        em.set_thumbnail(url=target.display_avatar.url)

        await interaction.response.send_message(embed=em)


    @app_commands.command(name='leaderboard', description='Leaderboard of users (can be sorted by different categories)!')
    @app_commands.describe(category='What to sort by')
    @app_commands.choices(category=[
        app_commands.Choice(name="Money", value="money"),
        app_commands.Choice(name="Experience", value="experience")
    ])
    async def leaderboard(self, interaction: discord.Interaction, category: str = "experience"):
        try:
            size = 10
            await interaction.response.defer()

            leaderboard = get_leaderboard(size, category)
            embed = discord.Embed(title=f"{category.capitalize()} Leaderboard!")
            for i, user in enumerate(leaderboard):

                member: discord.Member = self.bot.get_user(user.id)
                if member is None:
                    try:
                        member = await self.bot.fetch_user(user.id)
                    except discord.NotFound:
                        continue

                if i == 0:
                    embed.set_thumbnail(url=member.display_avatar.url)

                if category == "experience":
                    category_value = f"{user.experience:,} XP"
                else:
                    category_value = f"${user.money:,}"
                level = get_level(user.experience)
                level_color = get_level_color(level)

                embed.add_field(name="", value=f"```ansi\n{i + 1}. {member.name} [{level_color}{level:,}\u001b[0;37m]:\n{category_value}\n```",
                                inline=False)

            await interaction.followup.send(embed=embed)
        except Exception as e:
            print(e)

def get_level_color(level: int) -> str:
    if level < 10: return "\u001b[1;30m"  # Stone (Gray)
    if level < 20: return "\u001b[0;37m"  # Iron (White)
    if level < 30: return "\u001b[0;32m"  # Moss (Dark Green)
    if level < 40: return "\u001b[1;32m"  # Emerald (Bright Green)
    if level < 50: return "\u001b[0;36m"  # Ice (Cyan)
    if level < 60: return "\u001b[1;36m"  # Sky (Bright Cyan)
    if level < 70: return "\u001b[0;35m"  # Void (Purple)
    if level < 80: return "\u001b[1;35m"  # Magic (Pink)
    if level < 90: return "\u001b[1;31m"  # Blood (Red)
    return "\u001b[1;33m"  # God (Gold)

async def setup(bot):
    await bot.add_cog(Profiles(bot))