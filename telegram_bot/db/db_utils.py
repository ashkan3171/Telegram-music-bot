from tortoise import Tortoise, run_async
from .config import TORTOISE_ORM

async def init_db():
    # Here we connect to a SQLite DB file.
    # also specify the app name of "models"
    # which contain models from "app.models"
    await Tortoise.init(TORTOISE_ORM)
    # Generate the schema
    await Tortoise.generate_schemas()

async def close_db():
    await Tortoise.close_connections()