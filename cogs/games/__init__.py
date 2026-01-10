import math
import random

import discord
from discord import app_commands
from discord.ext import commands

from cogs.games.Wordle import Wordle
from utils.database import get_user
from utils.leveling import get_level
from discord.ui import View, button

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

    @app_commands.command(name='wordle', description='Play wordle for money and xp!')
    async def wordle(self, interaction: discord.Interaction):
        member = interaction.user
        thread = await interaction.channel.create_thread(
            name=f"{member.name}'s Wordle",
            auto_archive_duration=60,
        )

        await interaction.response.send_message(f"Wordle Thread Created! {thread.jump_url}", ephemeral=True)
        wordle = Wordle(6)
        await thread.send("Send your first guess to start!")

        file = discord.File(fp=wordle.generate_wordle_image(), filename="wordle.png")
        image_message = await thread.send(file=file)

        def check(message: discord.Message):
            return message.author.id == member.id and message.channel.id == thread.id

        while wordle.game_state == "ongoing":
            msg = await self.bot.wait_for('message', check=check)
            if wordle.make_guess(msg.content):
                file = discord.File(fp=wordle.generate_wordle_image(), filename="wordle.png")
                await image_message.edit(attachments=[file])
            await msg.delete()
        await thread.send(f"You {wordle.game_state.capitalize()}!")
        if wordle.game_state == "lost":
            await thread.send(f"Word was: {wordle.answer.capitalize()}!")
        else:
            user = get_user(member.id)
            user_level = get_level(user.experience)
            payout = int((50 / len(wordle.guesses)-4.5) * (math.pow(user_level, 1.1)/10+1))
            exp_gain = int(50 / len(wordle.guesses) * 5.6)
            user.change_money(payout)
            user.change_experience(exp_gain)
            thread.send(f"You got **${payout}** and **{exp_gain} EXP**!")

    class replay_buttons(View)



async def setup(bot):
    await bot.add_cog(Games(bot))