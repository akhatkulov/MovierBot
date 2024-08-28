import telebot
from datetime import datetime

from data.alchemy import create_user, get_step, put_step, user_count, get_all_user, \
    get_channel, put_channel, get_channel_with_id, delete_channel

from helper.buttons import admin_buttons,channel_control,join_key,start_button
from helper.decode import decode
from helper.msg_getter import get_messages
import conf

bot = telebot.TeleBot(conf.BOT_TOKEN, parse_mode="html")
client = bot
admin_id = conf.ADMIN_ID

db_channel = bot.get_chat(conf.CHANNEL_ID)
bot.db_channel = db_channel

def join(user_id,ref_code):
    try:
        xx = get_channel()
        r = 0
        for i in xx:
            res = bot.get_chat_member(f"@{i}", user_id)
            x = ['member', 'creator', 'administrator']
            if res.status in x:
                r += 1
        if r != len(xx):
            bot.send_message(user_id,
                             "<b>👋 Assalomu alaykum Botni ishga tushurish uchun kanallarga a'zo bo'ling va a'zolikni tekshirish buyrug'ini bosing.</b>",
                             parse_mode='html', reply_markup=join_key(ref_code))
            return False
        else:
            return True
    except Exception as e:
        bot.send_message(chat_id=admin_id, text=f"Kanalga bot admin qilinmagan yoki xato: {str(e)}")
        return True


START_TIME = datetime.utcnow()
START_TIME_ISO = START_TIME.replace(microsecond=0).isoformat()
TIME_DURATION_UNITS = (
    ("week", 60 * 60 * 24 * 7),
    ("day", 60**2 * 24),
    ("hour", 60**2),
    ("min", 60),
    ("sec", 1),
)


def _human_time_duration(seconds):
    if seconds == 0:
        return "inf"
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append(f'{amount} {unit}{"" if amount == 1 else "s"}')
    return ", ".join(parts)

@bot.message_handler(commands=["start"])
def start_command(message: telebot.types.Message):
    user_id = message.from_user.id
    user_name = f"@{message.from_user.username}" if message.from_user.username else None

    try:
        create_user(cid=message.chat.id,name=message.chat.first_name)
    except Exception as e:
        print(f"Error creating user: {str(e)}")

    text = message.text
    if len(text) > 7 and join(user_id=message.chat.id,ref_code=text.split()[1]):
        try:
            base64_string = text.split(" ", 1)[1]
        except BaseException:
            return

        # Ensure decode returns a string
        string = decode(base64_string)

        # Debugging: Print the type of 'string'
        print(f"Decoded string type: {type(string)}",string)
        
        # Ensure it's a string
        if not isinstance(string, str):
            return

        argument = string.split("-")
        print("Argument:",argument)
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except Exception as e:
                print("error suka:",e)
                return 
            if start <= end:
                ids = range(start, end + 1)
            else:
                ids = []
                i = start
                while True:
                    ids.append(i)
                    i -= 1
                    if i < end:
                        break
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except BaseException:
                return

        temp_msg = bot.reply_to(message, "<code>iltimos kuting...</code>")
        try:
            messages = get_messages(bot, ids)
        except Exception as e:
            print("Error in Send Move",e)
            bot.reply_to(message, "<b>Xatolik </b>🥺")
            return
        bot.delete_message(temp_msg.chat.id, temp_msg.message_id)

        for msg in messages:
            if bool(CUSTOM_CAPTION) and bool(msg.document):
                caption = CUSTOM_CAPTION.format(
                    previouscaption=msg.caption.html if msg.caption else "",
                    filename=msg.document.file_name,
                )
            else:
                caption = msg.caption.html if msg.caption else ""

            reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None
            try:
                bot.send_message(
                    chat_id=message.from_user.id,
                    text=msg.text,
                    caption=caption,
                    parse_mode="HTML",
                    protect_content=PROTECT_CONTENT,
                    reply_markup=reply_markup,
                )
                time.sleep(0.5)
            except telebot.apihelper.ApiException as e:
                if e.result_json['description'] == 'Too Many Requests: retry after':
                    time.sleep(e.result_json['parameters']['retry_after'])
                    bot.send_message(
                        chat_id=message.from_user.id,
                        text=msg.text,
                        caption=caption,
                        parse_mode="HTML",
                        protect_content=PROTECT_CONTENT,
                        reply_markup=reply_markup,
                    )
                else:
                    pass
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text=conf.START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=f"@{message.from_user.username}" if message.from_user.username else None,
                id=message.from_user.id,
            ),
            reply_markup=start_button(bot),
            disable_web_page_preview=True,
        )



@bot.message_handler(commands=["start"])
def not_joined(message):
    try:
        create_user(cid=message.chat.id,name=message.chat.first_name)
    except Exception as e:
        print(f"Error creating user: {str(e)}")

    buttons = fsub_button(bot, message)
    bot.send_message(
        chat_id=message.chat.id,
        text=FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=f"@{message.from_user.username}"
            if message.from_user.username
            else None,
            mention=message.from_user.mention,
            id=message.from_user.id,
        ),
        reply_markup=types.InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True,
    )


@bot.message_handler(commands=["users", "stats"])
def get_users(message):
    if message.from_user.id in ADMINS:
        msg = bot.send_message(
            chat_id=message.chat.id, text="<code>Yuklanmoqda ...</code>"
        )
        users = full_userbase()
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=msg.message_id,
            text=f"{len(users)} <b>Foydalanuvchilar soni</b>",
        )


@bot.message_handler(commands=["broadcast"])
def send_text(message):
    if message.from_user.id in ADMINS:
        if message.reply_to_message:
            query = query_msg()
            broadcast_msg = message.reply_to_message
            total = 0
            successful = 0
            blocked = 0
            deleted = 0
            unsuccessful = 0

            pls_wait = bot.reply_to(
                message, "<code>Broadcasting Message Tunggu Sebentar...</code>"
            )
            for row in query:
                chat_id = int(row[0])
                if chat_id not in ADMINS:
                    try:
                        bot.copy_message(chat_id, broadcast_msg.chat.id, broadcast_msg.message_id, protect_content=PROTECT_CONTENT)
                        successful += 1
                    except telebot.apihelper.ApiException as e:
                        if e.result_json['description'] == 'Too Many Requests: retry after':
                            asyncio.sleep(e.result_json['parameters']['retry_after'])
                            bot.copy_message(chat_id, broadcast_msg.chat.id, broadcast_msg.message_id, protect_content=PROTECT_CONTENT)
                            successful += 1
                        elif e.result_json['description'] == 'Forbidden: bot was blocked by the user':
                            delete_user(chat_id)
                            blocked += 1
                        elif e.result_json['description'] == 'Forbidden: user is deactivated':
                            delete_user(chat_id)
                            deleted += 1
                        else:
                            unsuccessful += 1
                    total += 1

            status = f"""<b><u>Berhasil Broadcast</u>
Jami foydalanuvchilar: <code>{total}</code>
Muvaffaqiyatli Yuborildi: <code>{successful}</code>
Muvaffaqiyatsiz Yuborildi: <code>{unsuccessful}</code>
Bloklaganlar: <code>{blocked}</code>
ochirilgan hisoblar: <code>{deleted}</code></b>"""
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=pls_wait.message_id,
                text=status,
            )
        else:
            msg = bot.reply_to(
                message,
                "<code>Gunakan Perintah ini Harus Sambil Reply ke pesan telegram yang ingin di Broadcast.</code>",
            )
            asyncio.sleep(8)
            bot.delete_message(message.chat.id, msg.message_id)


@bot.message_handler(commands=["ping"])
def ping_pong(message):
    start = time()
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = _human_time_duration(int(uptime_sec))
    m_reply = bot.reply_to(message, "Pinging...")
    delta_ping = time() - start
    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=m_reply.message_id,
        text="<b>PONG!!</b>🏓 \n"
        f"<b>• Pinger -</b> <code>{delta_ping * 1000:.3f}ms</code>\n"
        f"<b>• Uptime -</b> <code>{uptime}</code>\n"
    )


@bot.message_handler(commands=["uptime"])
def get_uptime(message):
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = _human_time_duration(int(uptime_sec))
    bot.send_message(
        chat_id=message.chat.id,
        text="🤖 <b>Bot Status:</b>\n"
        f"• <b>Uptime:</b> <code>{uptime}</code>\n"
        f"• <b>Start Time:</b> <code>{START_TIME_ISO}</code>"
    )        

        
@bot.message_handler(content_types=['text'])
def more(message):
    if message.text == "/admin" and message.chat.id == admin_id:
        bot.send_message(chat_id=admin_id, text="Salom, Admin", reply_markup=admin_buttons())
        put_step(cid=message.chat.id, step="!!!")

    if get_step(message.chat.id) == "channel_del" and message.text != "/start" and message.text != "/admin":
        x = int(message.text)
        if delete_channel(ch_id=x):
            bot.send_message(chat_id=message.chat.id, text="Kanal olib tashlandi")
            put_step(cid=message.chat.id, step="!!!")
        else:
            bot.send_message(chat_id=message.chat.id, text="Xatolik! IDni to'g'ri kiritdingizmi tekshiring!")

    if get_step(message.chat.id) == "add_channel" and message.text != "/start" and message.text != "/admin":
        if put_channel(message.text):
            bot.send_message(chat_id=message.chat.id, text=f"{message.text} kanali qabul qilindi!")
            put_step(cid=int(admin_id), step="!!!")
        else:
            bot.send_message(chat_id=message.chat.id,
                             text="Xatolik! Bu kanal oldin qo'shilgan bo'lishi mumkin yoki boshqa xatolik, iltimos tekshiring")
            put_step(cid=int(admin_id), step="!!!")
    
    if get_step(message.chat.id) == 'send':
        text = message.text
        mid = message.id
        bot.send_message(chat_id=message.chat.id, text="Xabar yuborish boshlandi")
        try:
            for i in get_all_user():
                try:
                    bot.forward_message(chat_id=i, from_chat_id=admin_id, message_id=mid)
                except Exception as e:
                    print(f"Error sending message to user {i}: {str(e)}")
            bot.send_message(chat_id=message.chat.id, text="Tarqatish yakunlandi")
            put_step(cid=int(admin_id), step="!!!")
        except Exception as e:
            bot.send_message(chat_id=message.chat.id, text=f"Xabar yuborishda muammo bo'ldi: {str(e)}")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):  
    if call.data == "/start" and join(call.message.chat.id):
        bot.send_message(chat_id=call.message.chat.id,text="<b>Obuna tasdiqlandi✅</b>",parse_mode="html") 
    if call.data == "stat" and str(call.message.chat.id) == str(admin_id):
        bot.send_message(chat_id=call.message.chat.id, text=f"Foydalanuvchilar soni: {user_count()}")
    if call.data == "send" and str(call.message.chat.id) == str(admin_id):
        put_step(cid=call.message.chat.id, step="send")
        bot.send_message(chat_id=call.message.chat.id, text="Forward xabaringizni yuboring")
    if call.data == "channels" and str(call.message.chat.id) == str(admin_id):
        r = get_channel_with_id()
        bot.send_message(chat_id=call.message.chat.id, text=f"Kanallar ro'yxati:{r}", reply_markup=channel_control())
    if call.data == "channel_add" and str(call.message.chat.id) == str(admin_id):
        put_step(cid=call.message.chat.id, step="add_channel")
        bot.send_message(chat_id=call.message.chat.id, text="Kanali linkini yuboring! bekor qilish uchun /start !")
    if call.data == "channel_del" and str(call.message.chat.id) == str(admin_id):
        put_step(cid=call.message.chat.id, step="channel_del")
        bot.send_message(chat_id=call.message.chat.id,
                         text=f"{get_channel_with_id()}\n⚠️O'chirmoqchi bo'lgan kanalingiz IDsini bering, bekor qilish uchun /start yoki /admin deng!")

if __name__ == '__main__':
    print(bot.get_me())
    bot.polling(none_stop=True)
