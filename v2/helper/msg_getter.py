import re
import time

from telebot import TeleBot, types
from telebot.apihelper import ApiTelegramException

import conf



bot = TeleBot(conf.BOT_TOKEN)
admin_id = conf.ADMIN_ID

db_channel = bot.get_chat(conf.CHANNEL_ID)
bot.db_channel = db_channel

def get_message_x(client, chat_id, message_id):
    try:
        return client.forward_message(chat_id=conf.DUMB_CHANNEL_ID, from_chat_id=chat_id, message_id=message_id)

    except ApiTelegramException as e:
        if 'Too Many Requests' in str(e):
            time.sleep(int(re.search(r'\d+', str(e)).group()))

            return client.forward_message(chat_id=conf.DUMB_CHANNEL_ID, from_chat_id=chat_id, message_id=message_id)
        else:
            print(f"Failed to retrieve message: {e}")
            return None

def get_messages(client, message_ids):
    messages = []
    for message_id in message_ids:
        msg = get_message_x(client, client.db_channel.id, message_id)
        if msg:
            messages.append(msg)
    return messages

def get_message_id(message):
    if message.forward_from_chat and message.forward_from_chat.id == bot.db_channel.id:
        return message.forward_from_message_id
    elif message.forward_from_chat or message.forward_sender_name or not message.text:
        return 0
    else:
        pattern = r"https://t.me/(?:c/)?(.*)/(\\d+)"
        matches = re.match(pattern, message.text)
        if not matches:
            return 0
        channel_id = matches.group(1)
        msg_id = int(matches.group(2))
        if channel_id.isdigit():
            if f"-100{channel_id}" == str(bot.db_channel.id):
                return msg_id
        elif channel_id == bot.db_channel.username:
            return msg_id
    return 0
