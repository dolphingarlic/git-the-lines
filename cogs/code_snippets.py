"""
Cog that prints out snippets to Discord

Matches each message against a regex and prints the contents
of the first matched snippet url
"""

import re

from discord.ext.commands import Cog

from cogs.utils import (fetch_bitbucket_snippet, fetch_github_gist_snippet,
                        fetch_github_snippet, fetch_gitlab_snippet, fetch_heptapod_snippet,
                        wait_for_deletion)

GITHUB_RE = re.compile(
    r'https://github\.com/(?P<repo>[a-zA-Z0-9-]+/[\w.-]+)/blob/'
    r'(?P<path>[^#>\s]+)(\?[^#>\s]+)?(#L(?P<start_line>\d+)([-~:]L(?P<end_line>\d+))?)?'
)

GITHUB_GIST_RE = re.compile(
    r'https://gist\.github\.com/([a-zA-Z0-9-]+)/(?P<gist_id>[a-zA-Z0-9]+)/*'
    r'(?P<revision>[a-zA-Z0-9]*)/*#file-(?P<file_path>[^#>\s]+?)(\?[^#>\s]+)?'
    r'(-L(?P<start_line>\d+)([-~:]L(?P<end_line>\d+))?)'
)

GITLAB_RE = re.compile(
    r'https://gitlab\.com/(?P<repo>[\w.-]+/[\w.-]+)/\-/blob/(?P<path>[^#>\s]+)'
    r'(\?[^#>\s]+)?(#L(?P<start_line>\d+)(-(?P<end_line>\d+))?)?'
)

BITBUCKET_RE = re.compile(
    r'https://bitbucket\.org/(?P<repo>[a-zA-Z0-9-]+/[\w.-]+)/src/(?P<ref>[0-9a-zA-Z]+)'
    r'/(?P<file_path>[^#>\s]+)(\?[^#>\s]+)?(#lines-(?P<start_line>\d+)(:(?P<end_line>\d+))?)?'
)

HEPTAPOD_RE = re.compile(
    r'https://foss\.heptapod\.net/([a-zA-Z0-9-]+/[\w.-]+)/-/blob/'
    r'([^#>]+)(\?[^#>]+)?(#L(\d+)([-~:](\d+))?)?'
)

class CodeSnippets(Cog):
    def __init__(self, bot, session):
        """Initializes the cog's bot"""

        self.bot = bot
        self.session = session
        
        self.pattern_handlers = [
            (GITHUB_RE, fetch_github_snippet),
            (GITHUB_GIST_RE, fetch_github_gist_snippet),
            (GITLAB_RE, fetch_gitlab_snippet),
            (BITBUCKET_RE, fetch_bitbucket_snippet),
            (HEPTAPOD_RE, fetch_heptapod_snippet)
        ]

    @Cog.listener()
    async def on_message(self, message):
        """
        Checks if the message starts is a GitHub snippet, then removes the embed,
        then sends the snippet in Discord
        """
        
        if not message.author.bot:
            message_to_send = ''

            for pattern, handler in self.pattern_handlers:
                for match in pattern.finditer(message.content):
                    message_to_send += await handler(self.session, **match.groupdict())

            if 0 < len(message_to_send) <= 2000 and message_to_send.count('\n') <= 50:
                await wait_for_deletion(message, self.bot, message_to_send)
