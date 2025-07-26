from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "musics" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "music_id" VARCHAR(100) NOT NULL UNIQUE,
    "title" VARCHAR(255) NOT NULL,
    "duration" INT NOT NULL,
    "youtube_url" VARCHAR(255) NOT NULL,
    "uploader" VARCHAR(255),
    "audio_file" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "search_logs" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "query" VARCHAR(255) NOT NULL,
    "results" JSON NOT NULL,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "users" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "user_id" INT NOT NULL UNIQUE,
    "chat_id" INT NOT NULL UNIQUE,
    "first_name" VARCHAR(50),
    "username" VARCHAR(255),
    "chat_type" VARCHAR(20),
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "playlist" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "added_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "music_id" INT NOT NULL REFERENCES "musics" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_playlist_user_id_741359" UNIQUE ("user_id", "music_id")
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
