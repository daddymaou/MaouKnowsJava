from telethon import events
from telethon.tl.types import DocumentAttributeAudio
from io import BytesIO
from urllib.parse import quote
import random
import requests

from config import BOT_NAME, OWNER_USERNAME
from utils import require_private, require_sudo

try:
    from gtts import gTTS
except ImportError:
    gTTS = None


def register(client):
    @client.on(events.NewMessage(pattern=r"^[.!]tts(?: |$)([\s\S]*)"))
    @require_private
    async def tts(event):
        if gTTS is None:
            return await event.reply("gTTS is not installed.")
        args = event.pattern_match.group(1).strip()
        lang = "en"
        text = args
        if args:
            parts = args.split(maxsplit=1)
            if parts[0].lower() in {"en", "es", "fr", "de", "ja", "ru", "pt", "id", "ar"}:
                lang = parts[0].lower()
                text = parts[1] if len(parts) > 1 else ""
        if not text and event.is_reply:
            reply = await event.get_reply_message()
            text = reply.raw_text or ""
        if not text:
            return await event.reply(
                "Usage:\n`.tts Hello world`\n`.tts es Hola mundo`\nOr reply to a message."
            )
        text = text[:300]
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            buf = BytesIO()
            tts.write_to_fp(buf)
            buf.seek(0)
            await client.send_file(
                event.chat_id,
                buf,
                voice_note=True,
                attributes=[DocumentAttributeAudio(duration=0, voice=True, title=f"TTS ({lang})")],
                caption=f"🔊 {text[:40]}...",
                reply_to=event.id,
            )
        except Exception as e:
            await event.reply(f"❌ TTS error: {e}")

    @client.on(events.NewMessage(pattern=r"^[.!]ai(?: |$)(.*)"))
    @require_private
    @require_sudo
    async def ai_chat(event):
        query = event.pattern_match.group(1).strip()
        if not query:
            return await event.reply("Usage: `.ai <question>`")
        prompt = (
            f"You are {BOT_NAME}, a sharp and helpful assistant created by @{OWNER_USERNAME}. "
            f"Be concise and useful. Query: {query}"
        )
        try:
            url = f"https://apis.davidcyriltech.my.id/ai/chatbot?query={quote(prompt)}"
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                data = r.json()
                answer = data.get("result", "No response.")
                await event.reply(f"**⚡ {BOT_NAME}**\n\n{answer}")
            else:
                await event.reply("AI service is currently unavailable.")
        except Exception:
            await event.reply("Failed to reach AI service.")

    @client.on(events.NewMessage(pattern=r"^[.!](?:owner|about)$"))
    @require_private
    async def about(event):
        text = f"""
**⚡ {BOT_NAME}**

Clean & modular Telegram userbot.

• Owner: @{OWNER_USERNAME}
• Open source
• Built for speed and clarity

Use `.menu` or `.help` to see commands.
"""
        await event.reply(text.strip())

@client.on(events.NewMessage(pattern=r"^[.!](?:coinflip|flip)$"))
@require_private
async def coinflip(event):
    result = random.choice(["Heads", "Tails"])
    await event.reply(f"🪙 **Coin Flip**\nResult: `{result}`")


@client.on(events.NewMessage(pattern=r"^[.!](?:dice|roll)(?: (\d+))?$"))
@require_private
async def dice(event):
    sides = event.pattern_match.group(1)
    sides = int(sides) if sides and sides.isdigit() else 6
    if sides < 2 or sides > 100:
        return await event.reply("Please choose between 2 and 100 sides.")
    result = random.randint(1, sides)
    await event.reply(f"🎲 You rolled a **{result}** (1–{sides})")