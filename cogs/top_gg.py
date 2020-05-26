import os

import dbl
from discord.ext.commands import Cog


class TopGG(Cog):
    """Handles interactions with the top.gg API"""

    def __init__(self, bot):
        """Sets the bot and top.gg tokens"""

        self.bot = bot
        self.token = os.environ['TOP_GG_TOKEN']
        self.dblpy = dbl.DBLClient(self.bot, self.token, autopost=True)

    @Cog.listener()
    async def on_guild_post(self):
        print("Server count posted successfully")
