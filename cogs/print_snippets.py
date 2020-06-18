"""
Cog that prints out snippets to Discord

Matches each message against a regex and prints the contents
of the first matched snippet url
"""

import os
import re

from discord.ext.commands import Cog

from cogs.utils import fetch_http, revert_to_orig, orig_to_encode, create_message


GITHUB_RE = re.compile(
    r'https://github\.com/(?P<repo>.+?)/blob/(?P<branch>.+?)/' +
    r'(?P<file_path>.+?)#L(?P<start_line>\d+)([-~]L(?P<end_line>\d+))?\b'
)

GITHUB_GIST_RE = re.compile(
    r'https://gist\.github\.com/([^/]*)/(?P<gist_id>[0-9a-zA-Z]+)/*' +
    r'(?P<revision>[0-9a-zA-Z]*)/*#file-(?P<file_path>.+?)' +
    r'-L(?P<start_line>\d+)([-~]L(?P<end_line>\d+))?\b'
)

GITLAB_RE = re.compile(
    r'https://gitlab\.com/(?P<repo>.+?)/\-/blob/(?P<branch>.+?)/' +
    r'(?P<file_path>.+?)#L(?P<start_line>\d+)([-~](?P<end_line>\d+))?\b'
)

BITBUCKET_RE = re.compile(
    r'https://bitbucket\.org/(?P<repo>.+?)/src/(?P<branch>.+?)/' +
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
                d = gh.groupdict()
                headers = {'Accept': 'application/vnd.github.v3.raw'}
                if 'GITHUB_TOKEN' in os.environ:
                    headers['Authorization'] = f'token {os.environ["GITHUB_TOKEN"]}'
                file_contents = await fetch_http(
                    self.session,
                    f'https://api.github.com/repos/{d["repo"]}/contents/{d["file_path"]}?ref={d["branch"]}',
                    'text',
                    headers=headers,
                )
                message_to_send += await create_message(d, file_contents)

            for gh_gist in GITHUB_GIST_RE.finditer(message.content):
                d = gh_gist.groupdict()
                gist_json = await fetch_http(
                    self.session,
                    f'https://api.github.com/gists/{d["gist_id"]}{"/" + d["revision"] if len(d["revision"]) > 0 else ""}',
                    'json',
                )
                for f in gist_json['files']:
                    if d['file_path'] == f.lower().replace('.', '-'):
                        d['file_path'] = f
                        file_contents = await fetch_http(
                            self.session,
                            gist_json['files'][f]['raw_url'],
                            'text',
                        )
                        message_to_send += await create_message(d, file_contents)
                        break

            for gl in GITLAB_RE.finditer(message.content):
                d = gl.groupdict()
                await orig_to_encode(d)
                headers = {}
                if 'GITLAB_TOKEN' in os.environ:
                    headers['PRIVATE-TOKEN'] = os.environ["GITLAB_TOKEN"]
                file_contents = await fetch_http(
                    self.session,
                    f'https://gitlab.com/api/v4/projects/{d["repo"]}/repository/files/{d["file_path"]}/raw?ref={d["branch"]}',
                    'text',
                    headers=headers,
                )
                await revert_to_orig(d)
                message_to_send += await create_message(d, file_contents)

            for bb in BITBUCKET_RE.finditer(message.content):
                d = bb.groupdict()
                await orig_to_encode(d)
                file_contents = await fetch_http(
                    self.session,
                    f'https://bitbucket.org/{d["repo"]}/raw/{d["branch"]}/{d["file_path"]}',
                    'text',
                )
                await revert_to_orig(d)
                message_to_send += await create_message(d, file_contents)

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
