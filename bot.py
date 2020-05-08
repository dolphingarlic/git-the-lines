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


@client.event
async def on_message(message):
    '''
    Checks if the message starts is a GitHub snippet, then removes the embed, then sends the snippet in Discord
    '''

    match = re.match(
        r'https:\/\/github\.com\/(.+)\/blob\/(.+?)\/(.+?)\.(.+)#L([0-9]+)(-L([0-9]+))*', message.content)
    if match:
        response_json = requests.get(
            f'https://api.github.com/repos/{match.group(1)}/contents/{match.group(3)}.{match.group(4)}?ref={match.group(2)}').json()
        file_contents = base64.b64decode(
            response_json['content']).decode('utf-8')

        if match.group(6):
            start_line = int(match.group(5))
            end_line = int(match.group(7))
        else:
            start_line = end_line = int(match.group(5))

        split_file_contents = file_contents.split('\n')

        required = split_file_contents[start_line:end_line + 1]

        while all(line.startswith('\t') for line in required) or all(line.startswith(' ') for line in required):
            required = list(map(lambda line: line[1:], required))

        required = '\n'.join(required)

        await message.edit(suppress=True)
        await message.channel.send(f'```{match.group(4)}\n{required}\n```')


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

client.run(os.environ['DISCORD_TOKEN'])
