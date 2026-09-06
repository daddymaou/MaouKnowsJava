"""
MaouKnowsJava - Professional Telethon Userbot
"""

import asyncio
import logging
from telethon import TelegramClient

from config import API_ID, API_HASH, SESSION, BOT_NAME, OWNER_ID, LOG_LEVEL
from handlers import core, admin, tools, fun, games, media

# Logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(BOT_NAME)

# Client
client = TelegramClient(SESSION, API_ID, API_HASH)


async def main():
    # Register all handlers
    core.register(client)
    admin.register(client)
    tools.register(client)
    fun.register(client)
    games.register(client)
    media.register(client)

    logger.info(f"Starting {BOT_NAME}...")
    await client.start()
    me = await client.get_me()
    logger.info(f"Logged in as {me.first_name} (@{me.username}) | ID: {me.id}")
    logger.info(f"Owner ID: {OWNER_ID}")
    logger.info("Bot is ready. Press Ctrl+C to stop.")
    await client.run_until_disconnected()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopped by user.")
