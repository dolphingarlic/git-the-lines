from discord.ext.commands import Bot
import discord.ext.test as dpytest
import pytest

from cogs.print_snippets import PrintSnippets


@pytest.mark.asyncio
async def test_github():
    bot = Bot(command_prefix='.')

    bot.add_cog(PrintSnippets(bot))

    dpytest.configure(bot)

    # Test single line
    await dpytest.message('https://github.com/dolphingarlic/git-the-lines/blob/master/README.md#L1')
    dpytest.verify_message('```md\n# Git the lines```')

    # Test no file extension
    await dpytest.message('https://github.com/dolphingarlic/git-the-lines/blob/master/Procfile#L1')
    dpytest.verify_message('```Procfile\nworker: python bot.py```')

    # Test indexing of multi-line snippets
    await dpytest.message('https://github.com/dolphingarlic/git-the-lines/blob/master/bot.py#L1-L2')
    dpytest.verify_message('```py\n"""\nGit the lines```')
    await dpytest.message('https://github.com/dolphingarlic/git-the-lines/blob/master/bot.py#L2-L1')
    dpytest.verify_message('```py\n"""\nGit the lines```')
    await dpytest.message('https://github.com/dolphingarlic/git-the-lines/blob/master/bot.py#L0-L2')
    dpytest.verify_message('```py\n"""\nGit the lines```')


@pytest.mark.asyncio
async def test_gitlab():
    bot = Bot(command_prefix='.')

    bot.add_cog(PrintSnippets(bot))

    dpytest.configure(bot)

    # Test multi-line snippet
    await dpytest.message('https://gitlab.com/dolphingarlic/bot-testing/-/blob/master/example.test.py#L1-2')
    dpytest.verify_message('```py\nprint(help(str))\nprint(\'Hi\')```')

    # Test nested file
    await dpytest.message('https://gitlab.com/dolphingarlic/bot-testing/-/blob/master/nested/file.py#L1-2')
    dpytest.verify_message('```py\nprint(\'Hey there!\')\nprint(\'Nice to see you\')```')
    await dpytest.message('https://gitlab.com/dolphingarlic/bot-testing/-/blob/master/nested/file.py#L1')
    dpytest.verify_message('```py\nprint(\'Hey there!\')```')

    # Test weird file path
    await dpytest.message('https://gitlab.com/dolphingarlic/bot-testing/-/blob/master/nested/fi.l/e.py#L2')
    dpytest.verify_message('```py\nprint(1 + 3)```')

    # Test no file extension
    await dpytest.message('https://gitlab.com/dolphingarlic/bot-testing/-/blob/master/nested/fi.l/ee#L1')
    dpytest.verify_message('```ee\nMinu nimi on Andi```')
