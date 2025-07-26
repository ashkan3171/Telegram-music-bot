import os
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv('db_url', 'sqlite://db.sqlite3')

TORTOISE_ORM = {
    "connections": {
        "default": os.getenv("db_url", "sqlite://db.sqlite3")
    },
    "apps": {
        "models": {
            "models": ["telegram_bot.db.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}
