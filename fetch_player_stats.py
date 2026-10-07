import csv
import re

from yahoo_session import yahoo_page

PLAYERS_URL = (
    "https://basketball.fantasysports.yahoo.com/nba/88338/players"
    "?status=ALL&eteam=ALL&fteam=NONE&pos=P&cut_type=33&stat1=S_PSR"
    "&myteam=0&sort=OR&sdir=1&count={count}"
)
OUTPUT_FILE = "player_stats.csv"
CSV_COLUMNS = [
    "name", "team", "position", "GP",
    "FGM", "FGA", "FG%", "FTM", "FTA", "FT%",
    "3PTM", "PTS", "REB", "AST", "ST", "BLK", "TO",
]

TD = {
    "player": 2,
    "GP": 5,
    "FGM/A": 10,
    "FG%": 11,
    "FTM/A": 12,
    "FT%": 13,
    "3PTM": 14,
    "PTS": 15,
    "REB": 16,
    "AST": 17,
    "ST": 18,
    "BLK": 19,
    "TO": 20,
}


def _clean(value: str) -> str:
    return value.strip().replace(",", "")


def _clean_team(value: str) -> str:
    return re.sub(r"[^A-Za-z]", "", value)


def _clean_position(value: str) -> str:
    return re.sub(r"[^A-Za-z,]", "", value)


def parse_row(row) -> dict | None:
    tds = row.locator("td").all()
    if len(tds) != 22:
        return None
    name = tds[TD["player"]].locator("img").get_attribute("alt")
    lines = [line.strip() for line in tds[TD["player"]].inner_text().splitlines() if line.strip()]
    team, _, position = lines[-1].partition(" - ")
    gp = _clean(tds[TD["GP"]].inner_text())
    if gp in ("-", ""):
        return None
    fgm, _, fga = _clean(tds[TD["FGM/A"]].inner_text()).partition("/")
    ftm, _, fta = _clean(tds[TD["FTM/A"]].inner_text()).partition("/")

    return {
        "name": name or lines[0].replace("Player Note", "").strip(),
        "team": _clean_team(team),
        "position": _clean_position(position),
        "GP": gp,
        "FGM": fgm,
        "FGA": fga,
        "FG%": _clean(tds[TD["FG%"]].inner_text()),
        "FTM": ftm,
        "FTA": fta,
        "FT%": _clean(tds[TD["FT%"]].inner_text()),
        "3PTM": _clean(tds[TD["3PTM"]].inner_text()),
        "PTS": _clean(tds[TD["PTS"]].inner_text()),
        "REB": _clean(tds[TD["REB"]].inner_text()),
        "AST": _clean(tds[TD["AST"]].inner_text()),
        "ST": _clean(tds[TD["ST"]].inner_text()),
        "BLK": _clean(tds[TD["BLK"]].inner_text()),
        "TO": _clean(tds[TD["TO"]].inner_text()),
    }


def main() -> None:
    total = 0
    with yahoo_page(PLAYERS_URL.format(count=0)) as page, open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for count in range(0, 501, 25):
            _goto_url = PLAYERS_URL.format(count=count)
            if count:
                page.goto(_goto_url, timeout=60_000, wait_until="domcontentloaded")
            page.wait_for_timeout(2_500)
            page.wait_for_selector("#players-table tbody tr", timeout=30_000)
            rows = page.locator("#players-table tbody tr").all()
            for row in rows:
                record = parse_row(row)
                if record:
                    writer.writerow(record)
            f.flush()
            saved = sum(1 for r in rows if parse_row(r))
            total += saved
            print(f"count={count}: {saved} players saved (cumulative {total})")
    print(f"Done. {total} players saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
