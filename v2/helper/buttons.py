from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup,ReplyKeyboardRemove
from data.alchemy import get_channel
import conf
from telebot import TeleBot

bot = TeleBot(conf.BOT_TOKEN)


def admin_buttons():
    x = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton(text="Statistika", callback_data="stat")
    btn2 = InlineKeyboardButton(text="Xabar yuborish", callback_data="send")
    btn3 = InlineKeyboardButton(text="Kanallarni sozlash", callback_data="channels")
    x.add(btn1, btn2, btn3)
    return x


def channel_control():
    x = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton(text="➕Kanal qo'shish", callback_data="channel_add")
    btn2 = InlineKeyboardButton(text="➖Kanalni olib tashlash", callback_data="channel_del")
    x.add(btn1, btn2)
    return x

def join_key(ref_code,confirm):
    keyboard = InlineKeyboardMarkup(row_width=1)
    x = get_channel()
    r = 1
    print(x)
    for i in x:
        print(i)
        ch_name = bot.get_chat("@"+i).title
        print(ch_name)
        print(ch_name.title)
        keyboard.add(
            InlineKeyboardButton(f"{ch_name}", url=f"https://t.me/{i}")
        )
        r += 1
    if confirm == "yes":
        keyboard.add(InlineKeyboardButton('✅ Tasdiqlash', url=f'https://t.me/{conf.BOT_USERNAME}?start={ref_code}'))
    return keyboard

def start_button():
    markup = InlineKeyboardMarkup()

    markup.row(
        InlineKeyboardButton(text="📝 Bot Haqida", callback_data="help"),
        InlineKeyboardButton(text="🔒 Yopish", callback_data="close")
    )
    
    return markup

def main_button():
    x = InlineKeyboardMarkup()

    btn1 = InlineKeyboardButton(text="🧑‍💻 Yaratuvchi",callback_data="bot_owner_text")
    btn2 = InlineKeyboardButton(text="🔒 Yopish", callback_data="close")

    x.add(btn1,btn2)
    return x
