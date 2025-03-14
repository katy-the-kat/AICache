import discord
import requests
import os
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = "" # Your bot token
API_KEY = "" # API-KEY from your AICache Server. Not groq
CHANNEL_ID = 1350020871372275803

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def get_response_from_api(user_message):
    url = "http://localhost:5000/v1/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    payload = {
        "model": "qwen-qwq-32b",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message}
        ]
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        bot_response = data['choices'][0]['text']
        tokens_per_second = data['tokens_per_second']
        cached = data['cached']
        return bot_response, tokens_per_second, cached
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return "Sorry, I couldn't get a response right now.", None, None

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.channel.id == CHANNEL_ID:
        user_message = message.content
        bot_response, tokens_per_second, cached = get_response_from_api(user_message)
        if tokens_per_second is not None and cached is not None:
            additional_info = f"\n\nTPS: {tokens_per_second}\nCached: {cached}"
            bot_response += additional_info
        await message.channel.send(bot_response)

client.run(DISCORD_TOKEN)
