"""
Cog that prints out snippets to Discord
"""

import os
import re

import aiohttp
from discord.ext.commands import Cog


class PrintSnippets(Cog):
    def __init__(self, bot):
        self.bot = bot

        self.github_re = re.compile(
            r'https:\/\/github\.com\/(?P<repo>.+)\/blob\/(?P<branch>.+?)\/' +
            r'(?P<file_path>.+?(\.(?P<language>.+))*)#L(?P<start_line>[0-9]+)(-L(?P<end_line>[0-9]+))*'
        )
        self.github_gist_re = re.compile(
            r'https:\/\/gist\.github\.com\/([^\/]*)\/(?P<gist_id>[0-9a-zA-Z]+)\/*(?P<revision>[0-9a-zA-Z]*)\/*#file-(?P<file_name>.+?)' +
            r'-L(?P<start_line>[0-9]+)(-L(?P<end_line>[0-9]+))*'
        )
        self.gitlab_re = re.compile(
            r'https:\/\/gitlab\.com\/(?P<repo>.+)\/\-\/blob\/(?P<branch>.+)\/' +
            r'(?P<file_path>.+?(\.(?P<language>.+)))*#L(?P<start_line>[0-9]+)(-(?P<end_line>[0-9]+))*'
        )

    async def fetch(self, session, url, format='text', **kwargs):
        """
        Uses aiohttp to make http GET requests
        """

        async with session.get(url, **kwargs) as response:
            if format == 'text':
                return await response.text()
            elif format == 'json':
                return await response.json()

    @Cog.listener()
    async def on_message(self, message):
        """
        Checks if the message starts is a GitHub snippet, then removes the embed,
        then sends the snippet in Discord
        """

        gh_match = self.github_re.search(message.content)
        gh_gist_match = self.github_gist_re.search(message.content)
        gl_match = self.gitlab_re.search(message.content)

        if (gh_match or gh_gist_match or gl_match) and message.author.id != self.bot.user.id:
            if gh_match:
                d = gh_match.groupdict()
                headers = {'Accept': 'application/vnd.github.raw'}
                if 'GITHUB_TOKEN' in os.environ:
                    headers['Authorization'] = f'token {os.environ["GITHUB_TOKEN"]}'
                async with aiohttp.ClientSession() as session:
                    file_contents = await self.fetch(
                        session,
                        f'https://api.github.com/repos/{d["repo"]}/contents/{d["file_path"]}?ref={d["branch"]}',
                        'text',
                        headers=headers,
                    )
            elif gh_gist_match:
                d = gh_gist_match.groupdict()
                headers = {}
                if 'GITHUB_TOKEN' in os.environ:
                    headers['Authorization'] = f'token {os.environ["GITHUB_TOKEN"]}'
                async with aiohttp.ClientSession() as session:
                    gist_json = await self.fetch(
                        session,
                        f'https://api.github.com/gists/{d["gist_id"]}{"/" + d["revision"] if len(d["revision"]) > 0 else ""}',
                        'json',
                        headers=headers,
                    )
                    for f in gist_json['files']:
                        if d['file_name'] == f.lower().replace('.', '-'):
                            d['language'] = gist_json['files'][f]['language']
                            if d['language'] is None:
                                d['language'] = ''
                            file_contents = await self.fetch(
                                session,
                                gist_json['files'][f]['raw_url'],
                                'text',
                                headers=headers,
                            )
                            break
            elif gl_match:
                d = gl_match.groupdict()
                for obj in d:
                    d[obj] = d[obj].replace('/', '%2F').replace('.', '%2E')
                async with aiohttp.ClientSession() as session:
                    file_contents = await self.fetch(
                        session,
                        f'https://gitlab.com/api/v4/projects/{d["repo"]}/repository/files/{d["file_path"]}/raw?ref={d["branch"]}',
                        'text',
                    )

            if d['language'] is None:
                d['language'] = ''

            if d['end_line']:
                start_line = int(d['start_line'])
                end_line = int(d['end_line'])
            else:
                start_line = end_line = int(d['start_line'])

            split_file_contents = file_contents.split('\n')

            if start_line > end_line:
                start_line, end_line = end_line, start_line
            start_line = min(len(split_file_contents), max(1, start_line))
            end_line = min(len(split_file_contents), max(1, end_line))

            required = list(map(lambda x: x.replace('\t', '    '),
                                split_file_contents[start_line - 1:end_line]))

            while all(line.startswith(' ') or len(line) == 0 for line in required):
                required = list(map(lambda line: line[1:], required))
                if all(len(line) == 0 for line in required):
                    break

            required = '\n'.join(required).rstrip().replace('`', r'\`')

            if len(required) != 0:
                if len(required) + len(d['language']) > 1993:
                    await message.channel.send(
                        'Sorry, Discord has a 2000 character limit. Please send a shorter ' +
                        'snippet or split the big snippet up into several smaller ones :slight_smile:'
                    )
                else:
                    await message.channel.send(f'```{d["language"]}\n{required}```')
            else:
                await message.channel.send('``` ```')
            await message.edit(suppress=True)
