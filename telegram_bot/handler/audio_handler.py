import httpx
from yt_dlp import YoutubeDL
import logging
from ..bot import TELEGRAM_TOKEN
import json
from telegram_bot.db.models import Music, SearchLog
import os

async def search_music(query):
    existing_log = await SearchLog.get_or_none(query=query)
    if existing_log:
        logging.info(f"🔄 Using cached results for query: {query}")
        return existing_log.results

    search_url = f'ytsearch5:{query} Official Lyric Song'
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'cookiefile': 'cookies.txt'
    }

    results = []
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_url, download=False)
            entries = info.get('entries', [])
            for idx, entry in enumerate(entries):
                duration = entry.get('duration', 0)
                duration_minute = duration // 60
                duration_second = duration % 60
                duration_format = f"{duration_minute}:{duration_second:02d}"
                result = {
                    'idx': idx,
                    'music_id': entry.get('id', ''),
                    'title': entry.get('title', ''),
                    'duration': duration_format,
                    'youtube_url': entry.get('webpage_url', ''),
                    'uploader': entry.get('uploader')
                }
                results.append(result)
        await SearchLog.create(query=query, results=results)
        logging.info(f"💾 Cached results for query: {query}")
        return results

    except Exception as e:
        logging.exception(f'There was an error in searching musics: {e}')
    return []

async def download_music(music_id):
    os.makedirs("music", exist_ok=True)
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'outtmpl': 'music/%(title)s.mp3',
        'cookiefile': 'cookies.txt'
    }
    result = None
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(music_id, download=True)
            if info:
                result = {
                    'music_id': music_id,
                    'title' : info.get('title', ''),
                    'duration' : info.get('duration', 0),
                    'uploader' : info.get('uploader'),
                    'youtube_url' : info.get('webpage_url', ''),
                    'audio_file' : ydl.prepare_filename(info)
                }
        return result
    except Exception as e:
        logging.exception(f'There was error in downloading the music: {e}')
    return None

async def send_music(chat_id, music_data):
    URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendAudio"
    caption = f"🔗 {music_data['youtube_url']}"
    
    try:
        async with httpx.AsyncClient() as client:
            with open (music_data['audio_file'], 'rb') as audio:
                files ={'audio':(music_data['audio_file'], audio, 'audio/mpeg')}
                data = {
                    'chat_id': chat_id,
                    'caption': caption,
                    'duration': music_data.get('duration', 0),
                    'title': music_data.get('title', ''),
                    'performer': music_data.get('uploader', ''),
                    'youtube_url': music_data.get('webpage_url', ''),
                    'reply_markup': json.dumps({
                        'inline_keyboard': [
                            [
                                {'text': '🖤', 'callback_data': f"favorite:{music_data['music_id']}"},
                                {'text': '📂 Playlist',  'switch_inline_query_current_chat': 'playlist'}
                            ]
                        ]
                    })
                }
                response = await client.post(URL, files=files, data=data)
                response.raise_for_status()
                response_data = response.json()
                logging.info(f"✅ Music sent to chat_id={chat_id}")
                logging.info(f"{response_data}")
                return True
    except httpx.HTTPStatusError as http_err:
        logging.error(f"There was HTTP error in sending music: {http_err}")
    except httpx.RequestError as req_err:
        logging.error(f"There was request error in sending music: {req_err}")
    except Exception as e:
        logging.exception(f"There was an error in sending the music: {e}")
    return False

async def save_music(music_data):
    try:
        existing = await Music.get_or_none(music_id=music_data['music_id'])
        if existing:
            return existing
        
        new_music = await Music.create(
            music_id=music_data['music_id'],
            title=music_data['title'],
            duration=music_data['duration'],
            youtube_url=music_data['youtube_url']
        )
        return new_music
    except Exception as e:
        logging.exception(f"There was an error in saving music: {e}")