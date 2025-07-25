import logging
import httpx
from ..bot import TELEGRAM_TOKEN
from telegram_bot.db.models import Playlist, User, Music

async def add_favorite(callback):
    URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/editMessageReplyMarkup"

    chat_id = callback['message']['chat']['id']
    message_id = callback['message']['message_id']
    music_id = callback['data'].split(':')[1]

    user = await User.get_or_none(chat_id=chat_id)
    if not user:
        logging.warning(f"⚠️ User not found in DB for chat_id={chat_id}")
        return False
    
    music = await Music.get_or_none(music_id=music_id)
    if not music:
        logging.warning(f"⚠️ Music not found in DB for music_id={music_id}")
        return False
    
    exists = await Playlist.get_or_none(user=user, music=music)
    if not exists:
        await Playlist.create(user=user, music=music)
        logging.info(f"🎵 Added {music.title} to playlist for {user.first_name}")

    payload = {
        'chat_id': chat_id,
        'message_id': message_id,
        'reply_markup': {
            'inline_keyboard':[
                [
                    {'text': '❤️', 'callback_data': f"unfavorite:{music_id}"},
                    {'text': '📂 Playlist',  'switch_inline_query_current_chat': 'playlist'}
                ]
            ]
        }
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(URL, json=payload)
            response.raise_for_status()
            response_data = response.json()
            logging.info(f"✅ Added to favorite: {response_data}")
            return True
    except httpx.HTTPStatusError as http_err:
        logging.error(f"There was HTTP error in adding the music into favorite: {http_err}")
    except httpx.RequestError as req_err:
        logging.error(f"There was request error in adding the music into favorite: {req_err}")
    except Exception as e:
        logging.exception(f"There was an error in adding the music into favorite: {e}")
    return False

async def remove_favorite(callback):
    URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/editMessageReplyMarkup"
    
    chat_id = callback['message']['chat']['id']
    message_id = callback['message']['message_id']
    music_id = callback['data'].split(':')[1]

    user = await User.get_or_none(chat_id=chat_id)
    if not user:
        logging.warning(f"⚠️ User not found for chat_id={chat_id}")
        return False
    
    music = await Music.get_or_none(music_id=music_id)
    if not music:
        logging.warning(f"⚠️ Music not found for music_id={music_id}")
        return False
    
    deleted = await Playlist.filter(user=user, music=music).delete()
    if deleted:
        logging.info(f"🗑 Removed {music.title} from playlist of {user.first_name}")
    else:
        logging.info(f"ℹ️ Music not in playlist for {user.first_name}")

    payload = {
        'chat_id': chat_id,
        'message_id': message_id,
        'reply_markup':{
            'inline_keyboard':[
                [
                    {'text': '🖤', 'callback_data': f"favorite:{music_id}"},
                    {'text': '📂 Playlist', 'switch_inline_query_current_chat': 'playlist'}
                ]
            ]
        }
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(URL, json=payload)
            response.raise_for_status()
            response_data = response.json()
            logging.info(f"✅ Removed from favorite: {response_data}")
            return True
    except httpx.HTTPStatusError as http_err:
        logging.error(f"There was HTTP error in removing the music from favorite: {http_err}")
    except httpx.RequestError as req_err:
        logging.error(f"There was request error in removing the music from favorite: {req_err}")
    except Exception as e:
        logging.exception(f"There was an error in removing the music from favorite: {e}")
    return False