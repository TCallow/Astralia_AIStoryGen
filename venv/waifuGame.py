import os
from dotenv import load_dotenv

import aiohttp
import json
import sqlite3
import discord
from discord.ext import commands

load_dotenv()
database = sqlite3.connect('waifugame.db')
cursor = database.cursor()


async def generatewaifu():
    url = "https://waifu.it/api/waifu"
    headers = {
        "Authorization": os.getenv("WAIFU_KEY"),
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            parsed_data = await response.json()
            name = parsed_data["names"]["en"]
            nickname = parsed_data["names"]["alt"]
            series = parsed_data["from"]["name"]
            waifu_id = str(parsed_data["_id"])
            fav = parsed_data["statistics"]["fav"]
            love = parsed_data["statistics"]["love"]
            hate = parsed_data["statistics"]["hate"]
            upvotes = parsed_data["statistics"]["upvote"]
            downvotes = parsed_data["statistics"]["downvote"]
            images = parsed_data["images"]

            paginator = commands.Paginator(prefix="", suffix="")
            paginator.add_line(name)
            paginator.add_line(series)
            if nickname is not None:
                paginator.add_line("Also known as: " + nickname)
            for image in images:
                paginator.add_line("")
                paginator.add_line(f"![Image]({image})")
            embed = discord.Embed(description=paginator.pages[0])
            embed.set_image(url=images[0])
            embed.set_footer(text=f"page 1 of {len(paginator.pages)}")

            cursor.execute('SELECT * FROM waifu_info WHERE waifu_id = ?', (waifu_id,))
            if cursor.fetchone() is None:
                print("This character either doesn't exist or data has changed, creating new entry")
                addwaifutodb(waifu_id, name, series, fav, love, hate, upvotes, downvotes)
                return embed, paginator, images
            else:
                print("Waifu already in database, skipping database creation")
                return embed, paginator, images


def addwaifutodb(waifu_id, name, series, fav, love, hate, upvotes, downvotes):
    cursor.execute("INSERT INTO waifu_info VALUES (?,?,?,?,?,?,?,?)",
                   (waifu_id, name, series, fav, love, hate, upvotes, downvotes))
    database.commit()
