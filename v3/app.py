from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from datetime import datetime
from data.alchemy import create_user, get_step, put_step, user_count, get_all_user, \
    get_channel, put_channel, get_channel_with_id, delete_channel

from helper.buttons import admin_buttons, channel_control, join_key, start_button, main_button
from helper.decode import decode
from helper.encode import encode
from helper.msg_getter import get_messages, get_message_id
import conf
from time import time, sleep
import asyncio
bot = Bot(token=conf.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)
client = bot
admin_id = conf.ADMIN_ID

db_channel = bot.get_chat(conf.CHANNEL_ID)
bot.db_channel = db_channel

async def get_chat(chat_id):
    return await bot.get_chat(chat_id)

async def join(user_id, ref_code, confirm):
    try:
        xx = get_channel()
        r = 0
        for i in xx:
            res = await bot.get_chat_member(f"@{i}", user_id)
            x = ['member', 'creator', 'administrator']
            if res.status in x:
                r += 1
        if r != len(xx):
            await bot.send_message(user_id,
                                   "<b>Animeni yuklab olish uchun quyidagi kanallarga obuna bo'lgan bo'lishingiz kerak:</b>",
                                   parse_mode='html', reply_markup=join_key(ref_code, confirm=confirm))
            return False
        else:
            return True
    except Exception as e:
        await bot.send_message(chat_id=admin_id, text=f"Kanalga bot admin qilinmagan yoki xato: {str(e)}")
        return True

async def check_join(user_id):
    try:
        xx = get_channel()
        r = 0
        for i in xx:
            res = await bot.get_chat_member(f"@{i}", user_id)
            x = ['member', 'creator', 'administrator']
            if res.status in x:
                r += 1
        if r != len(xx):
            return False
        else:
            return True
    except Exception as e:
        await bot.send_message(chat_id=admin_id, text=f"Kanalga bot admin qilinmagan yoki xato: {str(e)}")
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




@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    user_id = message.from_user.id
    user_name = f"@{message.from_user.username}" if message.from_user.username else None

    try:
        create_user(cid=message.chat.id, name=message.chat.first_name)
    except Exception as e:
        print(f"Error creating user: {str(e)}")

    text = message.text
    if len(text) > 7:
        if await join(user_id=message.chat.id, ref_code=text.split()[1], confirm="yes"):
            try:
                base64_string = text.split(" ", 1)[1]
            except Exception as e:
                print("error:", e)
                return

            # Ensure decode returns a string
            string = decode(base64_string)

            # Debugging: Print the type of 'string'
            print(f"Decoded string type: {type(string)}", string)

            # Ensure it's a string
            if not isinstance(string, str):
                return

            argument = string.split("-")
            print("Argument:", argument)
            if len(argument) == 3:
                try:
                    start = int(int(argument[1]) / abs(int(conf.CHANNEL_ID)))
                    end = int(int(argument[2]) / abs(int(conf.CHANNEL_ID)))
                    print(start, end)
                except Exception as e:
                    print("error suka:", e)
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
                    ids = [int(int(argument[1]) / abs(int(conf.CHANNEL_ID)))]
                except BaseException:
                    return
                print(ids)

            temp_msg = await bot.send_message(message.chat.id, "<code>iltimos kuting...</code>")
            try:
                messages = await get_messages(client=bot,message_ids=ids)  # Await the coroutine
            except Exception as e:
                print("Error in Send Move", e)
                await bot.send_message(message.chat.id, "<b>Xatolik </b>🥺")
                return
            await bot.delete_message(temp_msg.chat.id, temp_msg.message_id)
            print("len:",len(messages))
            for msg in messages:
                print(msg)
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
                    await bot.copy_message(
                        chat_id=message.from_user.id,
                        from_chat_id=msg.chat.id,
                        message_id=msg.message_id,
                        caption=caption,
                        parse_mode='HTML',
                        protect_content=conf.PROTECT_CONTENT,
                        reply_markup=reply_markup
                    )
                    await asyncio.sleep(0.5)
                except Exception as e:
                    print("error#1 :",e)
                    if isinstance(e, aiogram.utils.exceptions.RetryAfter):
                        await asyncio.sleep(e.retry_after)
                        await bot.copy_message(
                            chat_id=message.from_user.id,
                            from_chat_id=msg.chat.id,
                            message_id=msg.message_id,
                            caption=caption,
                            parse_mode='HTML',
                            protect_content=conf.PROTECT_CONTENT,
                            reply_markup=reply_markup
                        )
    else:
        if not await check_join(user_id=message.chat.id):
            await bot.send_message(message.chat.id,
                                   conf.DEFAULT_START_TEXT,
                                   reply_markup=join_key(ref_code="!!!", confirm="no"),
                                   disable_web_page_preview=True,
                                   parse_mode='HTML'
                                  )
        else:
            await bot.send_message(message.chat.id, conf.START_MSG, reply_markup=start_button(), parse_mode="HTML", disable_web_page_preview=True)



@dp.message_handler(commands=['batch'])
async def batch(message: types.Message):
    if str(message.chat.id) in conf.ADMINS:
        print(message.chat.id)
        chat_id = message.chat.id
        msg = await bot.send_message(chat_id, "<b>Iltimos, birinchi xabarni/faylni ma'lumotlar bazasi kanalidan yuboring. (Qoute bilan yo'naltirish)</b>\n\n<b>yoki Kanal ma'lumotlar bazasidan post havolasini yuboring</b>", parse_mode="HTML")
        await dp.register_message_handler(process_first_message, state="*", content_types=types.ContentTypes.ANY)
        # Assuming the state is set for the next step
    else:
        await bot.send_message(chat_id=message.chat.id, text="Brat siz admin emassiz(")

@dp.message_handler(commands=['genlink'])
async def link_generator(message: types.Message):
    if str(message.from_user.id) not in conf.ADMINS:
        return
    chat_id = message.chat.id
    msg = await bot.send_message(chat_id, "<b>Ma'lumotlar bazasi kanalidan xabarlarni yo'naltiring. (Qoute bilan yo'naltirish)</b>\n\n<b>yoki Kanal ma'lumotlar bazasidan post havolasini yuboring</b>", parse_mode="HTML")
    await dp.register_message_handler(process_channel_message, state="*", content_types=types.ContentTypes.ANY)
    # Assuming the state is set for the next step

async def process_channel_message(message: types.Message):
    chat_id = message.chat.id
    try:
        msg_id = get_message_id(message)
        if msg_id:
            base64_string = encode(f"get-{msg_id * abs(bot.db_channel.id)}")
            link = f"https://t.me/{(await bot.get_me()).username}?start={base64_string}"
            await bot.send_message(chat_id, f"<b>Fayl almashish havolasi muvaffaqiyatli yaratildi:</b>\n\n{link}", parse_mode="HTML")
        else:
            await bot.send_message(chat_id, "❌ <b>XATO</b>\n\n<b>Ushbu yoʻnaltirilgan post maʼlumotlar bazasi kanalidan emas</b>", parse_mode="HTML")
            await link_generator(message)
    except Exception as e:
        await bot.send_message(chat_id, str(e))

@dp.message_handler(commands=["broadcast"])
async def send_text(message: types.Message):
    if str(message.from_user.id) in conf.ADMINS:
        put_step(cid=message.chat.id, step="broadcast")
        await bot.send_message(chat_id=message.chat.id, text="Yuboring!")


@dp.message_handler(commands=['ping'])
async def ping_pong(message: types.Message):
    start = time()
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = _human_time_duration(int(uptime_sec))
    m_reply = await message.answer("Pinging...")
    delta_ping = time() - start
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=m_reply.message_id,
        text=f"<b>PONG!!</b>🏓 \n"
             f"<b>• Pinger -</b> <code>{delta_ping * 1000:.3f}ms</code>\n"
             f"<b>• Uptime -</b> <code>{uptime}</code>\n",
        parse_mode=ParseMode.HTML
    )
@dp.message_handler(commands=["uptime"])
async def get_uptime(message: types.Message):
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = _human_time_duration(int(uptime_sec))
    await bot.send_message(
        chat_id=message.chat.id,
        text="🤖 <b>Bot Status:</b>\n"
             f"• <b>Uptime:</b> <code>{uptime}</code>\n"
             f"• <b>Start Time:</b> <code>{START_TIME_ISO}</code>"
    )

@dp.message_handler(content_types=['text', 'photo'])
async def more(message: types.Message):
    if message.text == "/start_put_videos" and str(message.chat.id) in conf.ADMINS:
        put_step(cid=message.chat.id, step="start_put_video")
        await bot.send_message(chat_id=message.chat.id, text="Yuborishni boshlang")

    if message.text == "/stop_put_videos" and str(message.chat.id) in conf.ADMINS:
        put_step(cid=message.chat.id, step='!!!')
        await bot.send_message(chat_id=message.chat.id, text="To'xtatildi, video yubormang!")

    if message.text == "/admin" and message.chat.id == admin_id:
        await bot.send_message(chat_id=admin_id, text="Salom, Admin", reply_markup=admin_buttons())
        put_step(cid=message.chat.id, step="!!!")

    if get_step(message.chat.id) == "channel_del" and message.text not in ["/start", "/admin"]:
        x = int(message.text)
        if delete_channel(ch_id=x):
            await bot.send_message(chat_id=message.chat.id, text="Kanal olib tashlandi")
            put_step(cid=message.chat.id, step="!!!")
        else:
            await bot.send_message(chat_id=message.chat.id, text="Xatolik! IDni to'g'ri kiritdingizmi tekshiring!")

    if get_step(message.chat.id) == "add_channel" and message.text not in ["/start", "/admin"]:
        if put_channel(message.text):
            await bot.send_message(chat_id=message.chat.id, text=f"{message.text} kanali qabul qilindi!")
            put_step(cid=int(admin_id), step="!!!")
        else:
            await bot.send_message(chat_id=message.chat.id,
                                 text="Xatolik! Bu kanal oldin qo'shilgan bo'lishi mumkin yoki boshqa xatolik, iltimos tekshiring")
            put_step(cid=int(admin_id), step="!!!")
    
    if get_step(message.chat.id) == 'send':
        text = message.text
        mid = message.message_id
        await bot.send_message(chat_id=message.chat.id, text="Xabar yuborish boshlandi")
        try:
            for i in get_all_user():
                try:
                    await bot.forward_message(chat_id=i, from_chat_id=admin_id, message_id=mid)
                except Exception as e:
                    print(f"Error sending message to user {i}: {str(e)}")
            await bot.send_message(chat_id=message.chat.id, text="Tarqatish yakunlandi")
            put_step(cid=int(admin_id), step="!!!")
        except Exception as e:
            await bot.send_message(chat_id=message.chat.id, text=f"Xabar yuborishda muammo bo'ldi: {str(e)}")

    if get_step(message.chat.id) == 'broadcast':
        if message.text not in ['/start', '/admin']:
            target_id = message.reply_to_message
            query = get_all_user()
            broadcast_msg = message.reply_to_message
            total = 0
            successful = 0
            blocked = 0
            deleted = 0
            unsuccessful = 0
            print(get_all_user())
            pls_wait = await bot.reply_to(
                message, "<code>Broadcasting Message Tunggu Sebentar...</code>"
            )
            for row in query:
                print(row)
                chat_id = row
                if str(chat_id) not in conf.ADMINS:
                    try:
                        await bot.copy_message(chat_id, target_id.chat.id, target_id.message_id, protect_content=conf.PROTECT_CONTENT)
                        successful += 1
                    except Exception as e:
                        if str(e) == 'Too Many Requests: retry after':
                            sleep(e.retry_after)
                            await bot.copy_message(chat_id, target_id.chat.id, target_id.message_id, protect_content=conf.PROTECT_CONTENT)
                            successful += 1
                        elif str(e) == 'Forbidden: bot was blocked by the user':
                            delete_user(chat_id)
                            blocked += 1
                        elif str(e) == 'Forbidden: user is deactivated':
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
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=pls_wait.message_id,
                text=status,
            )
        else:
            msg = await bot.reply_to(
                message,
                "<code>Efirga uzatmoqchi boʻlgan telegramma xabariga javob berishda ushbu buyruqdan foydalaning.</code>",
            )
            asyncio.sleep(8)
            await bot.delete_message(message.chat.id, msg.message_id)

@dp.message_handler(content_types=['video'])
async def put_videos(message: types.Message):
    step = get_step(cid=message.chat.id)
    print("step", step)
    print(message.video)
    if str(message.chat.id) in conf.ADMINS and step == "start_put_video":
        reply_text = await bot.reply_to(message, "<code>Bir daqiqa kuting...</code>", parse_mode='HTML')
        try:
            post_message = await bot.copy_message(
                chat_id=conf.CHANNEL_ID, from_chat_id=message.chat.id, message_id=message.message_id, disable_notification=True
            )
        except FloodWait as e:
            time_to_wait = e.retry_after
            await bot.send_message(message.chat.id, f"Flood kutish. {time_to_wait} soniyadan keyin qayta uriniladi.")
            await asyncio.sleep(time_to_wait)
            post_message = await bot.copy_message(
                chat_id=conf.CHANNEL_ID, from_chat_id=message.chat.id, message_id=message.message_id, disable_notification=True
            )
        except Exception as e:
            print(e)
            await bot.edit_message_text("<b>Xatolik yuz berdi...</b>", chat_id=reply_text.chat.id, message_id=reply_text.message_id, parse_mode='HTML')
            return

        converted_id = post_message.message_id * abs(int(conf.CHANNEL_ID))
        string = f"get-{converted_id}"
        base64_string = encode(string)
        link = f"https://t.me/{await bot.get_me().username}?start={base64_string}"

        await bot.edit_message_text(
            f"<b>Fayl almashish havolasi muvaffaqiyatli yaratildi:</b>\n\n{link}",
            chat_id=reply_text.chat.id,
            message_id=reply_text.message_id,
            parse_mode='HTML'
        )

        if not conf.DISABLE_CHANNEL_BUTTON:
            try:
                await bot.edit_message_reply_markup(
                    chat_id=post_message.chat.id,
                    message_id=post_message.message_id,
                    reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="Channel Button", url=link))
                )
            except Exception:
                pass
    else:
        await bot.send_message(chat_id=message.chat.id, text="Brat siz admin emassiz(")

@dp.callback_query_handler(lambda call: True)
async def callback_query(call: types.CallbackQuery):
    try:
        if call.data == "help":
            help_text = f"""<b>Botni ishlatishni bilmaganlar uchun!
                
❏ Botni ishlatish qo'llanmasi:
    1. Kanallarga obuna bo'ling!
    2. Tekshirish Tugmasini bosing ✅
    3. Kanaldagi anime post past qismidagi yuklab olish tugmasini bosing

👨‍💻 Yaratuvchi @{conf.OWNER}</b>"""
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=help_text, parse_mode="HTML", reply_markup=main_button())
        elif call.data == "bot_owner_text":
            help_text = """<b>• Admin: @Sukine
• Asosiy Kanal: @Anidonuz
• Reklama: @Anidonuz_reklama

👨‍💻 Savollar Boʻlsa: @Anime_chat_uzb</b>"""
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=help_text, parse_mode="HTML", reply_markup=start_button())
        elif call.data == "close":
            await bot.delete_message(call.message.chat.id, call.message.message_id)
        elif call.data == "stat" and str(call.message.chat.id) == str(admin_id):
            await bot.send_message(chat_id=call.message.chat.id, text=f"Foydalanuvchilar soni: {user_count()}")
        elif call.data == "send" and str(call.message.chat.id) == str(admin_id):
            put_step(cid=call.message.chat.id, step="send")
            await bot.send_message(chat_id=call.message.chat.id, text="Forward xabaringizni yuboring")
        elif call.data == "channels" and str(call.message.chat.id) == str(admin_id):
            r = get_channel_with_id()
            await bot.send_message(chat_id=call.message.chat.id, text=f"Kanallar ro'yxati:{r}", reply_markup=channel_control())
        elif call.data == "channel_add" and str(call.message.chat.id) == str(admin_id):
            put_step(cid=call.message.chat.id, step="add_channel")
            await bot.send_message(chat_id=call.message.chat.id, text="Kanali linkini yuboring! bekor qilish uchun /start !")
        elif call.data == "channel_del" and str(call.message.chat.id) == str(admin_id):
            put_step(cid=call.message.chat.id, step="channel_del")
            await bot.send_message(chat_id=call.message.chat.id,
                                 text=f"{get_channel_with_id()}\n⚠️O'chirmoqchi bo'lgan kanalingiz IDsini bering, bekor qilish uchun /start yoki /admin deng!")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    x = bot.get_me()
    print(x)
    executor.start_polling(dp, skip_updates=True)
