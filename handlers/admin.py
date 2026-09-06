from telethon import events, functions, types, errors
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.errors import (
    InviteHashEmptyError,
    InviteHashExpiredError,
    InviteHashInvalidError,
    InviteRequestSentError,
)
import re
import os
import asyncio

from config import OWNER_ID, BOT_NAME, OWNER_USERNAME
from utils import require_private, require_owner, require_sudo
from utils.storage import owners, sudo_users, save_data


def register(client):
    @client.on(events.NewMessage(pattern=r"^[.!]addowner (\d+)$"))
    @require_private
    @require_owner
    async def add_owner(event):
        uid = int(event.pattern_match.group(1))
        owners.add(uid)
        save_data()
        await event.reply(f"👑 Added `{uid}` as owner")

    @client.on(events.NewMessage(pattern=r"^[.!]delowner (\d+)$"))
    @require_private
    @require_owner
    async def del_owner(event):
        uid = int(event.pattern_match.group(1))
        if uid == OWNER_ID:
            return await event.reply("⚠ Cannot remove the primary owner.")
        if uid in owners:
            owners.remove(uid)
            save_data()
            await event.reply(f"❌ Removed `{uid}` from owners")
        else:
            await event.reply("User is not an owner.")

    @client.on(events.NewMessage(pattern=r"^[.!]listowners$"))
    @require_private
    @require_owner
    async def list_owners(event):
        lst = "\n".join(f"• `{uid}`" for uid in sorted(owners))
        await event.reply(f"👑 **Owners**\n{lst}")

    @client.on(events.NewMessage(pattern=r"^[.!]addsudo (\d+)$"))
    @require_private
    @require_owner
    async def add_sudo(event):
        uid = int(event.pattern_match.group(1))
        sudo_users.add(uid)
        save_data()
        await event.reply(f"💎 Added `{uid}` as sudo")

    @client.on(events.NewMessage(pattern=r"^[.!]delsudo (\d+)$"))
    @require_private
    @require_owner
    async def del_sudo(event):
        uid = int(event.pattern_match.group(1))
        if uid in sudo_users:
            sudo_users.remove(uid)
            save_data()
            await event.reply(f"❌ Removed `{uid}` from sudo")
        else:
            await event.reply("User is not sudo.")

    @client.on(events.NewMessage(pattern=r"^[.!]listsudo$"))
    @require_private
    @require_owner
    async def list_sudo(event):
        if not sudo_users:
            return await event.reply("No sudo users yet.")
        lst = "\n".join(f"• `{uid}`" for uid in sorted(sudo_users))
        await event.reply(f"💎 **Sudo Users**\n{lst}")

    @client.on(events.NewMessage(pattern=r"^[.!]setbio(?: |$)(.*)"))
    @require_private
    @require_owner
    async def set_bio(event):
        new_bio = event.pattern_match.group(1).strip()
        if not new_bio:
            full = await event.client(functions.users.GetFullUserRequest("me"))
            current = full.full_user.about or "No bio set"
            return await event.reply(f"Current bio:\n{current}\n\nUsage: `.setbio <text>`")
        await event.client(functions.account.UpdateProfileRequest(about=new_bio[:70]))
        await event.reply(f"✅ Bio updated:\n{new_bio}")

    @client.on(events.NewMessage(pattern=r"^[.!]setpp$"))
    @require_private
    @require_owner
    async def set_pp(event):
        if not event.is_reply:
            return await event.reply("Reply to an image with `.setpp`")
        reply = await event.get_reply_message()
        if not reply.media:
            return await event.reply("Replied message has no media.")
        path = await reply.download_media(file="profile_pic.jpg")
        try:
            await event.client(functions.photos.UploadProfilePhotoRequest(
                file=await event.client.upload_file(path)
            ))
            await event.reply("✅ Profile picture updated.")
        finally:
            if os.path.exists(path):
                os.remove(path)

    @client.on(events.NewMessage(pattern=r"^[.!]left$"))
    @require_private
    @require_owner
    async def leave(event):
        chat = await event.get_chat()
        if not isinstance(chat, (types.Chat, types.Channel)):
            return await event.reply("This command only works in groups/channels.")
        await event.reply(f"👋 **{BOT_NAME}** is leaving...")
        await asyncio.sleep(1.5)
        await event.client.delete_dialog(event.chat_id)

    @client.on(events.NewMessage(pattern=r"^[.!]joingc(?: |$)(.*)"))
    @require_private
    @require_owner
    async def joingc(event):
        link = event.pattern_match.group(1).strip()
        if not link:
            return await event.reply("Usage: `.joingc <invite link>`")

        invite_hash = None
        if "t.me/+" in link or "t.me/joinchat/" in link:
            m = re.search(r"(?:\+|joinchat/)([A-Za-z0-9_-]+)", link)
            if m:
                invite_hash = m.group(1)
        elif "t.me/" in link:
            m = re.search(r"t\.me/([A-Za-z0-9_]+)", link)
            if m:
                try:
                    await event.client(functions.channels.JoinChannelRequest(m.group(1)))
                    return await event.reply("✅ Joined the public group/channel.")
                except Exception as e:
                    return await event.reply(f"❌ Failed: {e}")

        if not invite_hash:
            return await event.reply("Invalid invite link.")

        try:
            await event.client(ImportChatInviteRequest(invite_hash))
            await event.reply("✅ Successfully joined!")
        except InviteRequestSentError:
            await event.reply("🕒 Join request sent (waiting for approval).")
        except InviteHashExpiredError:
            await event.reply("❌ Invite link expired.")
        except InviteHashInvalidError:
            await event.reply("❌ Invalid invite link.")
        except Exception as e:
            await event.reply(f"❌ Error: {e}")
