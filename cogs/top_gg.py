import os

import dbl
import discord
from discord.ext import commands


class TopGG(commands.Cog):
    """Handles interactions with the top.gg API"""

    def __init__(self, bot):
        self.bot = bot
        self.token = os.environ['TOP_GG_TOKEN']
        self.dblpy = dbl.DBLClient(self.bot, self.token, autopost=True)

    async def on_guild_post():
        print("Server count posted successfully")
