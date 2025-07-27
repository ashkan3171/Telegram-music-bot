import logging
import httpx
from ..bot import TELEGRAM_TOKEN

async def send_choices(chat_id, founded_music):
    URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    inline_keyboard = []
    for music in founded_music:
        button = {
            'text': f"{music['idx']+1} | {music['title'][:40]} ⏱ {music['duration_str']}",
            'callback_data': f"{music['music_id']}"
        }
        inline_keyboard.append([button])
    payload = {
        'chat_id': chat_id,
        'text': f'🎶 Please choose a song',
        'reply_markup': {
            'inline_keyboard': inline_keyboard
        }
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(URL, json=payload)
            response.raise_for_status()
            response_data= response.json()
            logging.info(f"✅ Sent choices: {response_data}")
        return True
    except httpx.HTTPStatusError as http_err:
        logging.error(f"There was HTTP error in sending the choices: {http_err}")
    except httpx.RequestError as req_err:
        logging.error(f"There was a request error in sending message: {req_err}")
    except Exception as e:
        logging.exception(f"There was an error in sending choices: {e}")
    return False

async def disable_button(chat_id, message_id, text):
    URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/editMessageText"
    payload = {
        'chat_id':chat_id,
        'message_id': message_id,
        'text': text,
        'reply_markup': {
            'inline_keyboard':[]
        }
    }   
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(URL, json=payload)
            response.raise_for_status()
        logging.info(f"✅ Disabled inline buttons for message_id={message_id} in chat_id={chat_id}")
        return True
    except httpx.HTTPStatusError as http_err:
        logging.error(f"There was HTTP error in disabling choices: {http_err}")
    except httpx.RequestError as req_err:
        logging.error(f"There was a request error in disabling choices: {req_err}")
    except Exception as e:
        logging.exception(f"There was an error in disabling choices: {e}")
    return False