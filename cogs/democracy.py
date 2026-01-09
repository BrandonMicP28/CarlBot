import math
import time

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, button

from utils.database import get_user, get_all_users_xp
from utils.leveling import get_level, level_to_xp


class Democracy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voter_level_req = 1
        self.voter_xp_req = level_to_xp(self.voter_level_req)

    def valid_voters(self, interaction: discord.Interaction):
        """
        creates a list of all voters with a minimum level
        :param interaction:
        :return: Returns a list of user ids that meet the voter_xp_req
        """
        valid_voters = []
        all_users_xp = get_all_users_xp()

        for member in interaction.guild.members:
            user_xp = all_users_xp.get(member.id, 0)
            if user_xp >= self.voter_xp_req:
                valid_voters.append(member)
        return valid_voters


    @app_commands.command(name='punt', description='Kick a member from the server with 1/3 vote of online players (minimum of 3 votes to kick)')
    async def punt(self, interaction: discord.Interaction, target: discord.Member):
        """
        :param interaction:
        :param target: member to kick
        :return: if 1/3 of members or more agree to kick the target then they will be kicked from the server unless if a major denies the vote (minimum of 3 votes to kick)
        """
        vote_time = 300
        embed = discord.Embed(title=f"Kick {target.name}")
        embed.set_thumbnail(url=target.avatar.url)
        vote_start_time = math.floor(time.time())
        embed.add_field(name="Vote Ends:", value=f"<t:{vote_start_time + vote_time}:R>")
        vote = PuntButtons(vote_time)
        await interaction.response.send_message(embed=embed, view=vote)

        await vote.wait()

        num_valid_voters = len(self.valid_voters(interaction))

        yesVotes = len(vote.yesVoters)
        noVotes = len(vote.noVoters)

        if noVotes > yesVotes or yesVotes < num_valid_voters/3:
            await interaction.followup.send(f"{target.mention} survives, for now")
        else:
            await target.kick(reason="The members have decided that it's better if you weren't here")
            await interaction.followup.send(f"{target.mention} has been kicked from the server")


class PuntButtons(View):
    def __init__(self, vote_time):
        super().__init__(timeout=vote_time)
        self.yesVoters = []
        self.noVoters = []

    def update_labels(self):
        self.children[0].label = str(len(self.yesVoters))
        self.children[1].label = str(len(self.noVoters))

    @button(label='0', style=discord.ButtonStyle.blurple, emoji="✅")
    async def kick_agree(self, interaction: discord.Interaction, button: discord.ui.Button):
        voter_id: int = interaction.user.id

        if voter_id in self.noVoters:
            self.noVoters.remove(voter_id)

        if voter_id not in self.yesVoters:
            self.yesVoters.append(interaction.user.id)
            self.update_labels()
            await interaction.response.edit_message(view=self)
        else:
            await interaction.response.send_message("You've already voted to kick!", ephemeral=True)

    @button(label='0', style=discord.ButtonStyle.blurple, emoji="❌")
    async def kick_disagree(self, interaction: discord.Interaction, button: discord.ui.Button):
        voter_id: int = interaction.user.id

        if voter_id in self.yesVoters:
            self.yesVoters.remove(voter_id)

        if voter_id not in self.noVoters:
            self.noVoters.append(interaction.user.id)
            self.update_labels()
            await interaction.response.edit_message(view=self)
        else:
            await interaction.response.send_message("You've already voted against the kick!", ephemeral=True)



async def setup(bot):
    await bot.add_cog(Democracy(bot))