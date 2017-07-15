import os

from chatterbot import ChatBot

# configure how the bot train and retrieve responses
chatbot = ChatBot(
    'Mokou',
    trainer='chatterbot.trainers.ListTrainer',
    storage_adapter='chatterbot.storage.MongoDatabaseAdapter'
)

#
PROCESS_POOL_EXECUTOR_COUNT = 3
WAIT_TIME_BEFORE_TYPING = 2
WAIT_TIME_RESPONSE_READY = 0.3

# Images are downloaded from SFW boards. Images are not downloaded from NSFW boards
SFW_BOARDS = ['jp', 'a', 'v',]
NSFW_BOARDS = ['b', 'pol']

# Messages that aren't in the corresponding length will be discarded from the training data
MIN_MESSAGE_LENGTH = 4
MAX_MESSAGE_LENGTH = 256

# Replies that aren't in the corresponding length will be discarded from the training data
MIN_REPLY_LENGTH = 4
MAX_REPLY_LENGTH = 140

# 4chan demand to not make more than one request per second to their API
SLEEP_TIME_4CHAN = 1.2
