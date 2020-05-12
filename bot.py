'''
Git the lines

A Discord bot that removes embeds and prints out specific lines of code
when a GitHub or GitLab link is sent
'''

import os
import base64
import re
from datetime import datetime

import requests
import discord
from discord.utils import find
from discord.ext import commands

bot = commands.Bot(';')
bot.remove_command('help')

start_time = None

github_re = re.compile(
    r'https:\/\/github\.com\/(?P<repo>.+)\/blob\/(?P<branch>.+?)\/(?P<file_path>.+?)' +
    r'(?P<extension>\.(?P<language>.+))*#L(?P<start_line>[0-9]+)(-L(?P<end_line>[0-9]+))*'
)

gitlab_re = re.compile(
    r'https:\/\/gitlab\.com\/(?P<repo>.+)\/\-\/blob\/(?P<branch>.+)\/(?P<file_path>.+?)' +
    r'(?P<extension>\.(?P<language>.+))*#L(?P<start_line>[0-9]+)(-(?P<end_line>[0-9]+))*'
)


@bot.command()
async def github(ctx):
    '''
    Sends the link to the bot's GitHub repo
    '''

    await ctx.send('https://github.com/dolphingarlic/git-the-lines')


@bot.command()
async def about(ctx):
    '''
    Sends information about the bot
    '''

    info = await bot.application_info()
    embed = discord.Embed(
        title=f'{info.name}',
        description=f'{info.description}',
        colour=0x1aaae5,
    ).add_field(
        name='Guild Count',
        value=len(bot.guilds),
        inline=True
    ).add_field(
        name='User Count',
        value=len(bot.users),
        inline=True
    ).add_field(
        name='Uptime',
        value=f'{datetime.now() - start_time}',
        inline=True
    ).add_field(
        name='Latency',
        value=f'{round(bot.latency * 1000, 2)}ms',
        inline=True
    ).set_footer(text=f'Made by {info.owner}', icon_url=info.owner.avatar_url)

    await ctx.send(embed=embed)


@bot.command()
async def stats(ctx):
    '''
    Same as ;about
    '''

    await about(ctx)


@bot.command()
async def help(ctx):
    '''
    Sends a help message
    '''

    info = await bot.application_info()
    embed = discord.Embed(
        title='Help',
        description='Just send the link to the snippet - no need for extra commands! *Git the lines* even highlights the code for you',
        colour=0x41c03f
    ).add_field(
        name='`;about`',
        value='About *Git the lines*',
        inline=True
    ).add_field(
        name='`;invite` or `;topgg`',
        value='Bot invite link',
        inline=True
    ).add_field(
        name='`;help`',
        value='Shows this message',
        inline=True
    ).add_field(
        name='`;ping`',
        value='Check the bot\'s latency',
        inline=True
    )

    await ctx.send(embed=embed)


@bot.command()
async def invite(ctx):
    '''
    Sends a bot invite link
    '''

    try:
        invite = await bot.fetch_invite(url='https://top.gg/bot/708364985021104198')
        await ctx.send(invite)
    except:
        await ctx.send('<https://discord.com/api/oauth2/authorize?client_id=708364985021104198&permissions=75776&scope=bot>')


@bot.command()
async def topgg(ctx):
    '''
    Sends a bot invite link
    '''

    await invite(ctx)


@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000, 2)}ms')


@bot.event
async def on_message(message):
    '''
    Checks if the message starts is a GitHub snippet, then removes the embed,
    then sends the snippet in Discord
    '''

    gh_match = github_re.search(message.content)
    gl_match = gitlab_re.search(message.content)
    if (gh_match or gl_match) and message.author.id != bot.user.id:
        if gh_match:
            d = gh_match.groupdict()
            response_json = requests.get(
                f'https://api.github.com/repos/{d["repo"]}/contents/{d["file_path"]}' +
                f'{d["extension"] if d["extension"] else ""}?ref={d["branch"]}',
                headers={'Accept': 'application/vnd.github.v3+json'}
            ).json()
        else:
            d = gl_match.groupdict()
            for x in d:
                if d[x]:
                    d[x] = d[x].replace('/', '%2F').replace('.', '%2E')
            response_json = requests.get(
                f'https://gitlab.com/api/v4/projects/{d["repo"]}/repository/files/{d["file_path"]}' +
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

        required = list(map(lambda x: x.replace('\t', '    '),
                            split_file_contents[start_line - 1:end_line]))

        while all(line.startswith(' ') for line in required):
            required = list(map(lambda line: line[1:], required))

        required = '\n'.join(required).rstrip().replace('`', r'\`')

        if len(required) != 0:
            if len(required) > 2000:
                await message.channel.send(
                    'Sorry, Discord has a 2000 character limit. Please send a shorter ' +
                    'snippet or split the big snippet up into several smaller ones :slight_smile:'
                )
            else:
                await message.channel.send(f'```{d["language"]}\n{required}```')
        else:
            await message.channel.send('``` ```')
        await message.edit(suppress=True)
    else:
        await bot.process_commands(message)


@bot.event
async def on_guild_join(guild):
    '''
    Sends a nice message when added to a new server
    '''

    general = find(lambda x: x.name == 'general',  guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        embed = discord.Embed(
            title='Thanks for adding me to your server! :heart:',
            description='To get started, simply send a GitHub or GitLab snippet link, or type `;help` for a list of commands',
            colour=0x2ac99e
        ).add_field(
            name='Simple and Unobtrusive',
            value='Git the lines runs automatically in the background and listens for commands and snippet links',
            inline=False
        ).add_field(
            name='Contribute',
            value='We gladly accept contributions. To get started, ' +
            'check out [Git the line\'s GitHub repo](https://github.com/dolphingarlic/git-the-lines)',
            inline=False
        ).add_field(
            name='Have fun!',
            value=':zap:',
            inline=False
        )
        await general.send(embed=embed)


@bot.event
async def on_ready():
    '''
    Just prints when the bot is ready
    '''

    global start_time
    start_time = datetime.now()

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='for snippet links and ;help'))
    print(f'{bot.user} has connected to Discord!')


bot.run(os.environ['DISCORD_TOKEN'])
