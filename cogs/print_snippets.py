"""
Cog that prints out snippets to Discord

Matches each message against a regex and prints the contents
of the first matched snippet url
"""

import re

from discord.ext.commands import Cog

from cogs.utils import (fetch_bitbucket_snippet, fetch_github_gist_snippet,
                        fetch_github_snippet, fetch_gitlab_snippet)

GITHUB_RE = re.compile(
    r'https://github\.com/(?P<repo>.+?)/blob/(?P<path>.+/.+)' +
    r'#L(?P<start_line>\d+)([-~]L(?P<end_line>\d+))?\b'
)

GITHUB_GIST_RE = re.compile(
    r'https://gist\.github\.com/([^/]*)/(?P<gist_id>[0-9a-zA-Z]+)/*' +
    r'(?P<revision>[0-9a-zA-Z]*)/*#file-(?P<file_path>.+?)' +
    r'-L(?P<start_line>\d+)([-~]L(?P<end_line>\d+))?\b'
)

GITLAB_RE = re.compile(
    r'https://gitlab\.com/(?P<repo>.+?)/\-/blob/(?P<path>.+/.+)' +
    r'#L(?P<start_line>\d+)([-~](?P<end_line>\d+))?\b'
)

BITBUCKET_RE = re.compile(
    r'https://bitbucket\.org/(?P<repo>.+?)/src/(?P<ref>.+?)/' +
    r'(?P<file_path>.+?)#lines-(?P<start_line>\d+)(:(?P<end_line>\d+))?\b'
)


class PrintSnippets(Cog):
    def __init__(self, bot, session):
        """Initializes the cog's bot"""

        self.bot = bot
        self.session = session

    @Cog.listener()
    async def on_message(self, message):
        """
        Checks if the message starts is a GitHub snippet, then removes the embed,
        then sends the snippet in Discord
        """

        gh_match = GITHUB_RE.search(message.content)
        gh_gist_match = GITHUB_GIST_RE.search(message.content)
        gl_match = GITLAB_RE.search(message.content)
        bb_match = BITBUCKET_RE.search(message.content)

        if (gh_match or gh_gist_match or gl_match or bb_match) and not message.author.bot:
            message_to_send = ''

            for gh in GITHUB_RE.finditer(message.content):
                message_to_send += await fetch_github_snippet(self.session, **gh.groupdict())

            for gh_gist in GITHUB_GIST_RE.finditer(message.content):
                message_to_send += await fetch_github_gist_snippet(self.session, **gh_gist.groupdict())

            for gl in GITLAB_RE.finditer(message.content):
                message_to_send += await fetch_gitlab_snippet(self.session, **gl.groupdict())

            for bb in BITBUCKET_RE.finditer(message.content):
                message_to_send += await fetch_bitbucket_snippet(self.session, **bb.groupdict())

            message_to_send = message_to_send[:-1]

            if len(message_to_send) > 2000:
                await message.channel.send(
                    'Sorry, Discord has a 2000 character limit. Please send a shorter ' +
                    'snippet or split the big snippet up into several smaller ones :slight_smile:'
                )
            elif len(message_to_send) == 0:
                await message.channel.send(
                    'Please send valid snippet links to prevent spam :slight_smile:'
                )
            elif message_to_send.count('\n') > 50:
                await message.channel.send(
                    'Please limit the total number of lines to at most 50 to prevent spam :slight_smile:'
                )
            else:
                await message.channel.send(message_to_send)
            await message.edit(suppress=True)
