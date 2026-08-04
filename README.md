# LunarisCasino forwarder

Pyrogram bot worker that re-forwards a fixed set of Telegram messages into the same
chat, waiting four hours between each message, then immediately repeats the cycle,
preserving content as-is via ``forward_messages``.

## Setup

1. Copy `.env.example` to `.env` and set `API_ID`, `API_HASH`, and `BOT_TOKEN`.
2. Add the bot to the target chat/channel as an admin with permission to post/forward.
3. Run:

```bash
uv sync
uv run python main.py
```

4. Docker:

```bash
docker build -t lunariscasino .
docker run --env-file .env lunariscasino
```

Configured messages: `t.me/c/4215169273/{5,7,8,9,10,12,13,14,15}` → chat `-1004215169273`.
