# Git the lines

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/85bfb01083994b77b2d074f327fbfd8d)](https://app.codacy.com/manual/dolphingarlic/git-the-lines?utm_source=github.com&utm_medium=referral&utm_content=dolphingarlic/git-the-lines&utm_campaign=Badge_Grade_Dashboard)
[![Build Status](https://travis-ci.com/dolphingarlic/git-the-lines.svg?branch=master)](https://travis-ci.com/dolphingarlic/git-the-lines)
[![Up Status](https://top.gg/api/widget/status/708364985021104198.svg)](https://top.gg/bot/708364985021104198)
[![Servers](https://top.gg/api/widget/servers/708364985021104198.svg)](https://top.gg/bot/708364985021104198)
[![inviteme](https://img.shields.io/static/v1?style=flat&logo=discord&logoColor=FFF&label=&message=invite%20me&color=7289DA)](https://top.gg/bot/708364985021104198)

A Discord bot that prints out the lines referenced in a GitHub or GitLab link

## Usage

Just send the link to the snippet - no need for extra commands! Git the lines even highlights the code for you

![The bot in action](git-the-lines.png)

### Features

- GitHub
  - Public repos and gists
  - Private repos and gists (if self-hosting)
- GitLab
  - Public repos
- BitBucket
  - Public repos

## Commands

### Ping

Command: `g;ping`.

Action: Pings bot, returns bot delay in ms.

### About

Command: `g;about`.

Aliases: `g;stats`.

Action: Shows bot statistics and technical data.

### Help

Command: `g;help`.

Action: Shows help information.

### Invite

Command: `g;invite`.

Aliases: `g;topgg`.

Action: Sends a bot invite link.

### GitHub Repo

Command: `g;github`.

Aliases: `g;source`.

Action: Sends the bot GitHub repo link

## Get the bot

[Use this link](https://top.gg/bot/708364985021104198) to add the bot to your server

Alternatively, you can self-host the bot using Heroku, pythonanywhere, or any other hosting service. Simply create a file named `.env` and set `DISCORD_TOKEN` to your Discord bot token

## Contribute

We gladly accept any (constructive) contributions. Feel free to open issues and pull requests!
