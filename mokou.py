import discord
import asyncio
from chatterbot import ChatBot
from concurrent.futures import ProcessPoolExecutor

API_KEY = ''

print("Starting process")
client = discord.Client()
ppool = ProcessPoolExecutor(3)  # Create a ProcessPool with 2 processes

chatbot = ChatBot(
    'Mokou',
    trainer='chatterbot.trainers.ChatterBotCorpusTrainer',
    storage_adapter="chatterbot.storage.MongoDatabaseAdapter"
)


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
    msg = message.content.lower().replace('mokou', '').replace(client.user.mention, '')
    response_gen = asyncio.get_event_loop().run_in_executor(ppool, generate_response, msg)
    await asyncio.sleep(2)
    while not response_gen.done():
        await asyncio.sleep(1)
        await client.send_typing(message.channel)
    response = response_gen.result()
    print("Sending", response)
    if client.user.mention in message.content:
        await client.send_message(message.channel, response)
    else:
        await client.send_message(message.channel, message.author.mention + ' ' + str(response))


@client.event
async def on_message(message):
    if client.user.mention == message.author.mention:
        return
    if not ('mokou' in message.content.lower() or client.user.mention in message.content):
        return

    await reply_to_message(message)

if __name__ == '__main__':
    while True:
        try:
            client.run(API_KEY)
        except:
            client = discord.Client()
