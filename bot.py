'''
Git the lines

A Discord bot that removes embeds and prints out specific lines of code
when a GitHub link is sent
'''

import os
import base64
import re

import requests
import discord

client = discord.Client()

pattern = re.compile(
    r'https:\/\/github\.com\/(?P<repo>.+)\/blob\/(?P<branch>.+?)\/(?P<file_path>.+?)' +
    r'(?P<extension>\.(?P<language>.+))*#L(?P<start_line>[0-9]+)(-L(?P<end_line>[0-9]+))*'
)


@client.event
async def on_message(message):
    '''
    Checks if the message starts is a GitHub snippet, then removes the embed,
    then sends the snippet in Discord
    '''

    match = pattern.search(message.content)
    if match and message.author.id != client.user.id:
        d = match.groupdict()
        response_json = requests.get(
            f'https://api.github.com/repos/{d["repo"]}/contents/{d["file_path"]}' +
            f'{d["extension"] if d["extension"] else ""}?ref={d["branch"]}'
        ).json()
        file_contents = base64.b64decode(
            response_json['content']).decode('utf-8')

        if d['end_line']:
            start_line = int(d['start_line'])
            end_line = int(d['end_line'])
        else:
            start_line = end_line = int(d['start_line'])

        split_file_contents = file_contents.split('\n')

        required = split_file_contents[start_line - 1:end_line]

        while all(line.startswith('\t') or line.startswith(' ') for line in required):
            required = list(map(lambda line: line[1:], required))

        required = '\n'.join(required).rstrip().replace('`', r'\`')

        if len(required) != 0:
            await message.channel.send(f'```{d["language"]}\n{required}```')
        else:
            await message.channel.send('``` ```')
        await message.edit(suppress=True)


@client.event
async def on_ready():
    '''
    Just prints when the bot is ready
    '''

    print(f'{client.user} has connected to Discord!')

client.run(os.environ['DISCORD_TOKEN'])
