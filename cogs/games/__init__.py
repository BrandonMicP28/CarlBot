import asyncio
import math
import random
from inspect import cleandoc

import discord
from discord import app_commands
from discord.ext import commands

from cogs.games.Wordle import Wordle
from cogs.games.finish_menu import create_summary_menu, ReplayButton
from utils.database import get_user
from utils.leveling import get_level

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
        original_text = f"Flipping coin on {guess.value} for ${amount}"
        await interaction.response.send_message(original_text)
        answer: str = random.choice(["heads", "tails"])
        user.change_money(amount if guess.value == answer else -amount)

        await asyncio.sleep(1)

        if guess.value == answer:
            message = cleandoc(f"""
            > 🪙 The coin landed on **{answer.capitalize()}**
            > 🎉 You Won **${amount}**!
            > 💰 New Balance: **${user.money}**
            """)
        else:
            message = cleandoc(f"""
            > 🪙 The coin landed on **{answer.capitalize()}**
            > 🥀 You Lost **${amount}**...
            > 💰 New Balance: **${user.money}**
            """)
        await interaction.edit_original_response(content=f"{original_text}\n{message}")

    @app_commands.command(name='wordle', description='Play wordle for money and xp!')
    async def wordle(self, interaction: discord.Interaction):
        member = interaction.user
        thread = await interaction.channel.create_thread(
            name=f"{member.name}'s Wordle",
            auto_archive_duration=60,
            type=discord.ChannelType.public_thread
        )
        user = get_user(member.id)

        total_money_gained = 0
        total_xp_gained = 0
        starting_money = user.money
        starting_xp = user.experience

        await interaction.response.send_message(f"Wordle Thread Created! {thread.jump_url}", ephemeral=True)
        wordle = Wordle(6)
        await thread.send("Send your first guess to start!")

        file = discord.File(fp=wordle.generate_wordle_image(), filename="wordle.png")
        image_message = await thread.send(file=file)

        def check(message: discord.Message):
            return message.author.id == member.id and message.channel.id == thread.id

        while True:
            while wordle.game_state == "ongoing":
                msg = await self.bot.wait_for('message', check=check)
                if wordle.make_guess(msg.content):
                    file = discord.File(fp=wordle.generate_wordle_image(), filename="wordle.png")
                    await image_message.edit(attachments=[file])
                await msg.delete()
            result_text = wordle.game_state.capitalize()
            await thread.send(f"# {'🎉' if result_text == 'Won' else '🥀'} You {result_text}!")
            if wordle.game_state == "lost":
                await thread.send(f"Word was: {wordle.answer.capitalize()}!")
            else:
                increased_streak = user.won_wordle_streak()
                wordle_streak, _ = user.get_wordle_streak()

                user_level = get_level(user.experience)
                payout = int((50 / len(wordle.guesses)-4.5) * (math.pow(user_level, 1.1)/10+1))
                exp_gain = int(50 / len(wordle.guesses) * 5.6) + wordle_streak

                total_money_gained += payout
                total_xp_gained += exp_gain

                user.change_money(payout)
                user.change_experience(exp_gain)
                if increased_streak:
                    await thread.send(f"> 🔥 **Streak Increased:** You are now at **{wordle_streak:,}** Day{'s' if wordle_streak > 1 else ''}!")
                await thread.send((f"> You got **${payout:,}** and **{(exp_gain - wordle_streak):,} XP**\n"
                                   f"> + **{wordle_streak:,} XP** from streak! 🔥"))

            summary_embed = create_summary_menu(total_money_gained, starting_money, xp_gained=total_xp_gained, xp=starting_xp)
            summary_embed.set_thumbnail(url=member.display_avatar.url)
            replay_buttons = ReplayButton(60)

            await thread.send(embed=summary_embed, view=replay_buttons)
            await replay_buttons.wait()

            if replay_buttons.result == "terminate":
                break
            else:
                await thread.purge(after=image_message)
                wordle.replay()
                file = discord.File(fp=wordle.generate_wordle_image(), filename="wordle.png")
                await image_message.edit(attachments=[file])

        await thread.send("Closing Thread")
        await thread.delete()

async def setup(bot):
    await bot.add_cog(Games(bot))