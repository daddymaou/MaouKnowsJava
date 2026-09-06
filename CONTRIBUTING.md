# Contributing to MaouKnowsJava

Thanks for your interest in contributing!

## How to Contribute

1. **Fork** the repository
2. Create a new branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test that the bot still starts and your command works
5. Commit with a clear message
6. Push and open a **Pull Request**

## Guidelines

- Keep the modular structure (put new commands in the appropriate `handlers/` file or create a new one)
- Use the existing decorators (`@require_owner`, `@require_sudo`, `@require_private`)
- Prefer clear error messages for users
- Do not hardcode secrets
- Follow existing code style as much as possible

## Adding a New Command

```python
# handlers/your_module.py
from telethon import events
from utils import require_private, require_sudo

def register(client):
    @client.on(events.NewMessage(pattern=r"^[.!]yourcommand$"))
    @require_private
    @require_sudo
    async def your_command(event):
        await event.reply("It works!")
```

Then import and call `your_module.register(client)` in `main.py`.

## Questions?

Open an issue or contact the maintainer.
