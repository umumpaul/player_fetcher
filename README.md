# player_fetcher

Fetch NBA player season statistics from Yahoo Fantasy Basketball using [Playwright](https://playwright.dev/python/), with persistent browser sessions so Yahoo login is only required once.

## Setup

```bash
uv sync                          # creates .venv from uv.lock
uv run playwright install chromium
cp .env.example .env             # then fill in your Yahoo credentials
```

Note: `cdn.playwright.dev` is blocked on some networks; see `playwright install` docs for offline/mirror options if the browser download fails.

## Usage

```bash
uv run python fetch_players.py             # load Yahoo Fantasy Basketball home page
uv run python fetch_player_stats.py        # fetch all player stats into player_stats.csv
```

### Session handling

- First run opens a visible browser window and pre-fills credentials from `.env`; complete any verification prompt Yahoo shows.
- The authenticated session is saved to `yahoo_session.json` and reused headlessly afterwards.
- If the saved session expires, the interactive login flow runs again automatically.

### Output

`player_stats.csv` contains one row per player with stats (GP, FG, FT, 3PT, PTS, REB, AST, ST, BLK, TO), in Yahoo's original sort order. Players with no recorded stats are skipped. Both `yahoo_session.json` and `player_stats.csv` are gitignored.

## Files

| File | Purpose |
| --- | --- |
| `yahoo_session.py` | Shared authenticated browser session logic |
| `fetch_players.py` | Quick page-fetch smoke test |
| `fetch_player_stats.py` | Paginated player stats scraper (CSV output) |
