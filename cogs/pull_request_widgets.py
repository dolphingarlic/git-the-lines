"""
Cog that sends pretty embeds of PRs

Matches each message against a regex and prints the contents
of matched snippets' url
"""

import datetime
import os
import re

import discord
from discord.ext.commands import Cog

from cogs.utils import fetch_http

GITHUB_RE = re.compile(
    r'https://github\.com/(?P<owner>[^/\s]+)/(?P<repo>[^/\s]+)/pull/'
    r'(?P<pr>[^/\s]+)')


class PullRequestWidgets(Cog):
    def __init__(self, bot, session):
        """Initializes the cog's bot"""

        self.bot = bot
        self.session = session

    @Cog.listener()
    async def on_message(self, message):
        """
        Checks if the message contains a pull request link, then removes the embed,
        then sends a rich embed to Discord
        """

        gh_match = GITHUB_RE.search(message.content)

        if gh_match and not message.author.bot:
            for gh in GITHUB_RE.finditer(message.content):
                d = gh.groupdict()
                headers = {}
                if 'GITHUB_TOKEN' in os.environ:
                    headers[
                        'Authorization'] = f'token {os.environ["GITHUB_TOKEN"]}'
                pull_request = await fetch_http(
                    self.session,
                    f'https://api.github.com/repos/{d["owner"]}/{d["repo"]}/pulls/{d["pr"]}',
                    'json',
                    headers=headers,
                )

                body = pull_request["body"]
                if len(body) > 512:
                    body = body[:512] + "..."

                embed = discord.Embed(
                    title=f'{pull_request["title"]} (#{pull_request["number"]})',
                    description=body,
                    url=pull_request['html_url'],
                    timestamp=datetime.datetime.fromisoformat(pull_request['created_at'][:-1]),
                    color=0x111111,
                ).set_author(
                    name=f'{d["owner"]}/{d["repo"]}',
                    url=f'https://github.com/{d["owner"]}/{d["repo"]}',
                ).add_field(
                    name="Status",
                    value='Merged' if pull_request['merged'] else pull_request['state'].capitalize(),
                    inline=True,
                ).add_field(
                    name="Additions",
                    value=str(pull_request['additions']),
                    inline=True,
                ).add_field(
                    name="Deletions",
                    value=str(pull_request['deletions']),
                    inline=True,
                ).add_field(
                    name="Files Changed",
                    value=str(pull_request['changed_files']),
                    inline=True,
                ).add_field(
                    name="Commits",
                    value=str(pull_request['commits']),
                    inline=True,
                ).set_footer(
                    text=f'Pull request created by {pull_request["user"]["login"]}',
                    icon_url=pull_request['user']['avatar_url'],
                )

                if pull_request["merged"]:
                    embed = embed.add_field(
                        name='Merged By',
                        value=pull_request['merged_by']['login'],
                        inline=True,
                    )
                else:
                    embed = embed.add_field(
                        name='State',
                        value='Mergeable' if pull_request['mergeable'] else 'Not Mergeable',
                        inline=True,
                    )

                await message.channel.send(embed=embed)

            await message.edit(suppress=True)
