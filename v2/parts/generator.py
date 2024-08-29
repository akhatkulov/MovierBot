import conf
import telebot
from helper.encode import encode
from helper.msg_getter import get_message_id

bot = telebot.TeleBot(conf.BOT_TOKEN)

# Handle the /batch command
@bot.message_handler(commands=['batch'])
def batch(message):
    print(message.from_user.id)
    if str(message.from_user.id) not in conf.ADMINS:
        print("batch")
        return

    chat_id = message.chat.id

    msg = bot.send_message(chat_id, "<b>Silahkan Forward Pesan/File Pertama dari Channel DataBase. (Forward with Qoute)</b>\n\n<b>atau Kirim Link Postingan dari Channel Database</b>", parse_mode="HTML")
    bot.register_next_step_handler(msg, process_first_message)

def process_first_message(message):
    chat_id = message.chat.id

    try:
        f_msg_id = get_message_id(bot, message)
        if f_msg_id:
            msg = bot.send_message(chat_id, "<b>Silahkan Forward Pesan/File Terakhir dari Channel DataBase. (Forward with Qoute)</b>\n\n<b>atau Kirim Link Postingan dari Channel Database</b>", parse_mode="HTML")
            bot.register_next_step_handler(msg, process_second_message, f_msg_id)
        else:
            bot.send_message(chat_id, "❌ <b>ERROR</b>\n\n<b>Postingan yang Diforward ini bukan dari Channel Database saya</b>", parse_mode="HTML")
            batch(message)
    except Exception as e:
        bot.send_message(chat_id, str(e))

def process_second_message(message, f_msg_id):
    chat_id = message.chat.id

    try:
        s_msg_id = get_message_id(bot, message)
        if s_msg_id:
            string = f"get-{f_msg_id * abs(bot.db_channel.id)}-{s_msg_id * abs(bot.db_channel.id)}"
            base64_string = encode(string)
            link = f"https://t.me/{bot.get_me().username}?start={base64_string}"
            reply_markup = types.InlineKeyboardMarkup()
            reply_markup.add(types.InlineKeyboardButton("🔁 Share Link", url=f"https://telegram.me/share/url?url={link}"))
            bot.send_message(chat_id, f"<b>Link Sharing File Berhasil Di Buat:</b>\n\n{link}", parse_mode="HTML", reply_markup=reply_markup)
        else:
            bot.send_message(chat_id, "❌ <b>ERROR</b>\n\n<b>Postingan yang Diforward ini bukan dari Channel Database saya</b>", parse_mode="HTML")
            batch(message)
    except Exception as e:
        bot.send_message(chat_id, str(e))


# Handle the /genlink command
@bot.message_handler(commands=['genlink'])
def link_generator(message):
    if message.from_user.id not in conf.ADMINS:
        return

    chat_id = message.chat.id

    msg = bot.send_message(chat_id, "<b>Silahkan Forward Pesan dari Channel DataBase. (Forward with Qoute)</b>\n\n<b>atau Kirim Link Postingan dari Channel Database</b>", parse_mode="HTML")
    bot.register_next_step_handler(msg, process_channel_message)

def process_channel_message(message):
    chat_id = message.chat.id

    try:
        msg_id = get_message_id(bot, message)
        if msg_id:
            base64_string = encode(f"get-{msg_id * abs(bot.db_channel.id)}")
            link = f"https://t.me/{bot.get_me().username}?start={base64_string}"
            reply_markup = types.InlineKeyboardMarkup()
            reply_markup.add(types.InlineKeyboardButton("🔁 Share Link", url=f"https://telegram.me/share/url?url={link}"))
            bot.send_message(chat_id, f"<b>Link Sharing File Berhasil Di Buat:</b>\n\n{link}", parse_mode="HTML", reply_markup=reply_markup)
        else:
            bot.send_message(chat_id, "❌ <b>ERROR</b>\n\n<b>Postingan yang Diforward ini bukan dari Channel Database saya</b>", parse_mode="HTML")
            link_generator(message)
    except Exception as e:
        bot.send_message(chat_id, str(e))