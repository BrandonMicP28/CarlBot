import asyncio
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils.database import create_database

load_dotenv()
TOKEN = os.getenv('TOKEN')
GUILD_ID = discord.Object(id=int(os.getenv('GUILD_ID')))



class CarlBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
            elif os.path.isdir(f'./cogs/{filename}') and not filename.startswith('__'):
                try:
                    await self.load_extension(f'cogs.{filename}')
                except Exception as e:
                    print(f"Failed to load folder cog {filename}: {e}")

        self.tree.copy_global_to(guild=GUILD_ID)
        await self.tree.sync(guild=GUILD_ID)

    async def on_ready(self):
        print(f'Logged in as {self.user.name}')

async def main():
    bot = CarlBot()
    async with bot:
        await bot.start(TOKEN)

if __name__ == '__main__':
    create_database()
    asyncio.run(main())