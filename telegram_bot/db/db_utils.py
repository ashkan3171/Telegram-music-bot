from tortoise import Tortoise, run_async
from telegram_bot.db.models import User
from dotenv import load_dotenv
from pathlib import Path
import os

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

DB_URL = os.getenv('db_url')

async def init_db():
    # Here we connect to a SQLite DB file.
    # also specify the app name of "models"
    # which contain models from "app.models"
    await Tortoise.init(
        db_url=DB_URL,
        modules={'models':['telegram_bot.db.models']}
    )
    # Generate the schema
    await Tortoise.generate_schemas()

async def close_db():
    await Tortoise.close_connections()

async def show_all_users():
    
    users = await User.all().values()
    print("===== Users in Database =====")
    for user in users:
        print(user)
    print("=============================")

if __name__ == "__main__":
    import asyncio

    async def run():
        from telegram_bot.db.db_utils import init_db, close_db, show_all_users
        await init_db()
        await show_all_users()
        await close_db()

    asyncio.run(run())