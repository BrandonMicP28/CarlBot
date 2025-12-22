import asyncio
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
GUILD_ID = discord.Object(id=int(os.getenv('GUILD_ID')))



class CarlBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        for extension in os.listdir('./cogs'):
            if extension.endswith('.py'):
                await self.load_extension(f'cogs.{extension[:-3]}')

        self.tree.copy_global_to(guild=GUILD_ID)
        await self.tree.sync(guild=GUILD_ID)

    async def on_ready(self):
        print(f'Logged in as {self.user.name}')

async def main():
    bot = CarlBot()
    async with bot:
        await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())