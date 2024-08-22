import aiohttp
import asyncio
import os
import discord
from discord.ext import commands, tasks
from bs4 import BeautifulSoup


token = os.getenv('token')

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ID голосового канала и канала для отправки статистики
VOICE_CHANNEL_ID = 1275678602238758953  # Замените на реальный ID вашего голосового канала
STATISTICS_CHANNEL_ID = 1134295768619032617  # Замените на реальный ID текстового канала для статистики

async def fetch_player_count():
    try:
        url = 'https://tsarvar.com/ru/servers/gta-samp/80.66.82.147:7777'
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    players_count = soup.find(class_='srvPage-countCur').text.strip()
                    return int(players_count)
                else:
                    print(f"Error fetching data: {response.status}")
                    return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

@tasks.loop(seconds=60)  # Обновлять каждые 60 секунд
async def update_voice_channel_name():
    guild = bot.guilds[0]
    channel = guild.get_channel(VOICE_CHANNEL_ID)

    if channel is not None:
        players_count = await fetch_player_count()
        if players_count is not None:
            new_name = f"{players_count} из 700 игроков"
        else:
            new_name = "Error fetching players"

        await channel.edit(name=new_name)
        print(f"Channel name updated to: {new_name}")
    else:
        print(f"Channel with ID {VOICE_CHANNEL_ID} not found.")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    update_voice_channel_name.start()

@bot.event
async def on_ready():
        print(f"Logged in as {bot.user.name}")
        update_voice_channel_name.start()



# Запуск бота
bot.run(token)
