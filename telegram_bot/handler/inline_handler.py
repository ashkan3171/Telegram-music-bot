import logging
import httpx
from ..bot import TELEGRAM_TOKEN
from telegram_bot.db.models import User, Playlist

async def handle_inline_query(inline_query):
    user_id = inline_query['from']['id']
    inline_query_id = inline_query['id']

    user = await User.get_or_none(user_id=user_id)
    if not user:
        return inline_query_id, [{
            "type": "article",
            "id": "no-user",
            "title": "😕 You are not registered",
            "input_message_content": {"message_text": "Please /start the bot first."}
        }]

    playlists = await Playlist.filter(user=user).prefetch_related('music')
    results = []

    if not playlists:
        results.append({
            "type": "article",
            "id": "no-result",
            "title": "😕 Your playlist is empty",
            "input_message_content": {"message_text": "🎧 You don't have any music in your playlist yet."}
        })
    else:
        for idx, pl in enumerate(playlists):
            music = pl.music
            duration_minute = music.duration // 60
            duration_second = music.duration % 60
            duration_str = f"{duration_minute}:{duration_second:02d}"
            results.append({
                "type": "article",
                "id": str(idx),
                "title": music.title,
                "description": f"⏱ {duration_str}",
                "input_message_content": {"message_text": f"🎵 {music.title}\n🔗 {music.youtube_url}"},
                "reply-markup":{
                    "inline_keyboard": [[
                        {"text": "▶ Play", "callback_data": f"playlsit_music:{music.music_id}"}
                    ]]
                }
            })
    return inline_query_id, results

async def playlist_inline_query(inline_query_id, results):
    URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/answerInlineQuery"
    payload = {
        'inline_query_id': inline_query_id,
        'results': results,
        'cache_time': 1,
        'is_personal': True
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(URL, json=payload)
        response.raise_for_status()
        return True
