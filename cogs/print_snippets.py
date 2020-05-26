"""
Cog that prints out snippets to Discord
"""

import os
import re

import aiohttp
from discord.ext.commands import Cog


GITHUB_RE = re.compile(
    r'https://github\.com/(?P<repo>.+)/blob/(?P<branch>.+?)/' +
    r'(?P<file_path>.+)#L(?P<start_line>\d+)(-L(?P<end_line>\d+))?\b'
)

GITHUB_GIST_RE = re.compile(
    r'https://gist\.github\.com/([^/]*)/(?P<gist_id>[0-9a-zA-Z]+)/*' +
    r'(?P<revision>[0-9a-zA-Z]*)/*#file-(?P<file_path>.+?)' +
    r'-L(?P<start_line>\d+)(-L(?P<end_line>\d+))?\b'
)

GITLAB_RE = re.compile(
    r'https://gitlab\.com/(?P<repo>.+)/\-/blob/(?P<branch>.+?)/' +
    r'(?P<file_path>.+)*#L(?P<start_line>\d+)(-(?P<end_line>\d+))?\b'
)

BITBUCKET_RE = re.compile(
    r'https://bitbucket\.org/(?P<repo>.+)/src/(?P<branch>.+?)/' +
    r'(?P<file_path>.+)#lines-(?P<start_line>\d+)(:(?P<end_line>\d+))?\b'
)


class PrintSnippets(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_http(self, session, url, format='text', **kwargs):
        """
        Uses aiohttp to make http GET requests
        """

        async with session.get(url, **kwargs) as response:
            if format == 'text':
                return await response.text()
            elif format == 'json':
                return await response.json()

    async def revert_to_orig(self, d):
        """
        Replace URL Encoded values back to their original
        """
        for obj in d:
            if d[obj] is not None:
                d[obj] = d[obj].replace('%2F', '/').replace('%2E', '.')

    async def orig_to_encode(self, d):
        """
        Encode URL Parameters
        """
        for obj in d:
            if d[obj] is not None:
                d[obj] = d[obj].replace('/', '%2F').replace('.', '%2E')

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
        if (gh_match or gh_gist_match or gl_match or bb_match) and message.author.id != self.bot.user.id:
            if gh_match:
                d = gh_match.groupdict()
                headers = {'Accept': 'application/vnd.github.v3.raw'}
                if 'GITHUB_TOKEN' in os.environ:
                    headers['Authorization'] = f'token {os.environ["GITHUB_TOKEN"]}'
                async with aiohttp.ClientSession() as session:
                    file_contents = await self.fetch_http(
                        session,
                        f'https://api.github.com/repos/{d["repo"]}/contents/{d["file_path"]}?ref={d["branch"]}',
                        'text',
                        headers=headers,
                    )
            elif gh_gist_match:
                d = gh_gist_match.groupdict()
                headers = {'Accept': 'application/vnd.github.v3.raw'}
                if 'GITHUB_TOKEN' in os.environ:
                    headers['Authorization'] = f'token {os.environ["GITHUB_TOKEN"]}'
                async with aiohttp.ClientSession() as session:
                    gist_json = await self.fetch_http(
                        session,
                        f'https://api.github.com/gists/{d["gist_id"]}{"/" + d["revision"] if len(d["revision"]) > 0 else ""}',
                        'json',
                        headers=headers,
                    )
                    for f in gist_json['files']:
                        if d['file_path'] == f.lower().replace('.', '-'):
                            d['file_path'] = f
                            file_contents = await self.fetch_http(
                                session,
                                gist_json['files'][f]['raw_url'],
                                'text',
                                headers=headers,
                            )
                            break
                    else:
                        return None
            elif gl_match:
                d = gl_match.groupdict()
                await self.orig_to_encode(d)
                headers = {}
                if 'GITLAB_TOKEN' in os.environ:
                    headers['PRIVATE-TOKEN'] = os.environ["GITLAB_TOKEN"]
                async with aiohttp.ClientSession() as session:
                    file_contents = await self.fetch_http(
                        session,
                        f'https://gitlab.com/api/v4/projects/{d["repo"]}/repository/files/{d["file_path"]}/raw?ref={d["branch"]}',
                        'text',
                        headers=headers,
                    )
                await self.revert_to_orig(d)
            elif bb_match:
                d = bb_match.groupdict()
                await self.orig_to_encode(d)
                async with aiohttp.ClientSession() as session:
                    file_contents = await self.fetch_http(
                        session,
                        f'https://bitbucket.org/{d["repo"]}/raw/{d["branch"]}/{d["file_path"]}',
                        'text',
                    )
                await self.revert_to_orig(d)

            if d['end_line']:
                start_line = int(d['start_line'])
                end_line = int(d['end_line'])
            else:
                start_line = end_line = int(d['start_line'])

            split_file_contents = file_contents.split('\n')

            if start_line > end_line:
                start_line, end_line = end_line, start_line
            if start_line > len(split_file_contents) or end_line < 1:
                return None
            start_line = max(1, start_line)
            end_line = min(len(split_file_contents), end_line)

            if end_line - start_line > 49:
                await message.channel.send(
                    'Please limit your snippets to 50 lines to prevent spam :slight_smile:'
                )
                return None

            required = list(map(lambda x: x.replace('\t', '    '),
                                split_file_contents[start_line - 1:end_line]))

            while all(line.startswith(' ') or len(line) == 0 for line in required):
                required = list(map(lambda line: line[1:], required))
                if all(len(line) == 0 for line in required):
                    break

            required = '\n'.join(required).rstrip().replace('`', r'\`')

            language = d['file_path'].split('/')[-1].split('.')[-1]
            if not language.replace('-', '').replace('+', '').isalnum():
                language = ''

            if len(required) != 0:
                if len(required) + len(language) > 1993:
                    await message.channel.send(
                        'Sorry, Discord has a 2000 character limit. Please send a shorter ' +
                        'snippet or split the big snippet up into several smaller ones :slight_smile:'
                    )
                else:
                    await message.channel.send(f'```{language}\n{required}```')
            else:
                await message.channel.send('``` ```')
            await message.edit(suppress=True)
