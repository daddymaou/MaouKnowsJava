import aiohttp
import requests
from urllib.parse import quote
from telethon import events, types
from telethon.utils import get_display_name
from telethon.tl.types import MessageEntityMention

from config import BOT_NAME
from utils import require_private, require_sudo, get_target_user_id
from utils.storage import notes, save_data

try:
    from deep_translator import GoogleTranslator
except ImportError:
    GoogleTranslator = None


def register(client):
    @client.on(events.NewMessage(pattern=r"^[.!](?:id|myid)$"))
    @require_private
    async def my_id(event):
        user = await event.get_sender()
        uname = f"@{user.username}" if user.username else "None"
        await event.reply(
            f"**👤 Your Info**\n"
            f"• Name: `{user.first_name}`\n"
            f"• ID: `{user.id}`\n"
            f"• Username: {uname}"
        )

    @client.on(events.NewMessage(pattern=r"^[.!]info(?: |$)(.*)"))
    @require_private
    async def user_info(event):
        target = None
        if event.is_reply:
            reply = await event.get_reply_message()
            target = await reply.get_sender()
        else:
            arg = event.pattern_match.group(1).strip()
            if arg:
                try:
                    target = await event.client.get_entity(arg)
                except Exception:
                    return await event.reply("Could not find that user.")
            else:
                target = await event.get_sender()

        uname = f"@{target.username}" if getattr(target, "username", None) else "None"
        name = get_display_name(target)
        await event.reply(
            f"**👤 User Info**\n"
            f"• Name: `{name}`\n"
            f"• ID: `{target.id}`\n"
            f"• Username: {uname}"
        )

    @client.on(events.NewMessage(pattern=r"^[.!]chatinfo$"))
    @require_private
    @require_sudo
    async def chat_info(event):
        chat = await event.get_chat()
        title = getattr(chat, "title", "Private Chat")
        members = getattr(chat, "participants_count", "N/A")
        chat_type = "Private"
        if getattr(chat, "megagroup", False):
            chat_type = "Supergroup"
        elif getattr(chat, "broadcast", False):
            chat_type = "Channel"
        elif getattr(chat, "gigagroup", False):
            chat_type = "Broadcast Group"

        await event.reply(
            f"**📋 Chat Info**\n"
            f"• Title: `{title}`\n"
            f"• ID: `{event.chat_id}`\n"
            f"• Type: `{chat_type}`\n"
            f"• Members: `{members}`"
        )

    @client.on(events.NewMessage(pattern=r"^[.!](?:tr|translate)(?: |$)(.*)"))
    @require_private
    async def translate(event):
        if GoogleTranslator is None:
            return await event.reply("Translation module not installed.")

        text = event.pattern_match.group(1).strip()
        if not text and event.is_reply:
            reply = await event.get_reply_message()
            text = reply.raw_text or ""

        if not text:
            return await event.reply(
                "Usage:\n`.tr <text>`\n`.tr es <text>` (to Spanish)\nOr reply to a message."
            )

        # Detect target language
        parts = text.split(maxsplit=1)
        dest = "en"
        if len(parts) > 1 and len(parts[0]) == 2 and parts[0].isalpha():
            dest = parts[0].lower()
            text = parts[1]

        try:
            result = GoogleTranslator(source="auto", target=dest).translate(text[:500])
            await event.reply(f"**🌐 Translated** → `{dest}`\n\n{result}")
        except Exception as e:
            await event.reply(f"❌ Translation failed: {e}")

    @client.on(events.NewMessage(pattern=r"^[.!]qr(?: |$)(.*)"))
    @require_private
    @require_sudo
    async def qr_code(event):
        text = event.pattern_match.group(1).strip()
        if not text and event.is_reply:
            reply = await event.get_reply_message()
            text = reply.raw_text or ""
        if not text:
            return await event.reply("Usage: `.qr <text or url>`")
        url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={quote(text)}"
        await client.send_file(
            event.chat_id,
            file=url,
            caption=f"🔲 **{BOT_NAME}** QR Code",
            reply_to=event.id,
        )

    @client.on(events.NewMessage(pattern=r"^[.!]ssweb(?: |$)(.*)"))
    @require_private
    @require_sudo
    async def screenshot(event):
        url = event.pattern_match.group(1).strip()
        if not url:
            return await event.reply("Usage: `.ssweb <url>`")
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        api = f"https://image.thum.io/get/fullpage/{url}"
        await client.send_file(
            event.chat_id,
            file=api,
            caption=f"📸 **{BOT_NAME}** Screenshot",
            reply_to=event.id,
        )

    @client.on(events.NewMessage(pattern=r"^[.!]short(?: |$)(.*)"))
    @require_private
    @require_sudo
    async def short_url(event):
        url = event.pattern_match.group(1).strip()
        if not url:
            return await event.reply("Usage: `.short <url>`")
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        try:
            r = requests.get(f"https://tinyurl.com/api-create.php?url={url}", timeout=10)
            await event.reply(f"🔗 Shortened:\n{r.text}")
        except Exception:
            await event.reply("❌ Failed to shorten URL.")

    @client.on(events.NewMessage(pattern=r"^[.!]ip(?:\s+(\S+))?$"))
    @require_private
    async def ip_lookup(event):
        ip = event.pattern_match.group(1)
        if not ip:
            return await event.reply("Usage: `.ip <address>`")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://ipwho.is/{ip}") as resp:
                    data = await resp.json()
            if data.get("success"):
                await event.reply(
                    f"**🔍 IP Lookup**\n"
                    f"• IP: `{data['ip']}`\n"
                    f"• Location: `{data.get('city', '?')}, {data.get('country', '?')}`\n"
                    f"• ISP: `{data.get('connection', {}).get('isp', '?')}`\n"
                    f"• Coords: `{data.get('latitude')}, {data.get('longitude')}`"
                )
            else:
                await event.reply(f"❌ {data.get('message', 'Lookup failed')}")
        except Exception as e:
            await event.reply(f"❌ Error: {e}")

    @client.on(events.NewMessage(pattern=r"^[.!]weather(?: |$)(.*)"))
    @require_private
    @require_sudo
    async def weather(event):
        city = event.pattern_match.group(1).strip()
        if not city:
            return await event.reply("Usage: `.weather <city>`")
        try:
            url = f"https://apis.davidcyriltech.my.id/weather?city={quote(city)}"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                d = r.json()
                await event.reply(
                    f"**🌤️ Weather — {city}**\n"
                    f"• Temp: `{d.get('temp', 'N/A')}°C`\n"
                    f"• Humidity: `{d.get('humidity', 'N/A')}%`\n"
                    f"• Wind: `{d.get('wind', 'N/A')} km/h`\n"
                    f"• Condition: `{d.get('condition', 'N/A')}`"
                )
            else:
                await event.reply("Could not fetch weather.")
        except Exception:
            await event.reply("Weather service unavailable.")

    # Simple notes system
    @client.on(events.NewMessage(pattern=r"^[.!]note(?: |$)(.*)"))
    @require_private
    @require_sudo
    async def save_note(event):
        arg = event.pattern_match.group(1).strip()
        if not arg:
            return await event.reply("Usage: `.note <name> <content>`")
        parts = arg.split(maxsplit=1)
        if len(parts) < 2:
            return await event.reply("Usage: `.note <name> <content>`")
        name, content = parts[0].lower(), parts[1]
        notes[name] = content
        save_data()
        await event.reply(f"✅ Note `{name}` saved.")

    @client.on(events.NewMessage(pattern=r"^[.!]notes$"))
    @require_private
    @require_sudo
    async def list_notes(event):
        if not notes:
            return await event.reply("No notes saved.")
        lst = "\n".join(f"• `{k}`" for k in notes.keys())
        await event.reply(f"**📝 Notes**\n{lst}\n\nUse `.getnote <name>` to read.")

    @client.on(events.NewMessage(pattern=r"^[.!]getnote(?: |$)(.*)"))
    @require_private
    @require_sudo
    async def get_note(event):
        name = event.pattern_match.group(1).strip().lower()
        if not name or name not in notes:
            return await event.reply("Note not found. Use `.notes` to list.")
        await event.reply(f"**📝 {name}**\n\n{notes[name]}")

    @client.on(events.NewMessage(pattern=r"^[.!]delnote(?: |$)(.*)"))
    @require_private
    @require_sudo
    async def del_note(event):
        name = event.pattern_match.group(1).strip().lower()
        if name in notes:
            del notes[name]
            save_data()
            await event.reply(f"🗑 Note `{name}` deleted.")
        else:
            await event.reply("Note not found.")
