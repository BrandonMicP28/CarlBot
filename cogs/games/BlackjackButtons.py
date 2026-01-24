import discord
from discord.ui import View, button

class BlackjackButtons(View):
    def __init__(self, player_id, timeout=60):
        super().__init__(timeout=timeout)
        self.result = "stand"
        self.player_id = player_id

    @button(label='Hit', style=discord.ButtonStyle.blurple, emoji="👊")
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.player_id == interaction.user.id:
            self.result = "hit"
            await interaction.response.defer()
            self.stop()
        else:
            await interaction.response.send_message("It's not your turn!", ephemeral=True)

    @button(label='Stand', style=discord.ButtonStyle.blurple, emoji="✋")
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.player_id == interaction.user.id:
            self.result = "stand"
            await interaction.response.defer()
            self.stop()
        else:
            await interaction.response.send_message("It's not your turn!", ephemeral=True)


class JoinGameButtons(View):
    def __init__(self, players, embed, timeout=300):
        super().__init__(timeout=timeout)
        self.players = players
        self.embed: discord.Embed = embed

    @button(label='join', style=discord.ButtonStyle.blurple, emoji="✅")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        if member in self.players:
            await interaction.response.send_message("You are already in the game!", ephemeral=True)
        else:
            self.players.append(member)
            await interaction.message.edit(embed=self.update_embed())
            await interaction.response.send_message("You've joined!", ephemeral=True)

    @button(label='leave', style=discord.ButtonStyle.blurple, emoji="🚪")
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        if not member in self.players:
            await interaction.response.send_message("You aren't in the game!", ephemeral=True)
        else:
            self.players.remove(member)
            await interaction.message.edit(embed=self.update_embed())
            await interaction.response.send_message("You've left the game 🥀", ephemeral=True)

    @button(label='start', style=discord.ButtonStyle.blurple, emoji="⚡")
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(self.players) <= 0 or self.players[0] != interaction.user:
            await interaction.response.send_message("Only the host can start the game!", ephemeral=True)
            return
        await interaction.response.send_message("Starting game...")
        self.stop()

    def update_embed(self):
        embed = self.embed.copy()
        embed.add_field(name=f"Players ({len(self.players)}):", value=", ".join([player.name for player in self.players]), inline=False)

        return embed