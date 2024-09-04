from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from data.alchemy import get_channel
import conf

bot = Bot(token=conf.BOT_TOKEN)
dp = Dispatcher(bot)

def admin_buttons():
    markup = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton(text="Statistika", callback_data="stat")
    btn2 = InlineKeyboardButton(text="Xabar yuborish", callback_data="send")
    btn3 = InlineKeyboardButton(text="Kanallarni sozlash", callback_data="channels")
    markup.add(btn1, btn2, btn3)
    return markup

def channel_control():
    markup = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton(text="➕Kanal qo'shish", callback_data="channel_add")
    btn2 = InlineKeyboardButton(text="➖Kanalni olib tashlash", callback_data="channel_del")
    markup.add(btn1, btn2)
    return markup

async def join_key(ref_code, confirm):
    keyboard = InlineKeyboardMarkup(row_width=1)
    channels = get_channel()
    print("Channels:", channels)
    
    for channel_id in channels:
        chat = await bot.get_chat(chat_id="@" + channel_id)
        ch_name = chat.title
        print(f"Adding button for channel: {ch_name} ({channel_id})")
        keyboard.add(
            InlineKeyboardButton(text=f"{ch_name}", url=f"https://t.me/{channel_id}")
        )
    
    if confirm == "yes":
        keyboard.add(
            InlineKeyboardButton(text='✅ Tasdiqlash', url=f'https://t.me/{conf.BOT_USERNAME}?start={ref_code}')
        )
    
    print("Keyboard JSON:", keyboard.to_python())
    return keyboard

def start_button():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text="📝 Bot Haqida", callback_data="help"),
        InlineKeyboardButton(text="🔒 Yopish", callback_data="close")
    )
    return markup

def main_button():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text="🧑‍💻 Yaratuvchi", callback_data="bot_owner_text"),
        InlineKeyboardButton(text="🔒 Yopish", callback_data="close")
    )
    return markup
