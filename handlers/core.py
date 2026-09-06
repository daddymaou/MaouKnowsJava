from datetime import datetime
from telethon import events
from telethon.utils import get_display_name

from config import BOT_NAME, BOT_IMAGE_URL, OWNER_USERNAME, PRIVATE_MODE
from utils import require_private, require_sudo, require_owner, format_uptime
from utils.storage import quotes, save_data
import random

START_TIME = datetime.now()


def register(client):
    @client.on(events.NewMessage(pattern=r"^[.!](?:menu|help)$"))
    @require_private
    async def menu(event):
        text = f"""
**⚡ {BOT_NAME}**

**Core**
`.ping` `.uptime` `.alive` `.stats`
`.mode public|private`
`.help` / `.menu`

**Admin**
`.addowner` `.delowner` `.listowners`
`.addsudo` `.delsudo` `.listsudo`
`.setbio` `.setpp` `.left` `.joingc`

**Tools**
`.id` `.info` `.chatinfo`
`.translate` `.tr`
`.qr` `.ssweb` `.short`
`.ip` `.weather`
`.note` `.notes` `.delnote`

**Fun & Media**
`.quote` `.addquote`
`.play` `.tts` `.ai`
`.img` `.gfx` `.sticker`
`.tourl`

**Games**
`.ttt` `.jointtt` `.move` `.quitttt`

Owner: @{OWNER_USERNAME}
"""
        await client.send_file(
            event.chat_id,
            file=BOT_IMAGE_URL,
            caption=text.strip(),
            reply_to=event.id,
            parse_mode="md",
        )

    @client.on(events.NewMessage(pattern=r"^[.!]ping$"))
    @require_private
    @require_sudo
    async def ping(event):
        start = datetime.now()
        msg = await event.reply("🏓 Pinging...")
        latency = (datetime.now() - start).total_seconds() * 1000
        await msg.edit(f"🏓 **Pong!** `{latency:.2f}ms`")

    @client.on(events.NewMessage(pattern=r"^[.!]uptime$"))
    @require_private
    @require_sudo
    async def uptime(event):
        d, h, m, s = format_uptime(START_TIME)
        await event.reply(
            f"⏱️ **{BOT_NAME} Uptime**\n"
            f"`{d}` days  `{h}` hours  `{m}` min  `{s}` sec"
        )

    @client.on(events.NewMessage(pattern=r"^[.!]alive$"))
    @require_private
    async def alive(event):
        d, h, m, s = format_uptime(START_TIME)
        text = (
            f"**⚡ {BOT_NAME} is alive**\n\n"
            f"• Status: `Online`\n"
            f"• Uptime: `{d}d {h}h {m}m`\n"
            f"• Mode: `{'Private' if PRIVATE_MODE else 'Public'}`\n"
            f"• Owner: @{OWNER_USERNAME}"
        )
        await event.reply(text)

    @client.on(events.NewMessage(pattern=r"^[.!]stats$"))
    @require_private
    @require_sudo
    async def stats(event):
        from utils.storage import owners, sudo_users, notes
        d, h, m, s = format_uptime(START_TIME)
        text = (
            f"**📊 {BOT_NAME} Stats**\n\n"
            f"• Uptime: `{d}d {h}h {m}m`\n"
            f"• Owners: `{len(owners)}`\n"
            f"• Sudo users: `{len(sudo_users)}`\n"
            f"• Quotes: `{len(quotes)}`\n"
            f"• Notes: `{len(notes)}`\n"
            f"• Mode: `{'🔒 Private' if PRIVATE_MODE else '🔓 Public'}`"
        )
        await event.reply(text)

    @client.on(events.NewMessage(pattern=r"^[.!]mode (private|public)$"))
    @require_private
    @require_owner
    async def set_mode(event):
        global PRIVATE_MODE
        from config import PRIVATE_MODE as cfg_mode
        mode = event.pattern_match.group(1).lower()
        # We mutate the imported name carefully
        import config
        config.PRIVATE_MODE = (mode == "private")
        status = "🔒 **Private** (silent to non-admins)" if config.PRIVATE_MODE else "🔓 **Public**"
        await event.reply(f"⚙️ Mode updated → {status}")

    @client.on(events.NewMessage(pattern=r"^[.!]quote$"))
    @require_private
    async def random_quote(event):
        if quotes:
            await event.reply(f"📜 {random.choice(quotes)}")
        else:
            await event.reply("No quotes yet. Add one with `.addquote <text>`")

    @client.on(events.NewMessage(pattern=r"^[.!]addquote (.+)$"))
    @require_private
    @require_owner
    async def add_quote(event):
        q = event.pattern_match.group(1).strip()
        quotes.append(q)
        save_data()
        await event.reply(f"✅ Quote added:\n_{q}_")
