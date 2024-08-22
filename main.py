import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

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

# Переменные для хранения предыдущего количества игроков
previous_players_count = None
last_update_time = None

def fetch_player_count():
    try:
        url = 'https://tsarvar.com/ru/servers/gta-samp/80.66.82.147:7777'
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        players_count = soup.find(class_='srvPage-countCur').text.strip()

        return int(players_count)
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def calculate_percentage_change(previous, current):
        """Вычисление процентного изменения."""
        if previous is None or previous == 0:
            return 0
        return ((current - previous) / previous) * 100

@tasks.loop(seconds=60)
async def update_voice_channel_name():
        global previous_players_count, last_update_time

        guild = bot.guilds[0]
        channel = guild.get_channel(VOICE_CHANNEL_ID)
        stats_channel = guild.get_channel(STATISTICS_CHANNEL_ID)

        if channel is not None:
            players_count = fetch_player_count()
            if players_count is not None:
                new_name = f"{players_count} из 700 игроков"
                await channel.edit(name=new_name)
                print(f"Channel name updated to: {new_name}")

                # Если есть предыдущее значение, сравниваем с текущим
                if previous_players_count is not None:
                    change = players_count - previous_players_count
                    percentage_change = calculate_percentage_change(previous_players_count, players_count)
                    now = datetime.now()

                    if last_update_time is not None:
                        time_diff = (now - last_update_time).total_seconds() / 60  # Время в минутах
                    else:
                        time_diff = 0

                    if change > 0:
                        emoji = "📈"  # Увеличение
                    elif change < 0:
                        emoji = "📉"  # Уменьшение
                    else:
                        emoji = "📊"  # Нет изменений

                    change_message = (
                        f"📊 **Статистика изменения онлайна:**\n"
                        f"👤 Было: {previous_players_count} игроков\n"
                        f"👤 Стало: {players_count} игроков\n"
                        f"{emoji} Изменение: {'+' if change > 0 else ''}{change} игроков\n"
                        f"📈 Процентное изменение: {percentage_change:.2f}%\n"
                        f"🕒 За {int(time_diff)} минут"
                    )
                    await stats_channel.send(change_message)

                # Обновляем предыдущее значение и время обновления
                previous_players_count = players_count
                last_update_time = datetime.now()
            else:
                await channel.edit(name="Error 404")
                print("Error fetching player count.")
        else:
            print(f"Channel with ID {VOICE_CHANNEL_ID} not found.")

@bot.event
async def on_ready():
        print(f"Logged in as {bot.user.name}")
        update_voice_channel_name.start()



# Запуск бота
bot.run(token)
