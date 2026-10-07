import sys

from yahoo_session import BASE_URL, yahoo_page


def fetch_players(url: str = BASE_URL) -> str:
    with yahoo_page(url) as page:
        body = page.inner_text("body")
        print(f"URL: {page.url}\nTitle: {page.title()}\n{body}")
        return body


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else BASE_URL
    fetch_players(target)
