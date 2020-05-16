"""
Cog that gives information about the bot
"""

import os
from datetime import datetime

import discord
from discord.ext.commands import Cog, command


class BotInfo(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.now()

        self.prefix = 'g;'
        if 'BOT_PREFIX' in os.environ:
            self.prefix = os.environ['BOT_PREFIX']

    @command(aliases=['source'])
    async def github(self, ctx):
        """
        Sends the link to the bot's GitHub repo
        """

        await ctx.send('https://github.com/dolphingarlic/git-the-lines')

    @command(aliases=['stats'])
    async def about(self, ctx):
        """
        Sends information about the bot
        """

        info = await self.bot.application_info()
        embed = discord.Embed(
            title=f'{info.name}',
            description=f'{info.description}',
            colour=0x1aaae5,
        ).add_field(
            name='Guild Count',
            value=len(self.bot.guilds),
            inline=True
        ).add_field(
            name='User Count',
            value=len(self.bot.users),
            inline=True
        ).add_field(
            name='Uptime',
            value=f'{datetime.now() - self.start_time}',
            inline=True
        ).add_field(
            name='Latency',
            value=f'{round(self.bot.latency * 1000, 2)}ms',
            inline=True
        ).set_footer(text=f'Made by {info.owner}', icon_url=info.owner.avatar_url)

        await ctx.send(embed=embed)

    @command()
    async def help(self, ctx):
        """
        Sends a help message
        """

        embed = discord.Embed(
            title='Help',
            description='Just send the link to the snippet - no need for extra commands! Git the lines even highlights the code for you',
            colour=0x41c03f
        ).add_field(
            name=f'`{self.prefix}about` or `{self.prefix}stats`',
            value='About Git the lines',
            inline=True
        ).add_field(
            name=f'`{self.prefix}invite` or `{self.prefix}topgg`',
            value='Bot invite link',
            inline=True
        ).add_field(
            name=f'`{self.prefix}help`',
            value='Shows this message',
            inline=True
        ).add_field(
            name=f'`{self.prefix}ping`',
            value='Check the bot\'s latency',
            inline=True
        ).add_field(
            name=f'`{self.prefix}github` or `{self.prefix}source`',
            value='Links to the bot\'s GitHub repo',
            inline=True
        )

        await ctx.send(embed=embed)

    @command(aliases=['topgg'])
    async def invite(self, ctx):
        """
        Sends a bot invite link
        """

        try:
            invite = await self.bot.fetch_invite(url='https://top.gg/bot/708364985021104198')
            await ctx.send(invite)
        except:
            await ctx.send('<https://discord.com/api/oauth2/authorize?client_id=708364985021104198&permissions=75776&scope=bot>')

    @command()
    async def ping(self, ctx):
        """
        Checks latency
        """

        await ctx.send(f'Pong; {round(self.bot.latency * 1000, 2)}ms')

    @Cog.listener()
    async def on_guild_join(self, guild):
        """
        Sends a nice message when added to a new server
        """

        embed = discord.Embed(
            title='Thanks for adding me to your server! :heart:',
            description='To get started, simply send a GitHub or GitLab snippet link, or type `g;help` for a list of commands',
            colour=0x2ac99e
        ).add_field(
            name='Simple and Unobtrusive',
            value='Git the lines runs automatically in the background and listens for commands and snippet links',
            inline=False
        ).add_field(
            name='Contribute',
            value='We gladly accept contributions. To get started, ' +
            'check out [Git the lines\' GitHub repo](https://github.com/dolphingarlic/git-the-lines)',
            inline=False
        ).add_field(
            name='Have fun!',
            value=':zap:',
            inline=False
        )
        await guild.system_channel.send(embed=embed)
