import telebot
import sys

from conf import (
    API_HASH,
    APP_ID,
    CHANNEL_ID,
    FORCE_SUB_CHANNEL,
    FORCE_SUB_GROUP,
    LOGGER,
    OWNER,
    TG_BOT_TOKEN,
    TG_BOT_WORKERS,
)

# Initialize the bot
bot = telebot.TeleBot(TG_BOT_TOKEN, parse_mode='HTML')
bot.LOGGER = LOGGER


@bot.message_handler(commands=['start'])
def start_bot(message):
    try:
        usr_bot_me = bot.get_me()
        bot.username = usr_bot_me.username
        bot.namebot = usr_bot_me.first_name
        bot.LOGGER(__name__).info(
            f"TG_BOT_TOKEN detected!\n┌ First Name: {bot.namebot}\n└ Username: @{bot.username}\n——"
        )
    except Exception as e:
        print("error: ",e)
        sys.exit()

    if FORCE_SUB_CHANNEL:
        try:
            info = bot.get_chat(FORCE_SUB_CHANNEL)
            link = bot.export_chat_invite_link(FORCE_SUB_CHANNEL)
            bot.invitelink = link
            bot.LOGGER(__name__).info(
                f"FORCE_SUB_CHANNEL detected!\n┌ Title: {info.title}\n└ Chat ID: {info.id}\n——"
            )
        except Exception as e:
            print("error: ",e)
            sys.exit()

    if FORCE_SUB_GROUP:
        try:
            info = bot.get_chat(FORCE_SUB_GROUP)
            link = bot.export_chat_invite_link(FORCE_SUB_GROUP)
            bot.invitelink2 = link
            bot.LOGGER(__name__).info(
                f"FORCE_SUB_GROUP detected!\n┌ Title: {info.title}\n└ Chat ID: {info.id}\n——"
            )
        except Exception as e:
            print("error: ",e)
            sys.exit()

    try:
        db_channel = bot.get_chat(CHANNEL_ID)
        bot.db_channel = db_channel
        test = bot.send_message(chat_id=db_channel.id, text="Test Message", disable_notification=True)
        bot.delete_message(chat_id=db_channel.id, message_id=test.message_id)
        bot.LOGGER(__name__).info(
            f"CHANNEL_ID Database detected!\n┌ Title: {db_channel.title}\n└ Chat ID: {db_channel.id}\n——"
        )
    except Exception as e:
        print("error: ",e)
        sys.exit()


@bot.message_handler(commands=['stop'])
def stop_bot(message):
    bot.stop_polling()
    bot.LOGGER(__name__).info("Bot stopped.")

