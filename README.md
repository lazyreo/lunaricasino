# LunarisCasino forwarder

Bot worker that copies a fixed set of Telegram messages into the same chat without
a forward tag. Timing and the next message ID are tracked in MongoDB via Motor
(`FindMongo`), so restarts resume the correct message at the correct time.

## Setup

1. Copy `.env.example` to `.env` and set `API_ID`, `API_HASH`, `BOT_TOKEN`, and `MONGO_URI`.
2. Add the bot to the target chat/channel as an admin with permission to post.
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

Mongo document (`forward_schedule`) stores `next_message_id`, `next_index`, and `next_at`.
On first boot the bot skips copying and schedules the first message after `DELAY_HOURS`
(default 4). After each successful copy, the schedule advances by another `DELAY_HOURS`.

Configured messages: `t.me/c/4215169273/{5,7,8,9,10,12,13,14,15}` → chat `-1004215169273`.
