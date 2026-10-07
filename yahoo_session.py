import os
import time
from contextlib import contextmanager
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import Page, sync_playwright

load_dotenv()

BASE_URL = "https://basketball.fantasysports.yahoo.com/"
LOGIN_URL = (
    "https://login.yahoo.com/?.lang=en-US&src=sports"
    "&.done=https%3A%2F%2Fbasketball.fantasysports.yahoo.com%2F"
)
SESSION_FILE = Path(__file__).parent / "yahoo_session.json"


def _signed_in(page: Page) -> bool:
    return page.locator('a[href*="activity=ybar-signin"]').count() == 0


def _goto(page: Page, url: str, settle_ms: int = 2000) -> None:
    page.goto(url, timeout=60_000, wait_until="domcontentloaded")
    page.wait_for_timeout(settle_ms)


def _interactive_login(page: Page) -> None:
    _goto(page, LOGIN_URL)
    page.fill('input[name="username"]', os.environ["YAHOO_USERNAME"])
    page.click('button[name="signin"]')
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2_000)
    page.fill('input[name="password"]', os.environ["YAHOO_PASSWORD"])
    page.click('button[name="validate"]')
    print("Credentials submitted - complete any verification in the browser window...")

    deadline = time.time() + 240
    while time.time() < deadline:
        try:
            if "login.yahoo.com" not in page.url and _signed_in(page):
                page.context.storage_state(path=str(SESSION_FILE))
                print(f"Session saved to {SESSION_FILE}")
                return
        except Exception:
            raise RuntimeError("Browser window closed before login completed")
        page.wait_for_timeout(2_000)
    raise RuntimeError("Login did not complete within 240s")


@contextmanager
def yahoo_page(url: str = BASE_URL, settle_ms: int = 2000):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = None
        try:
            if SESSION_FILE.exists():
                context = browser.new_context(storage_state=str(SESSION_FILE))
                page = context.new_page()
                _goto(page, url, settle_ms)
                if not _signed_in(page):
                    print("Saved session is no longer valid - logging in again...")
                    context.close()
                    page = None
                    browser.close()
                    browser = p.chromium.launch(headless=False)
            else:
                browser.close()
                browser = p.chromium.launch(headless=False)
            if page is None:
                context = browser.new_context()
                page = context.new_page()
                _interactive_login(page)
                _goto(page, url, settle_ms)
            yield page
        finally:
            browser.close()
