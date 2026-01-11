from math import ceil

import discord

from utils.leveling import get_level, level_to_xp
from discord.ui import View, button


class SummaryMenu:
    def __init__(self):
        pass
def create_summary_menu(money_gained, money, xp_gained=0, xp=0):
    embed = discord.Embed(title="Summary!")
    embed.add_field(name="Money Gained:", value=f"${money} + ${money_gained} -> ${money + money_gained}", inline=False)
    if xp_gained > 0 and xp > 0:
        embed.add_field(name="XP Gained:", value=f"{xp} + {xp_gained} -> {xp + xp_gained}", inline=False)

        level = get_level(xp + xp_gained)
        xp_till_level_up = level_to_xp(level+1) - (xp + xp_gained)

        embed.add_field(name="XP Till Level Up:", value=xp_till_level_up, inline=True)
        embed.add_field(name=generate_xp_bar(xp+xp_gained), value="", inline=False)
    return embed


class ReplayButton(View):

    def __init__(self, timeout):
        super().__init__(timeout=timeout)
        self.result = "terminate"

    @button(label='Replay', style=discord.ButtonStyle.blurple, emoji="🔄")
    async def replay(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.result = "replay"
        await interaction.response.defer()
        self.stop()

    @button(label='Close Thread', style=discord.ButtonStyle.red, emoji="🚫")
    async def close_thread(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.result = "terminate"
        await interaction.response.defer()
        self.stop()


def generate_xp_bar(xp:int):
    level = get_level(xp)
    xp_for_next_level = level_to_xp(level + 1) - level_to_xp(level)
    progress_to_next_level = xp - level_to_xp(level)

    percentage_progress = (progress_to_next_level/xp_for_next_level) * 100
    #number_of_bars = 10
    xp_bar: str = f"**{level}** |{'▰' * int(percentage_progress/10)}{'▱' * ceil(10 - (percentage_progress/10))}| **{level+1}**"
    return xp_bar
