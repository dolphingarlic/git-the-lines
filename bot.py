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
    r'https:\/\/github\.com\/(.+)\/blob\/(.+?)\/(.+?)(\.(.+))*#L([0-9]+)(-L([0-9]+))*')


@client.event
async def on_message(message):
    '''
    Checks if the message starts is a GitHub snippet, then removes the embed, then sends the snippet in Discord
    '''

    match = pattern.search(message.content)
    if match:
        response_json = requests.get(
            f'https://api.github.com/repos/{match.group(1)}/contents/{match.group(3)}{match.group(4) if match.group(4) else ""}?ref={match.group(2)}').json()
        file_contents = base64.b64decode(
            response_json['content']).decode('utf-8')

        if match.group(7):
            start_line = int(match.group(6))
            end_line = int(match.group(8))
        else:
            start_line = end_line = int(match.group(6))

        split_file_contents = file_contents.split('\n')

        required = split_file_contents[start_line - 1:end_line]

        while all(line.startswith('\t') for line in required) or all(line.startswith(' ') for line in required):
            required = list(map(lambda line: line[1:], required))

        required = '\n'.join(required).rstrip()

        await message.edit(suppress=True)
        if (len(required) != 0):
            await message.channel.send(f'```{match.group(5)}\n{required}\n```')


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

client.run(os.environ['DISCORD_TOKEN'])
