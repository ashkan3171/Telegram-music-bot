from fastapi import FastAPI, Request
import logging
import os
from html import escape
from telegram_bot.handler.command_handler import start_bot
from telegram_bot.utils.telegram_api import delete_message, send_message
from telegram_bot.handler.audio_handler import search_music, download_music, send_music, save_music
from telegram_bot.handler.button_handler import disable_button, send_choices
from telegram_bot.handler.favorite_handler import add_favorite, remove_favorite
from telegram_bot.handler.inline_handler import playlist_inline_query, handle_inline_query
from telegram_bot.db.db_utils import init_db, close_db
from telegram_bot.db.models import User, Music


logging.basicConfig(
    level=logging.INFO,  # Set to INFO or DEBUG to see more logs
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI()
registered_user = set()

@app.on_event('startup')
async def startup_event():
    await init_db()

app.on_event('shutdown')
async def shatdown_event():
    await close_db()

@app.post('/webhook')
async def telegram_webhook(req: Request):
    try:
        logging.info(f"Request recieved!")
        data = await req.json()
        logging.info(f"📥 Received update: {data}")

        if 'message' in data:
            # Collecting Info
            message_id = data['message']['message_id']
            chat_id = data['message']['chat']['id']
            first_name = data['message']['chat']['first_name']
            text = data['message'].get('text', '')
            safe_text = escape(text)

            if '/start' in safe_text:
                chat_id = data['message']['chat']['id']
                from_user = data['message']['from']
                chat = data['message']['chat']

                user_exist = await User.filter(user_id= from_user['id']).exists()
                if user_exist:
                    already_user_msg = await send_message(chat_id, 'You are already registered!')
                    if not already_user_msg:
                        logging.warning(f"⚠️ Couldn't send the user is already there message for :{chat_id}!")
                else:
                    await User.create(
                            user_id = from_user['id'],
                            chat_id = chat_id,
                            first_name = from_user.get('first_name'),
                            username = from_user.get('username'),
                            chat_type = chat.get('chat_type')
                    )
                    user_saved = await start_bot(chat_id, from_user, chat)
                    if not user_saved:
                        user_saved_warning = f"⚠️ Couldnt save the user for {chat_id}"
                        warning_text = f"⚠️ There is prblem with registreing you. Please try ;ater!"
                        await send_message(chat_id, warning_text)
                        if not user_saved_warning:
                            logging.error(f"❌Couldn't even send the waring -> save user!")
                return
                    
            logging.info(f'Collected Info: message_id: {message_id} | chat_id: {chat_id} | firstname: {first_name} | text: {safe_text}')

            # Step 1: Sending the message
            reply_message = await send_message(chat_id, f'Searching for: 🎵 {safe_text}')
            if not reply_message:
                logging.warning(f"⚠️ Couldn't send initial message for: {chat_id} | {first_name} | {text}")
                warning_text = f"⚠️ There is problem sending message. Please try again later!"
                reply_message_warning = await send_message(chat_id, warning_text)
                if not reply_message_warning:
                    logging.error(f"❌ Couldn't even send the waring -> reply message!")
                return

            # Step 2: Searching music
            founded_musics = await search_music(text)
            if not founded_musics:
                logging.warning(f"⚠️ Couldn't found music for: {chat_id} | {first_name} | {text}")
                warning_text = f"⚠️ Sorry, I couldn't find the music for {text}"
                founded_music_warning = await send_message(chat_id, warning_text)
                if not founded_music_warning:
                    logging.error(f"❌ Couldn't even send the warning -> founded music!")
                return
            
            # Step 3: Sending the choices
            choices = await send_choices(chat_id, founded_musics)
            if not choices:
                logging.warning(f"⚠️ Couldn't send choices for: {chat_id} | {first_name} | {text}")
                choices_warning = await send_message(chat_id, f"Couldn't send choices for {text}")
                if not choices_warning:
                    logging.error(f"❌ Couldn't even send the warning -> send choice!")
                return

            # Step 4: Delete the reply message(send_message)
            delete_reply_msg = await delete_message(chat_id, reply_message)
            if not delete_reply_msg:
                logging.warning(f"⚠️ Couldn't delete message: {chat_id} | {reply_message}")

        elif 'callback_query' in data:
            logging.info(' Recieved callback_query!')
            callback = data['callback_query']

            # Adding to favorite playlist
            if callback['data'].startswith('favorite:'):
                favorite_music = await add_favorite(callback)
                if not favorite_music:
                    logging.warning(f"⚠️ Couldn't add the music into favorite playlist: music_id={callback['data']}, chat_id={callback['message']['chat']['id']}")
                return
            
            # Remove from favorite playlist
            if callback['data'].startswith('unfavorite:'):
                favorite_music = await remove_favorite(callback)
                if not favorite_music:
                    logging.warning(f"⚠️ Couldn't remove the music from favorite playlist: music_id={callback['data']}, chat_id={callback['message']['chat']['id']}")
                return           
            
            # Send Music from Playlist
            if callback['data'].startswith('playlist_music:'):
                music_id = callback['data'].split(':')[1]
                chat_id = callback['message']['chat']['id']
                music = await Music.get_or_none(music_id=music_id)
                if music and os.path.exists(music.audio_file):
                    await send_music(chat_id, {
                        'music_id': music.music_id,
                        'title': music.title,
                        'duration': music.duration,
                        'youtube_url': music.youtube_url,
                        'audio_file': music.audio_file,
                        'uploader': music.uploader       
                    })
            else:
                chat_id = callback['message']['chat']['id']
                await send_message(chat_id, "⚠️ Music file not found.")

            chat_id = callback['message']['chat']['id']
            message_id = callback['message']['message_id']
            text = callback['message'].get('text', '')
            music_id = callback['data']
            logging.info(f"📥 Loaded Calback_query: {callback}")
            logging.info(f"🎵 User in chat {chat_id} chose music ID: {music_id} | Original message: '{text}'")
   
            # Step 5: Disabling the buttons(choices)
            dis_buttons = await disable_button(chat_id, message_id, text)
            if not dis_buttons:
                logging.warning(f"⚠️ Couldn't disable buttons for chat {chat_id} | message {message_id} | text: '{text}'")

            # Step 6: Deleting the choices message
            delete_dis_buttons = await delete_message(chat_id, message_id)
            if not delete_dis_buttons:
                logging.warning(f"❌ Couldn't delete choices message: chat_id={chat_id}, message_id={message_id}")
            
            # Check database before download 
            existing_music = await Music.get_or_none(music_id=music_id)
            if(
                existing_music
                and isinstance(existing_music.audio_file, str)
                and existing_music.audio_file.strip() != ""
                and os.path.exists(existing_music.audio_file)
            ):
                music_sent = await send_music(chat_id, {
                    'music_id': existing_music.music_id,
                    'title': existing_music.title,
                    'duration': existing_music.duration,
                    'youtube_url': existing_music.youtube_url,
                    'uploader': existing_music.uploader,
                    'audio_file': existing_music.audio_file
                })

            # Step 7: Download the music
            else: 
                downloaded_music = await download_music(music_id)
                if not downloaded_music:
                    logging.warning(f"⚠️ Failed to download music with ID: {music_id} for chat_id={chat_id}")
                    await send_message(chat_id, "⚠️ Sorry, I couldn't download the selected music. Please try again later!")
                    return
            
            # Save music in database
            try:
                if existing_music:
                    existing_music.audio_file = downloaded_music['audio_file']
                    existing_music.uploader = downloaded_music['uploader']
                    await existing_music.save()
                else:
                    await save_music(downloaded_music)
            except Exception as e:
                logging.exception(f"Error saving music: {e}")
                
                # Step 8: Send the music
                music_sent = await send_music(chat_id, downloaded_music)
                if not music_sent:
                    logging.warning(f"⚠️ Failed to send music with ID: {music_id} for chat_id={chat_id}")
                    warning_text = f"⚠️ Sorry, I couldn't send the selected music. Please try again later!"
                    music_sent_warning = await send_message(chat_id, warning_text)
                    if not music_sent_warning:
                        logging.error(f"❌ Couldn't even send the warning -> send music!")
                    return               

        elif 'inline_query' in data:
            inline_query = data['inline_query']
            inline_query_id, results = await handle_inline_query(inline_query)
            
            # Show Playlist
            await playlist_inline_query(inline_query_id, results)


    except Exception as e:
        logging.exception(f'There was an error: {e}')