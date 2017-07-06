import requests
import json
import time
from html.parser import HTMLParser
from chatterbot import ChatBot

chatbot = ChatBot(
    'Mokou',
    trainer='chatterbot.trainers.ListTrainer',
    storage_adapter="chatterbot.storage.MongoDatabaseAdapter"
)
#chatbot.storage.drop()

BASE_THREADS_URL = "http://a.4cdn.org/{board}/threads.json"
BASE_THREAD_CONTENT_URL = "http://a.4cdn.org/{board}/thread/{number}.json"
BOARDS = ["a", "b", "g", "soc", "ck", "fit", "co", "v"]


# https://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def get_board():
    yield from BOARDS


def get_board_threads(board):
    r = requests.get(BASE_THREADS_URL.format(board=board))
    threads = json.loads(r.content)
    for page in threads:
        for thread in page['threads']:
            yield thread['no']


def get_thread_content(board, thread):
    r = requests.get(BASE_THREAD_CONTENT_URL.format(board=board, number=thread))
    try:
        posts = json.loads(r.content)
    except:
        print("couldn't load content, skipping")
        return
    for post in posts['posts']:
        if 'no' in post.keys() and 'com' in post.keys():
            yield post['no'], post['com']
        else:
            print('unknown post:', post)


def parse_post(content):
    fragments = content.split('class="quotelink">&gt;&gt;')
    if len(fragments) == 1:
        return None
    else:
        parsed_messages = []
        for fragment in fragments[1:]:
            tokens = fragment.split('</a>')
            if len(tokens) > 1:
                parsed_messages.append(tokens)
            else:
                print("unknown tokens:", content)
        return parsed_messages


def get_messages_in_thread(board, thread):
    messages = dict()
    for no, com in get_thread_content(board, thread):
        parsed_com = parse_post(com)
        if parsed_com:
            messages[str(no)] = {'com': strip_tags(parsed_com[0][1]), 'replies':[]}
        else:
            messages[str(no)] = {'com': strip_tags(com), 'replies': []}

        replies = parse_post(com)
        if replies:
            for data in replies:
                if len(data) != 2:
                    continue
                reply_to, reply = data
                if str(reply_to) in messages.keys():
                    messages[str(reply_to)]['replies'].append(strip_tags(reply))
    return messages


def learn(message, response):
    if len(message) > 256 or len(response) > 256 or len(message) == 0 or len(response) == 0:
        return
    print('learning', message, response)
    chatbot.train([message, response])

for board in BOARDS:
    time.sleep(1)
    threads = get_board_threads(board)
    time.sleep(1)

    for thread in threads:
        start_time = time.time()
        print('Reading thread', thread, 'from', board)
        messages = get_messages_in_thread(board, thread)
        for id in messages.keys():
            message = messages[id]
            if len(message['replies']) > 0:
                for reply in message['replies']:
                    learn(message['com'], reply)
        sleep_time = 1.5 - (time.time() - start_time)
        if sleep_time > 0:
            print('Sleeping', sleep_time)
            time.sleep(sleep_time)

