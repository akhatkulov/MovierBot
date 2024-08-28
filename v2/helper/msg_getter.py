import re
import time
from telebot import TeleBot
import conf

client = TeleBot(conf.BOT_TOKEN)

def get_message_id(client, message):
    if (
        message.forward_from_chat
        and message.forward_from_chat.id == client.db_channel.id
    ):
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
            if f"-100{channel_id}" == str(client.db_channel.id):
                return msg_id
        elif channel_id == client.db_channel.username:
            return msg_id
    return 0

def get_messages(client, message_ids):
    messages = []
    total_messages = 0
    
    # This loop is kept for managing large sets of message IDs
    while total_messages < len(message_ids):
        temp_ids = message_ids[total_messages : total_messages + 200]
        
        for msg_id in temp_ids:
            # Since there's no get_message method, let's assume you can only manage messages
            # that have been received and stored in some way (like in a database or in-memory).
            # You could store the messages when they are received by the bot.
            
            try:
                # Simulating message retrieval based on a previously stored record
                # You should replace this with actual logic to retrieve messages if possible
                msg = None  # Replace with logic to fetch the message
                if msg:  # Assuming msg is retrieved successfully
                    messages.append(msg)
                else:
                    print(f"Message {msg_id} could not be found.")
            
            except Exception as e:
                print(f"Error fetching message {msg_id}: {e}")
                continue
        
        total_messages += len(temp_ids)
    
    return messages

# Example of setting up message storage
stored_messages = {}

@client.message_handler(func=lambda message: True)
def store_message(message):
    # Store the message in a dictionary for later retrieval
    stored_messages[message.message_id] = message

    # Example of using get_message_id
    msg_id = get_message_id(client, message)
    print(f"Retrieved message ID: {msg_id}")

# This function would replace the 'get_message' function:
def retrieve_stored_message(msg_id):
    return stored_messages.get(msg_id, None)


