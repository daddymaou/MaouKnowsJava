from telethon import events
from telethon.utils import get_display_name

from config import OWNER_ID
from utils import require_private, require_sudo


class TicTacToe:
    def __init__(self):
        self.game = None

    def board_str(self):
        b = self.game["board"]
        return (
            "   A   B   C\n"
            f"1  {b[0][0]} | {b[0][1]} | {b[0][2]}\n"
            "  -----------\n"
            f"2  {b[1][0]} | {b[1][1]} | {b[1][2]}\n"
            "  -----------\n"
            f"3  {b[2][0]} | {b[2][1]} | {b[2][2]}"
        )

    def winner(self):
        b = self.game["board"]
        lines = b + list(zip(*b)) + [
            [b[0][0], b[1][1], b[2][2]],
            [b[0][2], b[1][1], b[2][0]],
        ]
        for line in lines:
            if line[0] != "⬜" and line[0] == line[1] == line[2]:
                return line[0]
        return None


ttt = TicTacToe()


def register(client):
    @client.on(events.NewMessage(pattern=r"^[.!]ttt$"))
    @require_private
    @require_sudo
    async def start(event):
        if ttt.game:
            return await event.reply("A game is already running.")
        sender = await event.get_sender()
        ttt.game = {
            "board": [["⬜"] * 3 for _ in range(3)],
            "players": {
                "❌": {
                    "id": event.sender_id,
                    "mention": f"[{get_display_name(sender)}](tg://user?id={event.sender_id})",
                },
                "⭕": None,
            },
            "turn": "❌",
            "moves": 0,
        }
        await event.reply(
            f"🎲 {ttt.game['players']['❌']['mention']} started **Tic-Tac-Toe**!\n"
            "Type `.jointtt` to join.\n\n"
            f"```\n{ttt.board_str()}\n```"
        )

    @client.on(events.NewMessage(pattern=r"^[.!]jointtt$"))
    async def join(event):
        if not ttt.game:
            return await event.reply("No active game.")
        if ttt.game["players"]["⭕"]:
            return await event.reply("Game is already full.")
        if event.sender_id == ttt.game["players"]["❌"]["id"]:
            return await event.reply("You can't play against yourself.")
        sender = await event.get_sender()
        ttt.game["players"]["⭕"] = {
            "id": event.sender_id,
            "mention": f"[{get_display_name(sender)}](tg://user?id={event.sender_id})",
        }
        await event.reply(
            f"⭕ {ttt.game['players']['⭕']['mention']} joined!\n"
            f"{ttt.game['players']['❌']['mention']}'s turn (❌)\n\n"
            f"```\n{ttt.board_str()}\n```\n"
            "Move with `.move A1`"
        )

    @client.on(events.NewMessage(pattern=r"^[.!]move ([A-Ca-c][1-3])$"))
    @require_private
    async def move(event):
        if not ttt.game:
            return await event.reply("No active game.")
        symbol = None
        for s, p in ttt.game["players"].items():
            if p and p["id"] == event.sender_id:
                symbol = s
                break
        if not symbol:
            return await event.reply("You're not in this game.")
        if symbol != ttt.game["turn"]:
            return await event.reply("Not your turn.")

        mv = event.pattern_match.group(1).upper()
        col = ord(mv[0]) - ord("A")
        row = int(mv[1]) - 1
        if ttt.game["board"][row][col] != "⬜":
            return await event.reply("That cell is taken.")

        ttt.game["board"][row][col] = symbol
        ttt.game["moves"] += 1

        if w := ttt.winner():
            await event.reply(
                f"🏆 {ttt.game['players'][w]['mention']} wins!\n\n"
                f"```\n{ttt.board_str()}\n```"
            )
            ttt.game = None
            return

        if ttt.game["moves"] >= 9:
            await event.reply(f"🤝 Draw!\n\n```\n{ttt.board_str()}\n```")
            ttt.game = None
            return

        ttt.game["turn"] = "⭕" if symbol == "❌" else "❌"
        nxt = ttt.game["players"][ttt.game["turn"]]["mention"]
        await event.reply(
            f"🎲 {nxt}'s turn ({ttt.game['turn']})\n\n"
            f"```\n{ttt.board_str()}\n```"
        )

    @client.on(events.NewMessage(pattern=r"^[.!]quitttt$"))
    @require_private
    async def quit_game(event):
        if not ttt.game:
            return await event.reply("No active game.")
        host = ttt.game["players"]["❌"]["id"]
        if event.sender_id not in (host, OWNER_ID):
            return await event.reply("Only the host or owner can quit.")
        await event.reply(f"🏳️ Game ended.\n\n```\n{ttt.board_str()}\n```")
        ttt.game = None
