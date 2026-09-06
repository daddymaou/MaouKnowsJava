from functools import wraps
from config import OWNER_USERNAME, PRIVATE_MODE
from utils.storage import owners, sudo_users


def is_owner(user_id: int) -> bool:
    return user_id in owners


def is_sudo(user_id: int) -> bool:
    return user_id in sudo_users or is_owner(user_id)


def require_owner(func):
    """Only primary + added owners."""
    @wraps(func)
    async def wrapper(event):
        if not is_owner(event.sender_id):
            await event.reply(
                f"🚫 **Owner only**\nContact @{OWNER_USERNAME} if you need access."
            )
            return
        return await func(event)
    return wrapper


def require_sudo(func):
    """Owners + sudo users."""
    @wraps(func)
    async def wrapper(event):
        if not is_sudo(event.sender_id):
            await event.reply(
                f"🚫 **Sudo only**\nContact @{OWNER_USERNAME} for access."
            )
            return
        return await func(event)
    return wrapper


def require_private(func):
    """
    When PRIVATE_MODE is enabled, only sudo/owners can run the command.
    Others are silently ignored.
    """
    @wraps(func)
    async def wrapper(event):
        if not PRIVATE_MODE or is_sudo(event.sender_id):
            return await func(event)
        return
    return wrapper
