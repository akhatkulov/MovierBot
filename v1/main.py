import logging
from config import *
from flask import *
import time

logging.basicConfig(level=logging._ExcInfoType)

conn.commit()

app = Flask(__name__)
@app.route('/', methods=['POST', 'GET'])
def webhook():
  if request.method == 'POST':
    data = request.get_json()
    bot.process_new_updates([telebot.types.Update.de_json(data)])
    return "OK"
  else:
    return "Hello, this is your Telegram bot's webhook!"




@bot.message_handler()
def welcome(msg):
    cid = msg.chat.id
    text = msg.text
    check = cursor.execute(f"SELECT * FROM users WHERE chat_id={cid}").fetchone()
    if check is None:
      cursor.execute(f"INSERT INTO users(chat_id) VALUES({cid})")
      
    elif text=='/start' and len(text)==6:
      bot.send_message(cid,f"""
<b>👋 Salom {msg.from_user.first_name}!</b>

<i>🎬 Kino kanalimizga kiring!</i>""",reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="🔎 Kanalimiz",url="https://t.me/Xeact_Uz")))
    elif text.split(" ")[0] and len(text)>5:
      code = text.split(" ")[1]
      if 's' in code and join(cid,code):
        code = code.replace("s","")
        all = cursor.execute(f"SELECT * FROM serial WHERE id={code}").fetchone()
        if all:
          name = all[1]
          json = cursor.execute(f"SELECT * FROM movies WHERE serial='{name}'").fetchall()
          c = 0
          key = InlineKeyboardMarkup(row_width=4)
          m = []
          for i in json:
            c+=1
            m.append(InlineKeyboardButton(text=f"{c}",callback_data=f'yukla-{i[0]}'))
          key.add(*m)
          bot.send_photo(cid,photo=all[2],caption=f"<b>#{name} - seriali!\n\n🎬 Qisimlar: {len(json)}</b>",reply_markup=key)
          
      elif 'f' in code and join(cid,code):
        code = code.replace("f","")
        check = cursor.execute(f"SELECT * FROM kino WHERE id={code}").fetchone()
        if check:
          json = cursor.execute(f"SELECT * FROM kino WHERE id={code}").fetchone()
          bot.send_video(cid,json[1],protect_content=True,reply_markup=share_button())
        else:
          bot.send_message(cid,"kod xato!")
      elif 'F' in code:
        code = code.replace("F","")
        check = cursor.execute(f"SELECT * FROM kino WHERE id={code}").fetchone()
        if check:
          json = cursor.execute(f"SELECT * FROM kino WHERE id={code}").fetchone()
          bot.send_video(cid,json[1],protect_content=True,reply_markup=share_button())
        else:
          bot.send_message(cid,"kod xato!")
        





@bot.message_handler(content_types=['video'])
def add_video(msg):
  if msg.chat.id==ADMIN_ID or msg.chat.id == BOSHLIQ:
    file_id=msg.video.file_id
    caption = msg.caption
    FILE_ID['id'] = file_id
    CAPTION['text']=caption
    key = InlineKeyboardMarkup()
    js = cursor.execute("SELECT * FROM serial").fetchall()
    for i in js:
      key.add(InlineKeyboardButton(text=f"{i[1]}",callback_data=f"newserial-{i[0]}"))
    key.add(InlineKeyboardButton(text="🚫 Bez serial",callback_data="solo"))
    bot.reply_to(msg,"Serial nomini tanlanag!",reply_markup=key)
  
@bot.message_handler(content_types=['text'])
def custom(msg):
  cid = msg.chat.id
  text = msg.text
  if text=='/panel' and cid==BOSHLIQ:
    bot.reply_to(msg,"<b>Admin panelga xush kelibsiz!</b>",reply_markup=admin_panel())
  try:
    if text=="📊 Statistika":
      try:
        count_serial = cursor.execute("SELECT COUNT(id) FROM serial").fetchone()[0]
        count_movie = cursor.execute("SELECT COUNT(id) FROM movies").fetchone()[0]      
        users = cursor.execute("SELECT COUNT(id) FROM users").fetchone()[0]
        kino = cursor.execute("SELECT COUNT(id) FROM kino").fetchone()[0]
        txt = f"""<b>
Bot statistikasi 📊

👤 Obunachilar: {users} ta  
🎥 Kinolar: {kino} ta

📺 Seriallar: {count_serial} ta
🎬 Serial qismi: {count_movie} ta

</b>
      """
        bot.send_message(cid,txt)
      except Exception as e:
        print(e)

      
    if text=="✉ Oddiy xabar" and cid==BOSHLIQ:
      a = bot.send_message(cid,"<b>Xabar matnini kiriting: </b>")
      bot.register_next_step_handler(a,oddiy_xabar)
    elif text=="✉ Forward xabar" and cid==BOSHLIQ:
      a = bot.send_message(cid,"<b>Xabar matnini yuboring: </b>")
      bot.register_next_step_handler(a,forward_xabar)
    elif text=="➕ Serial qo'shish" and cid==BOSHLIQ:
      a = bot.send_message(cid,"<b>Seryal nomini yuboring!</b>",reply_markup=back)
      bot.register_next_step_handler(a,new_serial)
    elif text=="🗑 Kino ochirish" and cid==BOSHLIQ:
      a = bot.send_message(cid,"<b>🎥 Kino kodini yuboring!</b>",reply_markup=back)
      bot.register_next_step_handler(a,del_kino)
    elif text=="📺 Seriallar" and cid==BOSHLIQ:
      js = cursor.execute("SELECT * FROM serial").fetchall()
      key = InlineKeyboardMarkup()
      for i in js:
        key.add(InlineKeyboardButton(text=f"{i[1]}",callback_data=f"info-{i[0]}"))
      bot.send_message(cid,"<b>Kerkali serialni  tanlang!</b>",reply_markup=key)
  except:
    pass





@bot.callback_query_handler(func=lambda call:True)
def callback(call):
  cid = call.message.chat.id
  mid = call.message.id
  data = call.data      
    
  if data=='solo':
    try:
      file_id = FILE_ID['id']
      caption =CAPTION['text'].replace("'","||")
      all = cursor.execute("SELECT * FROM kino").fetchall()
      if len(all)==0:
        code = 1
      else:
        code = all[-1][0]+1
      cursor.execute(f"INSERT INTO kino(file_id,caption) VALUES('{file_id}','{caption}')")
      bot.send_video(cid,video=file_id,caption=f"https://xeact.uz/link.php?link=f{code}",reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="📥 Yuklab olish",url=f"https://t.me/Xeact_bot?start=f{code}")))

    except Exception as e:
      print(e)
  elif "serial" in data:
    id  = data.split("-")[1]
    bot.delete_message(cid,mid)
    file_id = FILE_ID['id']
    caption =CAPTION['text'].replace("'","||")
    all = cursor.execute("SELECT * FROM movies").fetchall()
    if len(all)==0:
      code = 1
    else:
      code = all[-1][0]+1
    serial = cursor.execute(f"SELECT * FROM serial WHERE id={id}").fetchone()[1]
    cursor.execute(f"INSERT INTO movies(file_id,caption,serial) VALUES('{file_id}','{caption}','{serial}')")
    bot.send_video(cid,video=file_id,caption=f"https://xeact.uz/link.php?link=s{id}",reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="📥 Yuklab olish",url=f"https://t.me/Xeact_bot?start=s{id}")))
  
  elif "yukla" in data:
    id  = data.split("-")[1]
    json = cursor.execute(f"SELECT * FROM movies WHERE id={id}").fetchone()
    bot.send_video(cid,video=json[1],caption=json[2].replace("||","'"))
  elif "info" in data:
    id  = data.split("-")[1]
    json = cursor.execute(f"SELECT * FROM serial WHERE id={id}").fetchone()
    get = cursor.execute(F"SELECT * FROM movies WHERE serial='{json[1]}'").fetchall()
    c = 0
    key = InlineKeyboardMarkup(row_width=4)
    m = []
    for i in get:
      c+=1
      m.append(InlineKeyboardButton(text=f"🗑 {c}",callback_data=f'del-{i[0]}'))
    key.add(*m)
    key.add(InlineKeyboardButton(text=f"❌ Serial",callback_data=f'remove-{id}'),InlineKeyboardButton(text=f"Post share",callback_data=f'share-{id}'))
    bot.send_photo(cid,photo=json[2],caption=f"<b>🎥 Serial: {json[1]}\n📥 Yuklash: https://xeact.uz/link.php?link=s{id}\n🎬 Qisimlar: {c}</b>",reply_markup=key)
  elif "del" in data:
    id  = data.split("-")[1]
    bot.delete_message(cid,mid)
    cursor.execute(f"DELETE FROM movies WHERE id={id}")
    js = cursor.execute("SELECT * FROM serial").fetchall()
    key = InlineKeyboardMarkup()
    for i in js:
      key.add(InlineKeyboardButton(text=f"{i[1]}",callback_data=f"info-{i[0]}"))
    bot.send_message(cid,"<b>❌ Serial qismi o'chirildi!</b>",reply_markup=key)
  elif "remove" in data:
    id  = data.split("-")[1]
    bot.delete_message(cid,mid)
    cursor.execute(f"DELETE FROM serial WHERE id={id}")
    conn.commit()
    js = cursor.execute("SELECT * FROM serial").fetchall()
    key = InlineKeyboardMarkup()
    for i in js:
      key.add(InlineKeyboardButton(text=f"{i[1]}",callback_data=f"info-{i[0]}"))
    bot.send_message(cid,"<b>❌ Serial o'chirildi!</b>",reply_markup=key)
  elif "share" in data:
    id  = data.split("-")[1]
    js = cursor.execute(f"SELECT * FROM serial WHERE id={id}").fetchone()
    print(js)
    bot.send_photo("@Akhatkulov",photo=js[2],caption=f""""<b>
🎬 Nomi: {js[1]} 

🗣 Ovoz berdi : AniTrend
🎥 Qismilari: {5}
🌍 Davlati: Yaponiya
🇺🇿 Tili: O'zbek tilida
📆 Yili: 2023

#⃣ #{js[1]}
</b>
""",reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="📥 Yuklab olish",url=f"https://t.me/Xeact_bot?start=s{id}")))


#app.run(host='0.0.0.0', port=81)
print(bot.get_me())
bot.polling()
