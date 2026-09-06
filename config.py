import os
from dotenv import load_dotenv

load_dotenv()

# Core
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION = os.getenv("SESSION", "maouknowsjava")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "fwmaou")

# Branding
BOT_NAME = os.getenv("BOT_NAME", "MaouKnowsJava")
BOT_IMAGE_URL = os.getenv(
    "BOT_IMAGE_URL",
    "https://i.ibb.co/zhf6ZHKg/Img2url-bot.jpg"
)

# Runtime
PRIVATE_MODE = False
DATA_FILE = os.path.join("data", "maouknowsjava.json")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Validation
missing = []
if not API_ID:
    missing.append("API_ID")
if not API_HASH:
    missing.append("API_HASH")
if not OWNER_ID:
    missing.append("OWNER_ID")

if missing:
    raise ValueError(
        f"Missing required environment variables: {', '.join(missing)}\n"
        "Copy .env.example → .env and fill in the values."
    )
