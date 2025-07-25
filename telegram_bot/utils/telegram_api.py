import logging
import httpx
from ..bot import TELEGRAM_TOKEN

async def delete_message(chat_id, message_id):
    URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteMessage"
    payload = {
        'chat_id': chat_id,
        'message_id': message_id
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(URL, json=payload)
            response.raise_for_status()
            logging.info(f"✅ Message deleted: {chat_id} | {message_id}")
        return True
    except httpx.HTTPStatusError as http_err:
        logging.error(f"There was HTTP error in deleting the message: {http_err}")
    except httpx.RequestError as req_err:
        logging.error(f"There was request error in deleting the message: {req_err}")
    except Exception as e:
        logging.exception(f"There was an error in deleting the message: {e}")
    return False

async def send_message(chat_id, text):
    URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(URL, json=payload)
            response.raise_for_status()
            response_data = response.json()
            reply_message_id = response_data['result']['message_id']
            logging.info(f'✅ Reply message sent: {response_data}')
        return reply_message_id
    except httpx.HTTPStatusError as http_err:
        logging.error(f'There was HTTP error in sending message: {http_err}')
    except httpx.RequestError as req_err:
        logging.error(f'There was request error in sending message: {req_err}')
    except Exception as e:
        logging.exception(f'There was an error in sending message: {e}')
    return None