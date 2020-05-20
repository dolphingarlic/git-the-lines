from discord.ext.commands import Bot
import discord.ext.test as dpytest
import pytest

from cogs.print_snippets import PrintSnippets


@pytest.mark.asyncio
async def test_github():
    """
    Tests printing GitHub snippets
    """
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
async def test_github_gists():
    """
    Tests printing GitHub Gist snippets
    """
    bot = Bot(command_prefix='.')

    bot.add_cog(PrintSnippets(bot))

    dpytest.configure(bot)

    # Test single-line snippet
    await dpytest.message('https://gist.github.com/dolphingarlic/af127f2dcd5be302852d2b43e93802b7#file-test-py-L1')
    dpytest.verify_message('```py\nprint(\'Hello world!\')```')
    await dpytest.message('https://gist.github.com/dolphingarlic/af127f2dcd5be302852d2b43e93802b7/0127ff78c999c29697d65fa975c7d89c470e4984#file-test-py-L1')
    dpytest.verify_message('```py\nprint(\'Hello world!\')```')

    # Test single-line with indentation
    await dpytest.message('https://gist.github.com/dolphingarlic/9881f9bdd40d342338b2dc5d794f12d6#file-funkyname-test-cpp-L4')
    dpytest.verify_message('```cpp\nstd::cout << "Test\\n";```')

    # Test multi-line snippet
    await dpytest.message('https://gist.github.com/dolphingarlic/9881f9bdd40d342338b2dc5d794f12d6#file-funkyname-test-cpp-L1-L3')
    dpytest.verify_message('```cpp\n#include <iostream>\n\nint main() {```')
    await dpytest.message('https://gist.github.com/dolphingarlic/9881f9bdd40d342338b2dc5d794f12d6#file-funkyname-test-cpp-L3-L1')
    dpytest.verify_message('```cpp\n#include <iostream>\n\nint main() {```')


@pytest.mark.asyncio
async def test_gitlab():
    """
    Tests printing GitLab snippets
    """
    bot = Bot(command_prefix='.')

    bot.add_cog(PrintSnippets(bot))

    dpytest.configure(bot)

    # Test multi-line snippet
    await dpytest.message('https://gitlab.com/dolphingarlic/bot-testing/-/blob/master/example.test.py#L1-2')
    dpytest.verify_message('```py\nprint(help(str))\nprint(\'Hi\')```')

    # Test nested file
    await dpytest.message('https://gitlab.com/dolphingarlic/bot-testing/-/blob/master/nested/file.py#L1-2')
    dpytest.verify_message(
        '```py\nprint(\'Hey there!\')\nprint(\'Nice to see you\')```')
    await dpytest.message('https://gitlab.com/dolphingarlic/bot-testing/-/blob/master/nested/file.py#L1')
    dpytest.verify_message('```py\nprint(\'Hey there!\')```')

    # Test weird file path
    await dpytest.message('https://gitlab.com/dolphingarlic/bot-testing/-/blob/master/nested/fi.l/e.py#L2')
    dpytest.verify_message('```py\nprint(1 + 3)```')

    # Test no file extension
    await dpytest.message('https://gitlab.com/dolphingarlic/bot-testing/-/blob/master/nested/fi.l/ee#L1')
    dpytest.verify_message('```ee\nMinu nimi on Andi```')


@pytest.mark.asyncio
async def test_bitbucket():
    """
    Tests printing BitBucket snippets
    """
    bot = Bot(command_prefix='.')

    bot.add_cog(PrintSnippets(bot))

    dpytest.configure(bot)

    # Test single line
    await dpytest.message('https://bitbucket.org/avdg/ai-bot-js/src/197308c293b64151ef6ac1b7238051ed415a181b/MyBot.js#lines-1')
    dpytest.verify_message('```js\nvar stream = require("./lib/stream");```')

    # Test multi line
    await dpytest.message('https://bitbucket.org/avdg/ai-bot-js/src/197308c293b64151ef6ac1b7238051ed415a181b/MyBot.js#lines-1:2')
    dpytest.verify_message(
        '```js\nvar stream = require("./lib/stream");\nvar util = require("util");```')
