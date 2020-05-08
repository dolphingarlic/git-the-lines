'''
Git the lines

A Discord bot that removes embeds and prints out specific lines of code
when a GitHub link is sent
'''

import os
import base64

import requests
import discord
from pygments.lexers import guess_lexer_for_filename

client = discord.Client()


def remove_one_tab(s):
    return s[1:]


@client.event
async def on_message(message):
    if message.content.startswith('https://github.com/') and '#L' in message.content:
        url = message.content.replace('https://github.com/', '')
        lines = url[url.rfind('#'):]
        url = url.replace(lines, '')

        query = url.split('/')
        repo = '/'.join(query[:2])
        branch = query[3]
        file_path = '/'.join(query[4:])

        response_json = requests.get(
            f'https://api.github.com/repos/{repo}/contents/{file_path}?ref={branch}').json()
        file_contents = base64.b64decode(
            response_json['content']).decode('utf-8')

        language = guess_lexer_for_filename(
            query[-1], file_contents).aliases[0]

        if '-' in lines:
            lines = lines.split('-')
            start_line = int(lines[0][lines[0].find('L') + 1:]) - 1
            end_line = int(lines[1][lines[1].find('L') + 1:]) - 1
        else:
            start_line = end_line = int(lines[lines.find('L') + 1:]) - 1

        split_file_contents = file_contents.split('\n')

        required = split_file_contents[start_line:end_line + 1]

        while all(line.startswith('\t') for line in required) or all(line.startswith(' ') for line in required):
            required = list(map(remove_one_tab, required))
        
        required = '\n'.join(required)

        await message.edit(suppress=True)
        await message.channel.send(f'```{language}\n{required}```')


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

client.run(os.environ['DISCORD_TOKEN'])
