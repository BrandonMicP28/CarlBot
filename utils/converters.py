from io import BytesIO

import discord
from PIL import Image


def image_to_discord(img: Image.Image):
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return discord.File(buffer, filename='discord.png')