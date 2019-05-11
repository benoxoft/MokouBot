import asyncio
from concurrent.futures import ProcessPoolExecutor
import os
import sys

import discord

from config import chatbot, PROCESS_POOL_EXECUTOR_COUNT, WAIT_TIME_BEFORE_TYPING, WAIT_TIME_RESPONSE_READY


print("Starting process")
client = discord.Client()
ppool = ProcessPoolExecutor(PROCESS_POOL_EXECUTOR_COUNT)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


def generate_response(message):
    return chatbot.get_response(message)


async def reply_to_message(message):
    print("Got", message.content)
    msg = message.content.lower().replace(client.user.name.lower(), '').replace(client.user.mention, '')
    response_gen = asyncio.get_event_loop().run_in_executor(ppool, generate_response, msg)
    await asyncio.sleep(WAIT_TIME_BEFORE_TYPING)
    while not response_gen.done():
        await asyncio.sleep(WAIT_TIME_RESPONSE_READY)
        await message.channel.trigger_typing()
    response = response_gen.result()
    print("Sending", response)
    filename = ''
    if ' <img>' in str(response):
        response, filename = str(response).split(' <img>')
    await message.channel.send(message.author.mention + ' ' + str(response))
    print('file:', filename)
    if filename and os.path.exists(os.path.join('images', filename)):
        with open(os.path.join('images', filename), 'rb') as f:
            await message.channel.send(f)


@client.event
async def on_message(message):
    if client.user.mention == message.author.mention:
        return
    if not (client.user.name.lower() in message.content.lower() or client.user.mention in message.content):
        return

    await reply_to_message(message)

if __name__ == '__main__':
    if not os.path.exists('API_KEY.txt'):
        print("Couldn't find API_KEY.txt.")
        print("Create a file named API_KEY.txt and paste your API key in the file to connect the bot to Discord")
        sys.exit(0)

    with open('API_KEY.txt', 'r') as api_key_file:
        API_KEY = api_key_file.read().strip()

    while True:
        try:
            client.run(API_KEY)
        except Exception as e:
            print(e)
            import time
            time.sleep(10)
            client = discord.Client()
