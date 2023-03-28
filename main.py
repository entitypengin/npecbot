#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import os

import discord
from discord.ext import tasks

import era
from server import keep_alive
import wikiwiki


discord_token = os.environ["DISCORD_TOKEN"]
wikiwiki_password = os.environ["WIKIWIKI_PASSWORD"]
bot_channel_id = int(os.environ["BOT_CHANNEL_ID"])

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

wikiwiki_token = ""


@tasks.loop(seconds=60)
async def loop():
    now = datetime.datetime.now()
    if (now.hour, now.minute) == (15, 0):
        global wikiwiki_token
        wikiwiki_token = wikiwiki.get_token(wikiwiki_password)
        await client.get_channel(bot_channel_id).send(era.get_time())


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    global wikiwiki_token
    wikiwiki_token = wikiwiki.get_token(wikiwiki_password)
    print(f"{wikiwiki_token=}")
    loop.start()


@client.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content.startswith("npec/help"):
        await message.channel.send("https://entitypengin.github.io/metroprojbot/")
    if message.content.startswith("npec/time"):
        await message.channel.send(era.get_time())
    if message.content.startswith("npec/char"):
        name = message.content.split(" ", 1)[1]
        await message.channel.send(wikiwiki.get_character(wikiwiki_token, name))


keep_alive()

client.run(discord_token)
