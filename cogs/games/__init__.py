import random

import discord
from discord import app_commands
from discord.ext import commands

from utils.database import get_user


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='flip', description='Flip a coin')
    @app_commands.describe(guess='Heads or Tails', amount='Amount to Bet')
    @app_commands.choices(guess=[
        app_commands.Choice(name="Heads", value="heads"),
        app_commands.Choice(name="Tails", value="tails")
    ])
    async def flip(self, interaction: discord.Interaction, guess: app_commands.Choice[str], amount: int):
        user = get_user(interaction.user.id)
        if user.money < amount or amount <= 0:
            await interaction.response.send_message("Invalid amount.", ephemeral=True)
            return

        answer: str = random.choice(["heads", "tails"])

        if guess.value == answer:
            user.change_money(amount)
            await interaction.response.send_message(f"{answer.capitalize()}, You Win!\nNew Balance is ${user.money}", ephemeral=False)
        else:
            user.change_money(-amount)
            await interaction.response.send_message(f"{answer.capitalize()}, You Lost!\nNew Balance is ${user.money}",
                                                    ephemeral=False)

async def setup(bot):
    await bot.add_cog(Games(bot))