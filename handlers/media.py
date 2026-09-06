import os
import tempfile
from io import BytesIO
from urllib.parse import quote
import aiohttp
import requests
from PIL import Image
from telethon import events, types
from telethon.tl.types import DocumentAttributeFilename

from config import BOT_NAME
from utils import require_private, require_sudo


def register(client):
    @client.on(events.NewMessage(pattern=r"^[.!]tourl$"))
    @require_private
    @require_sudo
    async def to_url(event):
        if not event.is_reply:
            return await event.reply("Reply to a media message.")
        reply = await event.get_reply_message()
        if not reply.media:
            return await event.reply("No media found.")
        msg = await event.reply("⬆️ Uploading...")
        path = await reply.download_media()
        try:
            async with aiohttp.ClientSession() as session:
                with open(path, "rb") as f:
                    form = aiohttp.FormData()
                    form.add_field("reqtype", "fileupload")
                    form.add_field("fileToUpload", f)
                    async with session.post("https://catbox.moe/user/api.php", data=form) as resp:
                        if resp.status == 200:
                            url = await resp.text()
                            await msg.edit(f"✅ **URL**\n{url}")
                        else:
                            await msg.edit("Upload failed.")
        except Exception as e:
            await msg.edit(f"Error: {e}")
        finally:
            if path and os.path.exists(path):
                os.remove(path)

    @client.on(events.NewMessage(pattern=r"^[.!]sticker$"))
    @require_private
    @require_sudo
    async def make_sticker(event):
        if not event.is_reply:
            return await event.reply("Reply to an image.")
        reply = await event.get_reply_message()
        if not (reply.photo or (reply.document and reply.document.mime_type.startswith("image/"))):
            return await event.reply("Reply to a photo/image.")
        processing = await event.reply("🔄 Creating sticker...")
        try:
            data = await reply.download_media(bytes)
            with Image.open(BytesIO(data)) as img:
                if img.mode != "RGBA":
                    img = img.convert("RGBA")
                img.thumbnail((512, 512), Image.LANCZOS)
                canvas = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
                canvas.paste(img, ((512 - img.width) // 2, (512 - img.height) // 2), img)
                out = BytesIO()
                out.name = "sticker.webp"
                canvas.save(out, "WEBP")
                out.seek(0)
            await client.send_file(
                event.chat_id,
                out,
                force_document=False,
                reply_to=event.reply_to_msg_id,
            )
            await processing.delete()
        except Exception as e:
            await processing.edit(f"Failed: {e}")

    @client.on(events.NewMessage(pattern=r"^[.!]img(?:\s+(.+))?$"))
    @require_private
    @require_sudo
    async def img_search(event):
        query = event.pattern_match.group(1)
        if not query:
            return await event.reply("Usage: `.img <search term>`")
        msg = await event.reply(f"🔍 Searching `{query}`...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://api.nexoracle.com/search/pixabay-images"
                    f"?apikey=63b406007be3e32b53&q={quote(query)}"
                ) as resp:
                    data = await resp.json()
                results = data.get("result") or []
                if not results:
                    return await msg.edit("No images found.")
                image_url = results[0] if isinstance(results[0], str) else results[0].get("url", results[0])
                async with session.get(image_url) as img_resp:
                    if img_resp.status != 200:
                        return await msg.edit("Failed to download image.")
                    img_data = await img_resp.read()
                    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                        tmp.write(img_data)
                        path = tmp.name
                await client.send_file(
                    event.chat_id,
                    path,
                    caption=f"🖼️ {query}",
                    reply_to=event.id,
                )
                os.unlink(path)
                await msg.delete()
        except Exception as e:
            await msg.edit(f"Error: {e}")

    @client.on(events.NewMessage(pattern=r"^[.!]gfx(\d+)?(?:\s+(.+))?$"))
    @require_private
    @require_sudo
    async def gfx(event):
        style = event.pattern_match.group(1) or "3"
        full = event.pattern_match.group(2)
        if not full:
            return await event.reply("Usage: `.gfx3 Text1 | Text2`")
        parts = [p.strip() for p in full.split("|", 1)]
        if len(parts) < 2:
            return await event.reply("Provide two texts separated by `|`")
        text1, text2 = parts
        msg = await event.reply(f"🎨 Generating GFX{style}...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://api.nexoracle.com/image-creating/gfx{style}"
                    f"?apikey=d0634e61e8789b051e"
                    f"&text1={quote(text1)}&text2={quote(text2)}"
                ) as resp:
                    if resp.status != 200:
                        return await msg.edit("API error.")
                    data = await resp.read()
                    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                        tmp.write(data)
                        path = tmp.name
            await client.send_file(
                event.chat_id,
                path,
                caption=f"✨ GFX{style} — {text1} | {text2}",
                attributes=[DocumentAttributeFilename(f"gfx{style}.png")],
                reply_to=event.id,
            )
            os.unlink(path)
            await msg.delete()
        except Exception as e:
            await msg.edit(f"Error: {e}")
