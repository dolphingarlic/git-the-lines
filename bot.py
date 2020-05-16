"""
Git the lines

A Discord bot that removes embeds and prints out specific lines of code
when a GitHub or GitLab link is sent
"""

import os

from discord.ext.commands import Bot, when_mentioned_or

from cogs.bot_info import BotInfo
from cogs.print_snippets import PrintSnippets

prefix = 'g;'
if 'BOT_PREFIX' in os.environ:
    prefix = os.environ['BOT_PREFIX']

bot = Bot(command_prefix=when_mentioned_or(prefix))
bot.remove_command('help')

bot.add_cog(BotInfo(bot))
bot.add_cog(PrintSnippets(bot))

bot.run(os.environ['DISCORD_TOKEN'])
