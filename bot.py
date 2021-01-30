"""
Git the lines

A Discord bot that removes embeds and prints out specific lines of code
when a GitHub or GitLab link is sent
"""

import asyncio
import os
import logging

import aiohttp

from discord import Activity, ActivityType
from discord.ext.commands import Bot, when_mentioned_or

from cogs.bot_info import BotInfo
from cogs.code_snippets import CodeSnippets
from cogs.top_gg import TopGG
# from cogs.repo_widgets import RepoWidgets
# from cogs.commit_widgets import CommitWidgets
# from cogs.pull_request_widgets import PullRequestWidgets


async def main():
    logging.basicConfig(level=logging.INFO)

    prefix = os.environ.get('BOT_PREFIX', 'g;')

    bot = Bot(
        command_prefix=when_mentioned_or(prefix),
        help_command=None,
        activity=Activity(type=ActivityType.watching, name=f'for snippet links and {prefix}help'),
    )

    async with aiohttp.ClientSession() as session:
        bot.add_cog(BotInfo(bot))
        bot.add_cog(CodeSnippets(bot, session))
        # bot.add_cog(RepoWidgets(bot, session))
        # bot.add_cog(CommitWidgets(bot, session))
        # bot.add_cog(PullRequestWidgets(bot, session))

        if 'TOP_GG_TOKEN' in os.environ:
            bot.add_cog(TopGG(bot))

        await bot.start(os.environ['DISCORD_TOKEN'])


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        loop.close()
