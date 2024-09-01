import re
import time
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

import conf

bot = Bot(token=conf.BOT_TOKEN)
dp = Dispatcher(bot)

admin_id = conf.ADMIN_ID

async def get_message_x(client, chat_id, message_id):
    try:
        return await client.forward_message(chat_id=conf.DUMB_CHANNEL_ID, from_chat_id=chat_id, message_id=message_id)
    except Exception as e:
        if 'Too Many Requests' in str(e):
            wait_time = int(re.search(r'\d+', str(e)).group())
            await asyncio.sleep(wait_time)
            return await client.forward_message(chat_id=conf.DUMB_CHANNEL_ID, from_chat_id=chat_id, message_id=message_id)
        else:
            print(f"Failed to retrieve message: {e}")
            return None

async def get_messages(client, message_ids):
    messages = []
    print("get_messages() message_ids: ",message_ids)
    for message_id in message_ids:
        msg = await get_message_x(client, conf.CHANNEL_ID, message_id)
        if msg:
            messages.append(msg)
        else:
            print("xabar topilmadi!")
    return messages

def get_message_id(message):
    if message.forward_from_chat and message.forward_from_chat.id == conf.CHANNEL_ID:
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
            if f"-100{channel_id}" == str(conf.CHANNEL_ID):
                return msg_id
        elif channel_id == conf.CHANNEL_USERNAME:
            return msg_id
    return 0


# import re
# import time
# import asyncio

# from aiogram import Bot, Dispatcher, types
# from aiogram.utils import executor

# import conf

# bot = Bot(token=conf.BOT_TOKEN)
# dp = Dispatcher(bot)

# admin_id = conf.ADMIN_ID

# async def get_message_x(client, chat_id, message_id):
#     try:
#         return await client.forward_message(chat_id=conf.DUMB_CHANNEL_ID, from_chat_id=chat_id, message_ids=message_id)
#     except Exception as e:
#         if 'Too Many Requests' in str(e):
#             wait_time = int(re.search(r'\d+', str(e)).group())
#             await asyncio.sleep(wait_time)
#             return await client.forward_message(chat_id=conf.DUMB_CHANNEL_ID, from_chat_id=chat_id, message_ids=message_id)
#         else:
#             print(f"Failed to retrieve message: {e}")
#             return None

# async def get_messages(client, message_ids):
#     messages = []
#     for message_id in message_ids:
#         msg = await get_message_x(client, conf.CHANNEL_ID, message_id)
#         if msg:
#             messages.append(msg)
#     return messages

# def get_message_id(message):
#     if message.forward_from_chat and message.forward_from_chat.id == conf.CHANNEL_ID:
#         return message.forward_from_message_id
#     elif message.forward_from_chat or message.forward_sender_name or not message.text:
#         return 0
#     else:
#         pattern = r"https://t.me/(?:c/)?(.*)/(\\d+)"
#         matches = re.match(pattern, message.text)
#         if not matches:
#             return 0
#         channel_id = matches.group(1)
#         msg_id = int(matches.group(2))
#         if channel_id.isdigit():
#             if f"-100{channel_id}" == str(conf.CHANNEL_ID):
#                 return msg_id
#         elif channel_id == conf.CHANNEL_USERNAME:
#             return msg_id
#     return 0


# import re
# import time

# from aiogram import Bot, Dispatcher, types
# from aiogram.exceptions import TelegramAPIError
# from aiogram.utils import executor

# import conf

# bot = Bot(token=conf.BOT_TOKEN)
# dp = Dispatcher(bot)

# admin_id = conf.ADMIN_ID

# async def get_message_x(client, chat_id, message_id):
#     try:
#         return await client.forward_messages(chat_id=conf.DUMB_CHANNEL_ID, from_chat_id=chat_id, message_ids=message_id)
#     except TelegramAPIError as e:
#         if 'Too Many Requests' in str(e):
#             wait_time = int(re.search(r'\d+', str(e)).group())
#             await asyncio.sleep(wait_time)
#             return await client.forward_messages(chat_id=conf.DUMB_CHANNEL_ID, from_chat_id=chat_id, message_ids=message_id)
#         else:
#             print(f"Failed to retrieve message: {e}")
#             return None

# async def get_messages(client, message_ids):
#     messages = []
#     for message_id in message_ids:
#         msg = await get_message_x(client, conf.CHANNEL_ID, message_id)
#         if msg:
#             messages.append(msg)
#     return messages

# def get_message_id(message):
#     if message.forward_from_chat and message.forward_from_chat.id == conf.CHANNEL_ID:
#         return message.forward_from_message_id
#     elif message.forward_from_chat or message.forward_sender_name or not message.text:
#         return 0
#     else:
#         pattern = r"https://t.me/(?:c/)?(.*)/(\\d+)"
#         matches = re.match(pattern, message.text)
#         if not matches:
#             return 0
#         channel_id = matches.group(1)
#         msg_id = int(matches.group(2))
#         if channel_id.isdigit():
#             if f"-100{channel_id}" == str(conf.CHANNEL_ID):
#                 return msg_id
#         elif channel_id == conf.CHANNEL_USERNAME:
#             return msg_id
#     return 0




# import re
# import asyncio
# from aiogram import Bot, Dispatcher
# from aiogram.types import Message
# from aiogram.utils.exceptions import RetryAfter

# import conf

# bot = Bot(token=conf.BOT_TOKEN)
# dp = Dispatcher(bot)

# admin_id = conf.ADMIN_ID

# async def fetch_messages(chat_id: int, limit: int = 100) -> list[Message]:
#     messages = []
#     try:
#         async for message in bot.get_chat_history(chat_id, limit=limit):
#             messages.append(message)
#     except RetryAfter as e:
#         await asyncio.sleep(e.timeout)
#         return await fetch_messages(chat_id, limit)
#     except Exception as e:
#         print(f"Error: {e}")
#     return messages

# async def get_messages(chat_id: int, message_ids: list[int]) -> list[Message]:
#     all_messages = await fetch_messages(chat_id, limit=1000)  # Adjust limit as needed
#     message_map = {message.message_id: message for message in all_messages}
#     messages = [message_map.get(message_id) for message_id in message_ids if message_id in message_map]
#     return messages

# async def get_message_id(message: Message, db_channel_id: int, db_channel_username: str) -> int:
#     if message.forward_from_chat:
#         if message.forward_from_chat.id == db_channel_id:
#             return message.forward_from_message_id
#         else:
#             return 0
#     elif message.forward_sender_name:
#         return 0
#     elif message.text:
#         pattern = r"https://t.me/(?:c/)?(.*)/(\d+)"
#         matches = re.match(pattern, message.text)
#         if not matches:
#             return 0
#         channel_id = matches.group(1)
#         msg_id = int(matches.group(2))
#         if channel_id.isdigit():
#             if f"-100{channel_id}" == str(db_channel_id):
#                 return msg_id
#         else:
#             if channel_id == db_channel_username:
#                 return msg_id
#     else:
#         return 0


# import re
# import asyncio
# from aiogram import Bot, Dispatcher
# from aiogram.types import Message
# from aiogram.utils.exceptions import RetryAfter

# import conf

# bot = Bot(token=conf.BOT_TOKEN)
# dp = Dispatcher(bot)

# admin_id = conf.ADMIN_ID

# async def fetch_messages(chat_id: int, limit: int = 100) -> list[Message]:
#     messages = []
#     try:
#         async for message in bot.get_chat(chat_id).iter_messages(limit=limit):
#             messages.append(message)
#     except RetryAfter as e:
#         await asyncio.sleep(e.timeout)
#         return await fetch_messages(chat_id, limit)
#     except Exception as e:
#         print(f"Error: {e}")
#     return messages

# async def get_messages(chat_id: int, message_ids: list[int]) -> list[Message]:
#     all_messages = await fetch_messages(chat_id, limit=1000)  # Adjust limit as needed
#     message_map = {message.message_id: message for message in all_messages}
#     messages = [message_map.get(message_id) for message_id in message_ids if message_id in message_map]
#     return messages

# async def get_message_id(message: Message, db_channel_id: int, db_channel_username: str) -> int:
#     if message.forward_from_chat:
#         if message.forward_from_chat.id == db_channel_id:
#             return message.forward_from_message_id
#         else:
#             return 0
#     elif message.forward_sender_name:
#         return 0
#     elif message.text:
#         pattern = r"https://t.me/(?:c/)?(.*)/(\d+)"
#         matches = re.match(pattern, message.text)
#         if not matches:
#             return 0
#         channel_id = matches.group(1)
#         msg_id = int(matches.group(2))
#         if channel_id.isdigit():
#             if f"-100{channel_id}" == str(db_channel_id):
#                 return msg_id
#         else:
#             if channel_id == db_channel_username:
#                 return msg_id
#     else:
#         return 0


# import re
# import asyncio
# from aiogram import Bot, Dispatcher
# from aiogram.types import Message
# from aiogram.utils.exceptions import RetryAfter

# import conf

# bot = Bot(token=conf.BOT_TOKEN)
# dp = Dispatcher(bot)

# admin_id = conf.ADMIN_ID

# async def fetch_messages(chat_id: int, limit: int = 100) -> list[Message]:
#     messages = []
#     try:
#         async for message in bot.get_chat_history(chat_id, limit=limit):
#             messages.append(message)
#     except RetryAfter as e:
#         await asyncio.sleep(e.timeout)
#         return await fetch_messages(chat_id, limit)
#     except Exception as e:
#         print(f"Error: {e}")
#     return messages

# async def get_messages(chat_id: int, message_ids: list[int]) -> list[Message]:
#     all_messages = await fetch_messages(chat_id, limit=1000)  # Adjust limit as needed
#     message_map = {message.message_id: message for message in all_messages}
#     messages = [message_map.get(message_id) for message_id in message_ids if message_id in message_map]
#     return messages

# async def get_message_id(message: Message, db_channel_id: int, db_channel_username: str) -> int:
#     if message.forward_from_chat:
#         if message.forward_from_chat.id == db_channel_id:
#             return message.forward_from_message_id
#         else:
#             return 0
#     elif message.forward_sender_name:
#         return 0
#     elif message.text:
#         pattern = r"https://t.me/(?:c/)?(.*)/(\d+)"
#         matches = re.match(pattern, message.text)
#         if not matches:
#             return 0
#         channel_id = matches.group(1)
#         msg_id = int(matches.group(2))
#         if channel_id.isdigit():
#             if f"-100{channel_id}" == str(db_channel_id):
#                 return msg_id
#         else:
#             if channel_id == db_channel_username:
#                 return msg_id
#     else:
#         return 0



# import re
# import asyncio
# from aiogram import Bot, Dispatcher
# from aiogram.types import Message
# from aiogram.utils.exceptions import RetryAfter

# import conf

# bot = Bot(token=conf.BOT_TOKEN)
# dp = Dispatcher(bot)

# admin_id = conf.ADMIN_ID

# async def get_message(chat_id: int, message_id: int) -> Message:
#     try:
#         return await bot.get_message(chat_id=chat_id, message_id=message_id)
#     except RetryAfter as e:
#         await asyncio.sleep(e.timeout)
#         return await get_message(chat_id, message_id)
#     except Exception as e:
#         print(f"Error: {e}")
#         return None

# async def get_messages(bot, chat_id: int, message_ids: list[int]) -> list[Message]:
#     messages = []
#     for message_id in message_ids:
#         msg = await get_message(chat_id, message_id)
#         if msg:
#             messages.append(msg)
#     return messages

# async def get_message_id(message: Message, db_channel_id: int, db_channel_username: str) -> int:
#     if message.forward_from_chat:
#         if message.forward_from_chat.id == db_channel_id:
#             return message.forward_from_message_id
#         else:
#             return 0
#     elif message.forward_sender_name:
#         return 0
#     elif message.text:
#         pattern = r"https://t.me/(?:c/)?(.*)/(\d+)"
#         matches = re.match(pattern, message.text)
#         if not matches:
#             return 0
#         channel_id = matches.group(1)
#         msg_id = int(matches.group(2))
#         if channel_id.isdigit():
#             if f"-100{channel_id}" == str(db_channel_id):
#                 return msg_id
#         else:
#             if channel_id == db_channel_username:
#                 return msg_id
#     else:
#         return 0



# import re
# import asyncio
# from aiogram import Bot, Dispatcher
# from aiogram.types import Message
# from aiogram.utils.exceptions import RetryAfter

# import conf

# bot = Bot(token=conf.BOT_TOKEN)
# dp = Dispatcher(bot)

# admin_id = conf.ADMIN_ID

# async def get_message(chat_id: int, message_id: int) -> Message:
#     try:
#         async for message in bot.get_chat_history(chat_id=chat_id, limit=1, offset_id=message_id):
#             return message
#     except RetryAfter as e:
#         await asyncio.sleep(e.timeout)
#         return await get_message(chat_id, message_id)
#     except Exception as e:
#         print(f"Error: {e}")
#         return None

# async def get_messages(bot, chat_id: int, message_ids: list[int]) -> list[Message]:
#     messages = []
#     for message_id in message_ids:
#         msg = await get_message(chat_id, message_id)
#         if msg:
#             messages.append(msg)
#     return messages

# async def get_message_id(message: Message, db_channel_id: int, db_channel_username: str) -> int:
#     if message.forward_from_chat:
#         if message.forward_from_chat.id == db_channel_id:
#             return message.forward_from_message_id
#         else:
#             return 0
#     elif message.forward_sender_name:
#         return 0
#     elif message.text:
#         pattern = r"https://t.me/(?:c/)?(.*)/(\d+)"
#         matches = re.match(pattern, message.text)
#         if not matches:
#             return 0
#         channel_id = matches.group(1)
#         msg_id = int(matches.group(2))
#         if channel_id.isdigit():
#             if f"-100{channel_id}" == str(db_channel_id):
#                 return msg_id
#         else:
#             if channel_id == db_channel_username:
#                 return msg_id
#     else:
#         return 0





# import re
# import asyncio  # Import asyncio for sleep
# from aiogram import Bot, Dispatcher
# from aiogram.types import Message
# from aiogram.utils.exceptions import RetryAfter

# import conf

# bot = Bot(token=conf.BOT_TOKEN)
# dp = Dispatcher(bot)

# admin_id = conf.ADMIN_ID

# async def get_messages(bot, chat_id: int, message_ids: list[int]) -> list[Message]:
#     messages = []
#     total_messages = 0
#     while total_messages != len(message_ids):
#         temb_ids = message_ids[total_messages:total_messages + 200]
#         try:
#             msgs = await bot.get_messages(chat_id=chat_id, message_ids=temb_ids)
#         except RetryAfter as e:  # Corrected exception type
#             await asyncio.sleep(e.timeout)
#             msgs = await bot.get_messages(chat_id=chat_id, message_ids=temb_ids)
#         except Exception as e:
#             print(f"Error: {e}")
#             continue
#         total_messages += len(temb_ids)
#         messages.extend(msgs)
#     return messages

# async def get_message_id(message: Message, db_channel_id: int, db_channel_username: str) -> int:
#     if message.forward_from_chat:
#         if message.forward_from_chat.id == db_channel_id:
#             return message.forward_from_message_id
#         else:
#             return 0
#     elif message.forward_sender_name:
#         return 0
#     elif message.text:
#         pattern = r"https://t.me/(?:c/)?(.*)/(\d+)"
#         matches = re.match(pattern, message.text)
#         if not matches:
#             return 0
#         channel_id = matches.group(1)
#         msg_id = int(matches.group(2))
#         if channel_id.isdigit():
#             if f"-100{channel_id}" == str(db_channel_id):
#                 return msg_id
#         else:
#             if channel_id == db_channel_username:
#                 return msg_id
#     else:
#         return 0




# # async def get_message_x(client, chat_id, message_id):
# #     try:
# #         msg = await client.forward_message(chat_id=conf.DUMB_CHANNEL_ID, from_chat_id=chat_id, message_id=message_id)
# #         return msg

# #     except RetryAfter as e:
# #         await asyncio.sleep(e.timeout)
# #         return await client.forward_message(chat_id=conf.DUMB_CHANNEL_ID, from_chat_id=chat_id, message_id=message_id)

# #     except Exception as e:
# #         print(f"Failed to retrieve message: {e}")
# #         return None

# # async def get_messages(client, message_ids):
# #     messages = []
# #     for message_id in message_ids:
# #         msg = await get_message_x(client, client.id, message_id)
# #         if msg:
# #             messages.append(msg)
# #     return messages

# # def get_message_id(message: Message):
# #     if message.forward_from_chat and message.forward_from_chat.id == bot.db_channel.id:
# #         return message.forward_from_message_id
# #     elif message.forward_from_chat or message.forward_sender_name or not message.text:
# #         return 0
# #     else:
# #         pattern = r"https://t.me/(?:c/)?(.*)/(\\d+)"
# #         matches = re.match(pattern, message.text)
# #         if not matches:
# #             return 0
# #         channel_id = matches.group(1)
# #         msg_id = int(matches.group(2))
# #         if channel_id.isdigit():
# #             if f"-100{channel_id}" == str(bot.db_channel.id):
# #                 return msg_id
# #         elif channel_id == bot.db_channel.username:
# #             return msg_id
# #     return 0
