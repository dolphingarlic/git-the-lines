import os

from discord import Activity, ActivityType
from discord.ext.commands import Bot, when_mentioned_or
import discord.ext.test as dpytest
import pytest

from cogs.print_snippets import PrintSnippets


@pytest.mark.asyncio
async def test_github():
    prefix = 'g;'
    if 'BOT_PREFIX' in os.environ:
        prefix = os.environ['BOT_PREFIX']

    bot = Bot(
        command_prefix=when_mentioned_or(prefix),
        help_command=None,
        activity=Activity(type=ActivityType.watching, name=f'for snippet links and {prefix}help'),
    )

    bot.add_cog(PrintSnippets(bot))

    dpytest.configure(bot)

    await dpytest.message('https://github.com/dolphingarlic/git-the-lines/blob/master/README.md#L1')
    dpytest.verify_message('```md\n# Git the lines```')

    await dpytest.message('https://github.com/dolphingarlic/git-the-lines/blob/master/Procfile#L1')
    dpytest.verify_message('```Procfile\nworker: python bot.py```')
    await dpytest.message('https://github.com/dolphingarlic/git-the-lines/blob/master/Procfile#L1-L1000')
    dpytest.verify_message('```Procfile\nworker: python bot.py```')
    await dpytest.message('https://github.com/dolphingarlic/git-the-lines/blob/master/Procfile#L1-L0')
    dpytest.verify_message('```Procfile\nworker: python bot.py```')

    await dpytest.message('https://github.com/dolphingarlic/git-the-lines/blob/master/bot.py#L1-L2')
    dpytest.verify_message('```py\n"""\nGit the lines```')
    await dpytest.message('https://github.com/dolphingarlic/git-the-lines/blob/master/bot.py#L2-L1')
    dpytest.verify_message('```py\n"""\nGit the lines```')
    await dpytest.message('https://github.com/dolphingarlic/git-the-lines/blob/master/bot.py#L0-L2')
    dpytest.verify_message('```py\n"""\nGit the lines```')


@pytest.mark.asyncio
async def test_gitlab():
    prefix = 'g;'
    if 'BOT_PREFIX' in os.environ:
        prefix = os.environ['BOT_PREFIX']

    bot = Bot(
        command_prefix=when_mentioned_or(prefix),
        help_command=None,
        activity=Activity(type=ActivityType.watching, name=f'for snippet links and {prefix}help'),
    )

    bot.add_cog(PrintSnippets(bot))

    dpytest.configure(bot)

    await dpytest.message('https://gitlab.com/dolphingarlic/bot-testing/-/blob/master/example.test.py#L1-2')
    dpytest.verify_message('```py\nprint(help(str))\nprint(\'Hi\')```')

    await dpytest.message('https://gitlab.com/dolphingarlic/bot-testing/-/blob/master/nested/file.py#L1-2')
    dpytest.verify_message('```py\nprint(\'Hey there!\')\nprint(\'Nice to see you\')```')
    await dpytest.message('https://gitlab.com/dolphingarlic/bot-testing/-/blob/master/nested/file.py#L1')
    dpytest.verify_message('```py\nprint(\'Hey there!\')```')

    await dpytest.message('https://gitlab.com/dolphingarlic/bot-testing/-/blob/master/nested/fi.l/e.py#L2')
    dpytest.verify_message('```py\nprint(1 + 3)```')
