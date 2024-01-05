from telebot.types import  *
import telebot
from database import *
NEW_SERIAL = {}

CAPTION = {}
FILE_ID = {}

ADMIN_ID = 571015717

bot = telebot.TeleBot("6786116368:AAFiPZc3pl5Ft5FPjP94_E7jXtomVHnlp3c",parse_mode='html')

back = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Cancel"))

def new_serial(msg):
  try:
    cid = msg.chat.id
    try:
      file_id = msg.photo[-1].file_id
      text = msg.caption.replace("'","||")
    except:
      pass
    if msg.text=="Cancel":
      bot.reply_to(msg,"<b>Bekor qilindi!</b>",reply_markup=admin_panel())
    else:
      cursor.execute(f"INSERT INTO serial(name,file_id) VALUES('{text}','{file_id}')")
      conn.commit()
      bot.send_photo(cid,file_id,caption="<b>✅ Yangi serial qo'shildi!</b>",reply_markup=admin_panel())
  except Exception  as e:
    print(e)
def del_kino(msg):
  try:
    cid = msg.chat.id
    
    text = msg.text
    if text=="Cancel":
      bot.reply_to(msg,"<b>Bekor qilindi!</b>",reply_markup=admin_panel())
    else:
      cursor.execute(f"DELETE FROM kino WHERE id={text}")
      conn.commit()
    bot.reply_to(msg,"<b>✅ Kino o'chirildi!</b>")
  except Exception  as e:
    print(e)

def share_button():
  key = InlineKeyboardMarkup()
  key.add(InlineKeyboardButton(text="Kinolar",url="t.me/Bolqiboyevuz"))
  # key.add(InlineKeyboardButton(text="Ulashish",url="t.me/Bolqiboyevuz"))
  return key


def admin_panel():
  key = ReplyKeyboardMarkup(resize_keyboard=True)
  key.add(
    KeyboardButton("📺 Seriallar"),
    KeyboardButton("➕ Serial qo'shish"))
  key.add(
    KeyboardButton("✉ Oddiy xabar"),
    KeyboardButton("✉ Forward xabar"),
  )
  key.add(
      KeyboardButton("📊 Statistika"),
      KeyboardButton("🗑 Kino ochirish")
  )
  return key




def oddiy_xabar(msg):
  success = 0
  error = 0
  stat = cursor.execute("SELECT chat_id FROM users").fetchall()
  for i in stat:
    print(i[0])
    try:
      success+=1
      bot.send_message(i[0],msg.text)
    except:
      error+=1
  bot.send_message(ADMIN_ID,f"<b>Xabar yuborildi!\n\n✅Yuborildi: {success}\n❌ Yuborilmadi: {error}</b>",reply_markup=admin_panel())
def forward_xabar(msg):
  success = 0
  error = 0
  stat = cursor.execute("SELECT chat_id FROM users").fetchall()
  for i in stat:
    print(i[0])
    try:
      success+=1
      bot.forward_message(i[0], ADMIN_ID, msg.message_id)
    except:
      error+=1
  bot.send_message(ADMIN_ID,f"<b>Xabar yuborildi!\n\n✅Yuborildi: {success}\n❌ Yuborilmadi: {error}</b>",reply_markup=admin_panel())



def join_key():
  keyboard = InlineKeyboardMarkup(row_width=1)
  keyboard.add(
      InlineKeyboardButton('1️⃣ - kanal', url='https://t.me/anime_trendlar_rasmiy'),
      InlineKeyboardButton('2️⃣ - kanal', url='https://t.me/anime_trendlar_chati'),
      InlineKeyboardButton('✅ Tasdiqlash', callback_data="member")
  )
  return keyboard
def join(user_id):
  try:
    member = bot.get_chat_member("@anime_trendlar_rasmiy", user_id)
    member1 = bot.get_chat_member("@anime_trendlar_chati", user_id)
  except:
    bot.send_message(user_id,"<b>👋 Assalomu alaykum Botni ishga tushurish uchun kanallarga a'zo bo'ling va a'zolikni tekshirish buyrug'ini bosing.</b>",parse_mode='html',reply_markup=join_key())

  x = ['member', 'creator', 'administrator']
  if member.status not in x or member1.status not in x:
    bot.send_message(user_id,"<b>👋 Assalomu alaykum Botni ishga tushurish uchun kanallarga a'zo bo'ling va a'zolikni tekshirish buyrug'ini bosing.</b>",parse_mode='html',reply_markup=join_key())
    return False
  else:
      return True