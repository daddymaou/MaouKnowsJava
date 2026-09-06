# MaouKnowsJava 

**Clean, modular, and professional Telegram Userbot** built with [Telethon](https://github.com/LonamiWebs/Telethon).

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Telethon](https://img.shields.io/badge/Telethon-1.36+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

### Features

- Fully modular handler system (easy to extend)
- Owner + Sudo permission system
- Private / Public mode
- Clean help menu
- Notes system
- Translation
- Tic-Tac-Toe game
- TTS, AI chat, QR, Screenshots
- Image search, GFX generator, Stickers
- Weather, IP lookup, URL tools
- Media upload to URL
- Proper environment-based configuration

---

### Quick Start

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/MaouKnowsJava.git
cd MaouKnowsJava

# 2. Install
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit .env with your values

# 4. Run
python main.py
```

On first run you will be asked for your phone number and login code.

---

### Configuration (`.env`)

| Variable         | Required | Description                     |
|------------------|----------|---------------------------------|
| `API_ID`         | Yes      | From my.telegram.org            |
| `API_HASH`       | Yes      | From my.telegram.org            |
| `OWNER_ID`       | Yes      | Your Telegram numeric ID        |
| `OWNER_USERNAME` | Yes      | Your @username (without @)      |
| `SESSION`        | No       | Session file name               |
| `BOT_NAME`       | No       | Display name                    |

---

### Project Structure

```
MaouKnowsJava/
├── main.py                 # Entry point
├── config.py               # Environment loader
├── handlers/
│   ├── core.py             # menu, ping, uptime, stats, mode
│   ├── admin.py            # owner/sudo management
│   ├── tools.py            # id, info, translate, notes, etc.
│   ├── fun.py              # tts, ai, about
│   ├── games.py            # tic-tac-toe
│   └── media.py            # tourl, sticker, img, gfx
├── utils/
│   ├── decorators.py
│   ├── storage.py
│   └── helpers.py
├── data/                   # runtime data (gitignored)
├── .env.example
├── requirements.txt
└── LICENSE
```

---

### Main Commands

| Command              | Description                    | Access    |
|----------------------|--------------------------------|-----------|
| `.menu` / `.help`    | Show all commands              | Everyone* |
| `.ping`              | Latency check                  | Sudo      |
| `.uptime` / `.alive` | Bot status                     | Sudo      |
| `.stats`             | Bot statistics                 | Sudo      |
| `.mode private/public` | Toggle private mode          | Owner     |
| `.id` / `.info`      | User information               | Everyone* |
| `.tr` / `.translate` | Translate text                 | Everyone* |
| `.note` / `.notes`   | Save & list notes              | Sudo      |
| `.ttt`               | Start Tic-Tac-Toe              | Sudo      |
| `.qr` `.ssweb` `.ip` | Tools                          | Sudo      |
| `.tts` `.ai`         | Fun features                   | Sudo      |
| `.tourl` `.sticker`  | Media tools                    | Sudo      |

\* When Private Mode is enabled, only Owner + Sudo can use commands.

---

### Adding New Commands

1. Create a new file in `handlers/` or add to an existing one.
2. Define a `register(client)` function.
3. Import and call it from `main.py`.

Example: 

```python
# handlers/example.py
from telethon import events
from utils import require_private, require_sudo

def register(client):
    @client.on(events.NewMessage(pattern=r"^[.!]hello$"))
    @require_private
    @require_sudo
    async def hello(event):
        await event.reply("Hello from MaouKnowsJava!")
```

---

### Security Notes

- Never commit your `.env` or `.session` files.
- Keep your API credentials private.
- Review third-party API usage before deploying publicly.
- The project does **not** include dangerous eval/exec commands.

---

### Contributing

Pull requests are welcome and encouraged.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

---

### License

MIT © 2026 [ᗰᗩOᑌ.](https://github.com/daddymaou)

---

**MaouKnowsJava** — Code. Automate. Iterate.