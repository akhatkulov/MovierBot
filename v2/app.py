import telebot
from datetime import datetime

from data.alchemy import create_user, get_step, put_step, user_count, get_all_user, \
    get_channel, put_channel, get_channel_with_id, delete_channel

from helper.buttons import admin_buttons,channel_control,join_key,start_button,main_button
from helper.decode import decode
from helper.encode import encode
from helper.msg_getter import get_messages,get_message_id
import conf
from time import time,sleep
# import parts


bot = telebot.TeleBot(conf.BOT_TOKEN, parse_mode="html")
client = bot
admin_id = conf.ADMIN_ID

db_channel = bot.get_chat(conf.CHANNEL_ID)
bot.db_channel = db_channel

def join(user_id,ref_code,confirm):
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
                             "<b>Animeni yuklab olish uchun quyidagi kanallarga obuna bo'lgan bo'lishingiz kerak:</b>",
                             parse_mode='html', reply_markup=join_key(ref_code,confirm=confirm))
            return False
        else:
            return True
    except Exception as e:
        bot.send_message(chat_id=admin_id, text=f"Kanalga bot admin qilinmagan yoki xato: {str(e)}")
        return True

def check_join(user_id):
    try:
        xx = get_channel()
        r = 0
        for i in xx:
            res = bot.get_chat_member(f"@{i}", user_id)
            x = ['member', 'creator', 'administrator']
            if res.status in x:
                r += 1
        if r != len(xx):
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
    if len(text) > 7:
        if join(user_id=message.chat.id,ref_code=text.split()[1],confirm="yes"):
            try:
                base64_string = text.split(" ", 1)[1]
            except Exception as e:
                print("error:",e)
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
                    print(start,end)
                except Exception as e:
                    print("error suka:",e)
                    return 
                if start <= end:
                    ids = list(range(start, end + 1))
                    print(ids)
                else:
                    ids = []
                    i = start
                    while True:
                        ids.append(i)
                        i -= 1
                        if i < end:
                            break
                    print(ids)
            elif len(argument) == 2:
                try:
                    ids = [int(int(argument[1]) / abs(client.db_channel.id))]
                except BaseException:
                    return
                print(ids)

            temp_msg = bot.reply_to(message, "<code>iltimos kuting...</code>")
            try:
                messages = get_messages(bot, ids)
            except Exception as e:
                print("Error in Send Move",e)
                bot.reply_to(message, "<b>Xatolik </b>🥺")
                return
            bot.delete_message(temp_msg.chat.id, temp_msg.message_id)
            print(messages)
            for msg in messages:
                caption = (
                    conf.CUSTOM_CAPTION.format(
                        previouscaption=msg.caption if msg.caption else "",
                        filename=msg.document.file_name,
                    )
                    if conf.CUSTOM_CAPTION and msg.document
                    else msg.caption if msg.caption else ""
                )

                reply_markup = msg.reply_markup if not conf.DISABLE_CHANNEL_BUTTON else None
                try:
                    bot.copy_message(
                        chat_id=message.from_user.id,
                        from_chat_id=msg.chat.id,
                        message_id=msg.message_id,
                        caption=caption,
                        parse_mode='HTML',
                        protect_content=conf.PROTECT_CONTENT,
                        reply_markup=reply_markup
                    )
                    sleep(0.5)
                except telebot.apihelper.ApiException as e:
                    if e.result_code == 429:
                        sleep(e.retry_after)
                        bot.copy_message(
                            chat_id=message.from_user.id,
                            from_chat_id=msg.chat.id,
                            message_id=msg.message_id,
                            caption=caption,
                            parse_mode='HTML',
                            protect_content=conf.PROTECT_CONTENT,
                            reply_markup=reply_markup
                        )
                except:
                    pass
    else:
        if not check_join(user_id=message.chat.id):
            bot.reply_to(message,
                conf.DEFAULT_START_TEXT,
                reply_markup=join_key(ref_code="!!!",confirm="no"),
                disable_web_page_preview=True,
                parse_mode='HTML'
            )
        else:
            bot.reply_to(message,conf.START_MSG,reply_markup=start_button(),parse_mode="html",disable_web_page_preview=True)

# Handle the /batch command
@bot.message_handler(commands=['batch'])
def batch(message):
    if str(message.chat.id) in conf.ADMINS:
        print(message.chat.id)

        chat_id = message.chat.id

        msg = bot.send_message(chat_id, "<b>Iltimos, birinchi xabarni/faylni ma'lumotlar bazasi kanalidan yuboring. (Qoute bilan yo'naltirish)</b>\n\n<b>yoki Kanal ma'lumotlar bazasidan post havolasini yuboring</b>", parse_mode="HTML")
        bot.register_next_step_handler(msg, process_first_message)
    else:
        bot.send_message(chat_id=message.chat.id,text="Brat siz admin emassiz(")

def process_first_message(message):
    chat_id = message.chat.id

    try:
        f_msg_id = get_message_id(message)
        print(f_msg_id)
        if f_msg_id:
            msg = bot.send_message(chat_id, "<b>Iltimos, oxirgi xabarni/faylni ma'lumotlar bazasi kanalidan yuboring. (Qoute bilan yo'naltirish)</b>\n\n<b>yoki Kanal ma'lumotlar bazasidan post havolasini yuboring</b>", parse_mode="HTML")
            bot.register_next_step_handler(msg, process_second_message, f_msg_id)
        else:
            bot.send_message(chat_id, "❌ <b>XATO</b>\n\n<b>Ushbu yoʻnaltirilgan post maʼlumotlar bazasi kanalidan emas</b>", parse_mode="HTML")
            print(message)
            batch(message)
    except Exception as e:
        bot.send_message(chat_id, str(e))

def process_second_message(message, f_msg_id):
    chat_id = message.chat.id

    try:
        s_msg_id = get_message_id(message)
        if s_msg_id:
            string = f"get-{f_msg_id * abs(bot.db_channel.id)}-{s_msg_id * abs(bot.db_channel.id)}"
            base64_string = encode(string)
            link = f"https://t.me/{bot.get_me().username}?start={base64_string}"
            bot.send_message(chat_id, f"<b>Fayl almashish havolasi muvaffaqiyatli yaratildi:</b>\n\n{link}", parse_mode="HTML")
        else:
            bot.send_message(chat_id, "❌ <b>XATO</b>\n\n<b>Ushbu yoʻnaltirilgan post maʼlumotlar bazasi kanalidan emas</b>", parse_mode="HTML")
            batch(message)
    except Exception as e:
        bot.send_message(chat_id, str(e))


# Handle the /genlink command
@bot.message_handler(commands=['genlink'])
def link_generator(message):
    if str(message.from_user.id) not in conf.ADMINS:
        return

    chat_id = message.chat.id

    msg = bot.send_message(chat_id, "<b>Ma'lumotlar bazasi kanalidan xabarlarni yo'naltiring. (Qoute bilan yo'naltirish)</b>\n\n<b>yoki Kanal ma'lumotlar bazasidan post havolasini yuboring</b>", parse_mode="HTML")
    bot.register_next_step_handler(msg, process_channel_message)

def process_channel_message(message):
    chat_id = message.chat.id

    try:
        msg_id = get_message_id(message)
        if msg_id:
            base64_string = encode(f"get-{msg_id * abs(bot.db_channel.id)}")
            link = f"https://t.me/{bot.get_me().username}?start={base64_string}"
            bot.send_message(chat_id, f"<b>Fayl almashish havolasi muvaffaqiyatli yaratildi:</b>\n\n{link}", parse_mode="HTML")
        else:
            bot.send_message(chat_id, "❌ <b>XATO</b>\n\n<b>Ushbu yoʻnaltirilgan post maʼlumotlar bazasi kanalidan emas</b>", parse_mode="HTML")
            link_generator(message)
    except Exception as e:
        bot.send_message(chat_id, str(e))



@bot.message_handler(commands=["broadcast"])
def send_text(message):
    if str(message.from_user.id) in conf.ADMINS:
        put_step(cid=message.chat.id,step="broadcast")
        bot.send_message(chat_id=message.chat.id,text="Yuboring!")
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

        
@bot.message_handler(content_types=['text','photo'])
def more(message):
    if message.text == "/start_put_videos" and str(message.chat.id) in conf.ADMINS:
        put_step(cid=message.chat.id,step="start_put_video")
        bot.send_message(chat_id=message.chat.id,text="Yuborishni boshlang")

    if message.text == "/stop_put_videos" and str(message.chat.id) in conf.ADMINS:
        put_step(cid=message.chat.id,step='!!!')
        bot.send_message(chat_id=message.chat.id,text="To'xtatildi, video yubormang!")

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

    if get_step(message.chat.id) == 'broadcast':
        if message.text != '/start' or message.text != "/admin":
            target_id = message
            query = get_all_user()
            broadcast_msg = message.reply_to_message
            total = 0
            successful = 0
            blocked = 0
            deleted = 0
            unsuccessful = 0
            print(get_all_user())
            pls_wait = bot.reply_to(
                message, "<code>Broadcasting Message Tunggu Sebentar...</code>"
            )
            for row in query:
                print(row)
                chat_id = row
                if str(chat_id) not in conf.ADMINS:
                    try:
                        bot.copy_message(chat_id, target_id.chat.id, target_id.message_id, protect_content=conf.PROTECT_CONTENT)
                        successful += 1
                    except telebot.apihelper.ApiException as e:
                        if e.result_json['description'] == 'Too Many Requests: retry after':
                            sleep(e.result_json['parameters']['retry_after'])
                            bot.copy_message(chat_id, target_id.chat.id, target_id.message_id, protect_content=conf.PROTECT_CONTENT)
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

            status = f"""<b><u>Natijalar</u>
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
                "<code>Efirga uzatmoqchi boʻlgan telegramma xabariga javob berishda ushbu buyruqdan foydalaning.</code>",
            )
            sleep(8)
            bot.delete_message(message.chat.id, msg.message_id)



@bot.message_handler(content_types=['video'])
def put_videos(message):
    step = get_step(cid=message.chat.id)
    print("step",step)
    print(message.video)
    if str(message.chat.id) in conf.ADMINS and step == "start_put_video":
        reply_text = bot.reply_to(message, "<code>Bir daqiqa kuting...</code>", parse_mode='HTML')
        try:
            post_message = bot.copy_message(
                chat_id=conf.CHANNEL_ID, from_chat_id=message.chat.id, message_id=message.message_id, disable_notification=True
            )
        except ApiException as e:
            if e.error_code == 429:  # FloodWait exception
                time_to_wait = e.parameters['retry_after']
                bot.send_message(message.chat.id, f"Flood kutish. {time_to_wait} soniyadan keyin qayta uriniladi.")
                sleep(time_to_wait)
                post_message = bot.copy_message(
                    chat_id=conf.CHANNEL_ID, from_chat_id=message.chat.id, message_id=message.message_id, disable_notification=True
                )
            else:
                bot.edit_message_text("<b>Xatolik yuz berdi...</b>", chat_id=reply_text.chat.id, message_id=reply_text.message_id, parse_mode='HTML')
                return
        except Exception as e:
            print(e)
            bot.edit_message_text("<b>Xatolik yuz berdi...</b>", chat_id=reply_text.chat.id, message_id=reply_text.message_id, parse_mode='HTML')
            return

        converted_id = post_message.message_id * abs(int(conf.CHANNEL_ID))
        string = f"get-{converted_id}"
        base64_string = encode(string)
        link = f"https://t.me/{bot.get_me().username}?start={base64_string}"


        bot.edit_message_text(
            f"<b>Fayl almashish havolasi muvaffaqiyatli yaratildi:</b>\n\n{link}",
            chat_id=reply_text.chat.id,
            message_id=reply_text.message_id,
            parse_mode='HTML'
        )

        if not conf.DISABLE_CHANNEL_BUTTON:
            try:
                bot.edit_message_reply_markup(
                    chat_id=post_message.chat.id,
                    message_id=post_message.message_id,
                    reply_markup=reply_markup
                )
            except Exception:
                pass
    else:
        bot.send_message(chat_id=message.chat.id,text="Brat siz admin emassiz(")





@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):  
    try:
        if "help" == call.data:
            help_text = f"""<b>Botni ishlatishni bilmaganlar uchun!
                
❏ Botni ishlatish qo'llanmasi:
    1. Kanallarga obuna bo'ling!
    2. Tekshirish Tugmasini bosing ✅
    3. Kanaldagi anime post past qismidagi yuklab olish tugmasini bosing

👨‍💻 Yaratuvchi @{conf.OWNER}</b>"""
                
                # Edit the message with the help text
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=help_text, parse_mode="html", reply_markup=main_button())
        else:
            print("Error: call.data is not in the expected format or message ID is not a valid number.")
    except Exception as e:
        print(f"An error occurred: {e}")

    if call.data == "bot_owner_text":
        help_text = """<b>• Admin: @Sukine
• Asosiy Kanal: @Anidonuz
• Reklama: @Anidonuz_reklama

👨‍💻 Savollar Boʻlsa: @Anime_chat_uzb</b>
        """
        bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text=help_text,parse_mode="html",reply_markup=start_button())
    
    if "close" == call.data:
        bot.delete_message(call.message.chat.id, call.message.message_id)
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
