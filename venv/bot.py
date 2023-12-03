import io
import json
import os
import random
import re
import sqlite3

import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

import waifuGame

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
client = commands.Bot(command_prefix='!', intents=intents)
database = sqlite3.connect('waifugame.db')
cursor = database.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS waifu_info (waifu_id TEXT, name TEXT, series TEXT, rarity INTEGER)')
cursor.execute('Create TABLE IF NOT EXISTS registered_users (user_id TEXT, server_id TEXT)')


def run_discord_bot():
    token = os.getenv('DISCORD_TOKEN')

    @client.event
    async def on_ready():
        print(f'{client.user} is now running')
        activity = discord.Activity(name='with your feelings', type=discord.ActivityType.playing)
        await client.change_presence(activity=activity, status=discord.Status.online)
        try:
            synced = await client.tree.sync()
            print(f'Synced {len(synced)} commands')
        except Exception as e:
            print(f'Failed to sync commands: {e}')

    @client.tree.command(name='Roll', description='Rolls a random waifu, can be claimed using any reaction')
    async def roll(ctx):
        await ctx.response.defer(ephemeral=True)
        embed, paginator, images = waifuGame.generatewaifu()
        await ctx.followup.send(embed=embed)

    @client.tree.command(name='allcommands', description='Shows a list of commands')
    async def allcommands(ctx):
        await ctx.response.defer(ephemeral=False)
        embed = discord.Embed(title='Commands', color=0x00ff00)
        for command in client.tree.get_commands():
            embed.add_field(name=command.name, value=command.description, inline=False)
        await ctx.followup.send(embed=embed)

    client.run(token)
