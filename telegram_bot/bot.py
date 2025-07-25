import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN_BOT')

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN_BOT is missing in .env file.")