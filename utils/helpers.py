from datetime import datetime, timedelta
from telethon.utils import get_display_name


async def get_target_user_id(event):
    """Get user ID from reply, mention, or argument."""
    args = event.raw_text.split(maxsplit=1)
    if len(args) > 1:
        try:
            entity = await event.client.get_entity(args[1].strip())
            return entity.id
        except Exception:
            pass
    if event.is_reply:
        reply = await event.get_reply_message()
        return reply.sender_id
    return None


def format_uptime(start_time: datetime) -> tuple[int, int, int, int]:
    delta = datetime.now() - start_time
    days = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return days, hours, minutes, seconds


def humanize_seconds(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    minutes, sec = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m {sec}s"
    hours, minutes = divmod(minutes, 60)
    if hours < 24:
        return f"{hours}h {minutes}m"
    days, hours = divmod(hours, 24)
    return f"{days}d {hours}h"
