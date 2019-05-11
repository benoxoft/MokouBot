import requests
import json
import os
import shutil
import time
from html.parser import HTMLParser

from config import \
    chatbot, \
    trainer, \
    SFW_BOARDS, \
    NSFW_BOARDS, \
    SLEEP_TIME_4CHAN, \
    MIN_MESSAGE_LENGTH, \
    MAX_MESSAGE_LENGTH, \
    MIN_REPLY_LENGTH, \
    MAX_REPLY_LENGTH

BASE_THREADS_URL = 'http://a.4cdn.org/{board}/threads.json'
BASE_THREAD_CONTENT_URL = 'http://a.4cdn.org/{board}/thread/{number}.json'
BASE_IMAGE_URL = 'http://i.4cdn.org/{board}/{filename}'


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
    s.feed(html.replace('<br>', ' ').strip())
    return s.get_data()


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
            if 'tim' in post.keys() and 'ext' in post.keys():
                yield post['no'], post['com'], str(post['tim']) + post['ext']
            else:
                yield post['no'], post['com'], ''


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
                print('unknown tokens:', content)
        return parsed_messages


def save_image_file(board, filename):
    if not filename:
        return
    if os.path.exists(os.path.join('images', filename)):
        return
    if 'webm' in filename:
        return

    r = requests.get(BASE_IMAGE_URL.format(board=board, filename=filename), stream=True)
    with open(os.path.join('images', filename), 'wb') as out_file:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, out_file)


def get_messages_in_thread(board, thread):
    messages = dict()
    for no, com, filename in get_thread_content(board, thread):
        parsed_com = parse_post(com)
        if parsed_com:
            messages[str(no)] = {'com': strip_tags(parsed_com[0][1]), 'replies': [], 'filename': filename}
        else:
            messages[str(no)] = {'com': strip_tags(com), 'replies': [], 'filename': filename}

        replies = parse_post(com)
        if replies:
            for data in replies:
                if len(data) != 2:
                    continue
                reply_to, reply = data
                if str(reply_to) in messages.keys():
                    messages[str(reply_to)]['replies'].append((strip_tags(reply), filename))
    return messages


def learn(message, msg_filename, response, filename):
    print('learning', message, response)
    if msg_filename:
        message += ' <img>' + msg_filename
    if filename:
        response += ' <img>' + filename

    trainer.train([message, response])


def create_training_dataset(boards, save_images):
    training_data = []

    if not os.path.exists('images'):
        os.mkdir('images')

    for board in boards:
        time.sleep(1)
        threads = get_board_threads(board)
        time.sleep(1)

        for thread in threads:
            start_time = time.time()
            print('Reading thread', thread, 'from /' + board + '/')

            messages = get_messages_in_thread(board, thread)

            for id in messages.keys():
                message = messages[id]
                if len(message['replies']) == 0:
                    continue
                for reply, filename in message['replies']:
                    if (len(message['com']) > MAX_MESSAGE_LENGTH or
                        len(reply) > MAX_REPLY_LENGTH or
                        len(message['com']) < MIN_MESSAGE_LENGTH or
                            len(reply) < MIN_REPLY_LENGTH):
                        continue
                    training_data.append([message['com'], message['filename'], reply, filename])

                    if save_images:
                        save_image_file(board, filename)

            sleep_time = SLEEP_TIME_4CHAN - (time.time() - start_time)
            if sleep_time > 0:
                print('Sleeping', sleep_time)
                time.sleep(sleep_time)
    return training_data


def learn_from_dataset(training_data):
    for message, msg_filename, response, filename in training_data:
        learn(message, msg_filename, response, filename)


def main():
    sfw_data = create_training_dataset(SFW_BOARDS, True)
    with open('sfw_data.json', 'w') as datafile:
        #sfw_data = json.load(datafile)
        json.dump(sfw_data, datafile)

    nsfw_data = create_training_dataset(NSFW_BOARDS, False)
    with open('nsfw_data.json', 'w') as datafile:
        #nsfw_data = json.load(datafile)
        json.dump(nsfw_data, datafile)

    chatbot.storage.drop()
    learn_from_dataset(sfw_data)
    learn_from_dataset(nsfw_data)


if __name__ == '__main__':
    main()
