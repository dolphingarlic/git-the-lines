"""
Cog that sends pretty embeds of repos

Matches each message against a regex and prints the contents
of the first matched snippet url
"""

import datetime
import os
import re

import discord
from discord.ext.commands import Cog

from cogs.utils import fetch_http


GITHUB_RE = re.compile(
    r'https://github\.com/(?P<owner>[^/\s]+)/(?P<repo>[^/\s]+)/commit/'
    r'(?P<commit>[^/\s]+)'
)


class CommitWidgets(Cog):
    def __init__(self, bot, session):
        """Initializes the cog's bot"""

        self.bot = bot
        self.session = session

    @Cog.listener()
    async def on_message(self, message):
        """
        Checks if the message contains is a commit link, then removes the embed,
        then sends a rich embed to Discord
        """

        gh_match = GITHUB_RE.search(message.content)

        if gh_match and not message.author.bot:
            for gh in GITHUB_RE.finditer(message.content):
                d = gh.groupdict()
                headers = {}
                if 'GITHUB_TOKEN' in os.environ:
                    headers['Authorization'] = f'token {os.environ["GITHUB_TOKEN"]}'
                commit = await fetch_http(
                    self.session,
                    f'https://api.github.com/repos/{d["owner"]}/{d["repo"]}/commits/{d["commit"]}',
                    'json',
                    headers=headers,
                )

                embed = discord.Embed(
                    title=f'commit `{commit["sha"]}`',
                    description=commit['commit']['message'],
                    url=commit['html_url'],
                    timestamp=datetime.datetime.fromisoformat(
                        commit['commit']['author']['date'][:-1]
                    ),
                    color=0x111111
                ).set_author(
                    name=f'{d["owner"]}/{d["repo"]}',
                    url=f'https://github.com/{d["owner"]}/{d["repo"]}'
                ).add_field(
                    name="Additions",
                    value=str(commit['stats']['additions']),
                    inline=True
                ).add_field(
                    name="Deletions",
                    value=str(commit['stats']['deletions']),
                    inline=True
                ).add_field(
                    name="Files Changed",
                    value=str(len(commit['files'])),
                    inline=True
                ).set_footer(
                    text=f'{commit["author"]["login"]} committed',
                    icon_url=commit['author']['avatar_url']
                )

                await message.channel.send(embed=embed)

            await message.edit(suppress=True)
