"""
Cog that sends pretty embeds of repos

Matches each message against a regex and prints the contents
of the first matched snippet url
"""

import os
import re

import discord
from discord.ext.commands import Cog

from cogs.utils import fetch_http


GITHUB_RE = re.compile(
    r'https://github\.com/(?P<owner>[^/]+?)/(?P<repo>[^/]+?)(?:\s|$)')


class RepoWidgets(Cog):
    def __init__(self, bot, session):
        """Initializes the cog's bot"""

        self.bot = bot
        self.session = session

    @Cog.listener()
    async def on_message(self, message):
        """
        Checks if the message starts is a GitHub repo link, then removes the embed,
        then sends a rich embed to Discord
        """

        gh_match = GITHUB_RE.search(message.content)

        if gh_match and not message.author.bot:
            for gh in GITHUB_RE.finditer(message.content):
                d = gh.groupdict()
                headers = {}
                if 'GITHUB_TOKEN' in os.environ:
                    headers['Authorization'] = f'token {os.environ["GITHUB_TOKEN"]}'
                repo = await fetch_http(
                    self.session,
                    f'https://api.github.com/repos/{d["owner"]}/{d["repo"]}',
                    'json',
                    headers=headers,
                )

                embed = discord.Embed(
                    title=repo['full_name'],
                    description='No description provided' if repo[
                        'description'] is None else repo['description'],
                    url=repo['html_url'],
                    color=0x111111
                ).set_footer(
                    text=f'Language: {repo["language"]} | ' +
                         f'Stars: {repo["stargazers_count"]} | ' +
                         f'Forks: {repo["forks_count"]} | ' +
                         f'Size: {repo["size"]}kb'
                ).set_thumbnail(url=repo['owner']['avatar_url'])
                if repo['homepage']:
                    embed.add_field(name='Homepage', value=repo['homepage'])
                await message.channel.send(embed=embed)

            await message.edit(suppress=True)
