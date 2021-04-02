import aiohttp
import discord.ext.test as dpytest
import pytest

from cogs.code_snippets import CodeSnippets
from discord.ext.commands import Bot


@pytest.fixture(scope="function")
async def bot():
    """Fixture for creating a bot"""

    async with aiohttp.ClientSession() as session:
        bot = Bot(command_prefix='.')
        bot.add_cog(CodeSnippets(bot, session))

        yield bot


@pytest.mark.asyncio
async def test_github(bot):
    """Tests printing GitHub snippets"""

    dpytest.configure(bot)

    # Test single line
    await dpytest.message('https://github.com/dolphingarlic/git-the-lines/blob/master/README.md#L1')
    dpytest.verify_message('`README.md` line 1\n```md\n# Git the lines```')

    # Test no file extension
    await dpytest.message('https://github.com/dolphingarlic/git-the-lines/blob/master/Procfile#L1')
    dpytest.verify_message('`Procfile` line 1\n```Procfile\nworker: python bot.py```')

    # Test indexing of multi-line snippets
    await dpytest.message('https://github.com/dolphingarlic/git-the-lines/blob/master/bot.py#L1-L2')
    dpytest.verify_message('`bot.py` lines 1 to 2\n```py\n"""\nGit the lines```')
    await dpytest.message('https://github.com/dolphingarlic/git-the-lines/blob/master/bot.py#L2-L1')
    dpytest.verify_message('`bot.py` lines 1 to 2\n```py\n"""\nGit the lines```')
    await dpytest.message('https://github.com/dolphingarlic/git-the-lines/blob/master/bot.py#L0~L2')
    dpytest.verify_message('`bot.py` lines 1 to 2\n```py\n"""\nGit the lines```')

    # Test no line range
    await dpytest.message('https://github.com/dolphingarlic/git-the-lines/blob/master/Procfile')
    dpytest.verify_message('`Procfile` line 1\n```Procfile\nworker: python bot.py```')


@pytest.mark.asyncio
async def test_github_gists(bot):
    """Tests printing GitHub Gist snippets"""

    dpytest.configure(bot)

    # Test single-line snippet
    await dpytest.message('https://gist.github.com/dolphingarlic/af127f2dcd5be302852d2b43e93802b7#file-test-py-L1')
    dpytest.verify_message('`test.py` line 1\n```py\nprint(\'Hello world!\')```')
    await dpytest.message('https://gist.github.com/dolphingarlic/af127f2dcd5be302852d2b43e93802b7/0127ff78c999c29697d65fa975c7d89c470e4984#file-test-py-L1')
    dpytest.verify_message('`test.py` line 1\n```py\nprint(\'Hello world!\')```')

    # Test single-line with indentation
    await dpytest.message('https://gist.github.com/dolphingarlic/9881f9bdd40d342338b2dc5d794f12d6#file-funkyname-test-cpp-L4')
    dpytest.verify_message('`FuNkYnAmE.test.cpp` line 4\n```cpp\nstd::cout << "Test\\n";```')

    # Test multi-line snippet
    await dpytest.message('https://gist.github.com/dolphingarlic/9881f9bdd40d342338b2dc5d794f12d6#file-funkyname-test-cpp-L1-L3')
    dpytest.verify_message('`FuNkYnAmE.test.cpp` lines 1 to 3\n```cpp\n#include <iostream>\n\nint main() {```')
    await dpytest.message('https://gist.github.com/dolphingarlic/9881f9bdd40d342338b2dc5d794f12d6#file-funkyname-test-cpp-L3~L1')
    dpytest.verify_message('`FuNkYnAmE.test.cpp` lines 1 to 3\n```cpp\n#include <iostream>\n\nint main() {```')


@pytest.mark.asyncio
async def test_gitlab(bot):
    """Tests printing GitLab snippets"""

    dpytest.configure(bot)

    # Test multi-line snippet
    await dpytest.message('https://gitlab.com/dolphingarlic/bot-testing/-/blob/master/example.test.py#L1-2')
    dpytest.verify_message('`example.test.py` lines 1 to 2\n```py\nprint(help(str))\nprint(\'Hi\')```')

    # Test nested file
    await dpytest.message('https://gitlab.com/dolphingarlic/bot-testing/-/blob/master/nested/file.py#L1-2')
    dpytest.verify_message('`nested/file.py` lines 1 to 2\n```py\nprint(\'Hey there!\')\nprint(\'Nice to see you\')```')
    await dpytest.message('https://gitlab.com/dolphingarlic/bot-testing/-/blob/master/nested/file.py#L1')
    dpytest.verify_message('`nested/file.py` line 1\n```py\nprint(\'Hey there!\')```')

    # Test weird file path
    await dpytest.message('https://gitlab.com/dolphingarlic/bot-testing/-/blob/master/nested/fi.l/e.py#L2')
    dpytest.verify_message('`nested/fi.l/e.py` line 2\n```py\nprint(1 + 3)```')

    # Test no file extension
    await dpytest.message('https://gitlab.com/dolphingarlic/bot-testing/-/blob/master/nested/fi.l/ee#L1')
    dpytest.verify_message('`nested/fi.l/ee` line 1\n```ee\nMinu nimi on Andi```')

    # Test no line range
    await dpytest.message('https://gitlab.com/dolphingarlic/bot-testing/-/blob/master/nested/fi.l/e.py')
    dpytest.verify_message('`nested/fi.l/e.py` lines 1 to 2\n```py\nprint(\'Hi\')\nprint(1 + 3)```')


@pytest.mark.asyncio
async def test_bitbucket(bot):
    """Tests printing BitBucket snippets"""

    dpytest.configure(bot)

    # Test single line
    await dpytest.message('https://bitbucket.org/avdg/ai-bot-js/src/197308c293b64151ef6ac1b7238051ed415a181b/MyBot.js#lines-1')
    dpytest.verify_message('`MyBot.js` line 1\n```js\nvar stream = require("./lib/stream");```')

    # Test multi line
    await dpytest.message('https://bitbucket.org/avdg/ai-bot-js/src/197308c293b64151ef6ac1b7238051ed415a181b/MyBot.js#lines-1:2')
    dpytest.verify_message('`MyBot.js` lines 1 to 2\n```js\nvar stream = require("./lib/stream");\nvar util = require("util");```')

@pytest.mark.asyncio
async def test_heptapod(bot):
    """Tests printing Heptapod snippets"""
    
    dpytest.configure(bot)
    
    # Test single line
    await dpytest.message('https://foss.heptapod.net/pypy/pypy/-/blob/branch/py3.7/rpython/rtyper/lltypesystem/module/ll_math.py#L70')
    dpytest.verify_message('`rpython/rtyper/lltypesystem/module/ll_math.py` line 70\n```py\nmath_floor = llexternal('floor', [rffi.DOUBLE], rffi.DOUBLE, elidable_function=True)```')
    
    # Test multi line
    await dpytest.message('https://foss.heptapod.net/pypy/pypy/-/blob/branch/py3.7/include/PyPy.h#L1-2')
    dpytest.verify_message('`include/PyPy.h` lines 1 to 2\n```h\n#ifndef _PYPY_H_\n#define _PYPY_H_```')
