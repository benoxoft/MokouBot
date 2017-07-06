import discord
import asyncio
from chatterbot import ChatBot
import time

API_KEY = 'THE API KEY'
MENTION = '<@123456789>'

chatbot = ChatBot(
    'Mokou',
    trainer='chatterbot.trainers.ChatterBotCorpusTrainer',
    storage_adapter="chatterbot.storage.MongoDatabaseAdapter"
)

# Train based on the english corpus
#chatbot.storage.drop()
#chatbot.train("chatterbot.corpus.english",
#              "chatterbot.corpus.english.greetings",
#              "chatterbot.corpus.english.conversations"
#              )

client = discord.Client()


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    if message.author.mention != MENTION and 'mokou' in message.content.lower() or MENTION in message.content:
        print("Got", message.content)
        await client.send_typing(message.channel)
        msg = message.content.lower().replace('mokou', '').replace(MENTION, '')
        response = chatbot.get_response(msg)
        time.sleep(len(str(response)) / 1000)
        print("Sending", response)
        if MENTION in message.content:
            await client.send_message(message.channel, response)
        else:
            await client.send_message(message.channel, message.author.mention + ' ' + str(response))

client.run(API_KEY)
