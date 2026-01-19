from inspect import cleandoc

import discord
from discord import app_commands
from discord.ext import commands


class Info(commands.Cog):

    @app_commands.command(name='info', description='Various info about the bot!')
    @app_commands.describe(info='What info would you like to hear about')
    @app_commands.choices(info=[
        app_commands.Choice(name="Money", value="money"),
        app_commands.Choice(name="Experience", value="experience"),
        app_commands.Choice(name="Democracy", value="democracy"),
        app_commands.Choice(name="Stats", value="stats")
    ])
    async def info(self, interaction: discord.Interaction, info: str = "info"):
        message = "If you see this then something has gone wrong"
        if info == "info":
            message = cleandoc("""
            # 🤖 Carl Bot Info
            **Money, Wealth, Greed, and Democracy!**

            To learn more, try `/info [category]`:
            • **money** - Ways to get rich
            • **experience** - How to level up
            • **democracy** - How to kick people
            • **stats** - View profiles and leaderboards
            """)

        elif info == "money":
            message = cleandoc("""
            # 💵 Money
            *There are a few ways to build your wealth:*

            ### 1. `/Wordle`
            Play a game of Wordle.
            > • **Pay:** Based on guesses left and increased by your Level.

            ### 2. `/flip`
            A simple 50/50 coin flip.
            > Double your money or lose it all.
            """)

        elif info == "experience":
            message = cleandoc("""
            # ✨ Experience
            *Currently, there is only one way to gain XP:*

            ### 1. `/Wordle`
            > • **XP Gain:** Based on guesses left.
            > • **Bonus:** +1 XP per day of your streak.
            """)

        elif info == "democracy":
            message = cleandoc("""
            # 🗳️ Democracy
            *This server is run by the people.*

            ### 1. `/punt [user]`
            Start a vote to **kick** a player from the server.

            **The Rules:**
            • **Voters:** Must be Level 1+.
            • **Requirement:** 1/3 of all eligible voters must participate.
            • **Minimum:** At least 3 votes to kick are required.
            """)

        elif info == "stats":
            message = cleandoc("""
            # 📊 Stats
            *Check how you compare to the rest of the server.*

            • `/profile` - View your balance, XP, and streaks.
            • `/leaderboard` - Top 10 players in Money or XP.
            • `/voters` - See who is eligible to vote (Level 1+).
            """)

        await interaction.response.send_message(message, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Info(bot))