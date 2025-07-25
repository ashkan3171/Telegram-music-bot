import logging
from telegram_bot.utils.telegram_api import send_message

async def start_bot(chat_id, from_user, chat):
    try:
        user_id = from_user['id']
        username = from_user.get('username', '')
        first_name = from_user.get('first_name','')
        chat_type = chat.get('type', '')

        # Loggin the user 📌
        logging.info(f"🧾 New user started the bot:")
        logging.info(f"    user_id: {user_id}")
        logging.info(f"    username: {username}")
        logging.info(f"    first_name: {first_name}")
        logging.info(f"    chat_type: {chat_type}")
        logging.info(f"    chat_id: {chat_id}")

        welcome_tex = (
            f"🎶 Hello {first_name or 'there'}!\n\n"
            "🎵 Welcome to Music4Life Bot!\n"
            "You can search for any song by sending the name of the artist or track.\n"
            "✅ For example: shape of my heart sting.\n"
            "Let’s get started! 🔍"
        )
        await send_message(chat_id, welcome_tex)
        return True
    except Exception as e:
        logging.exception(f'There was an problem with start command in chat_id={chat_id}: {e}')
        return False