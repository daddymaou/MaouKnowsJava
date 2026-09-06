import json
import os
from config import DATA_FILE, OWNER_ID

os.makedirs(os.path.dirname(DATA_FILE) or ".", exist_ok=True)


def load_data() -> dict:
    if not os.path.exists(DATA_FILE):
        default = {
            "owners": [OWNER_ID],
            "sudo": [],
            "quotes": [
                "The only way to do great work is to love what you do.",
                "Code is like humor. When you have to explain it, it’s bad.",
                "First, solve the problem. Then, write the code.",
            ],
            "notes": {},
        }
        save_data(default)
        return default

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Ensure keys exist
    data.setdefault("owners", [OWNER_ID])
    data.setdefault("sudo", [])
    data.setdefault("quotes", [])
    data.setdefault("notes", {})
    return data


def save_data(data: dict | None = None):
    if data is None:
        data = {
            "owners": list(owners),
            "sudo": list(sudo_users),
            "quotes": quotes,
            "notes": notes,
        }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


_data = load_data()
owners: set[int] = set(_data.get("owners", [OWNER_ID]))
sudo_users: set[int] = set(_data.get("sudo", []))
quotes: list[str] = _data.get("quotes", [])
notes: dict = _data.get("notes", {})
