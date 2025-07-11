import asyncio, os, csv, pandas as pd
from datetime import datetime
from playwright.async_api import async_playwright

ORIGIN = "Vilnius"    # iš miesto (textbox pavadinime)
DEST   = "Athens"     # į miestą
DEP_DATE  = "2025-08-24"
RET_DATE  = "2025-08-28"
CSV_PATH = "data/flights.csv"

async def fetch_price():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(locale="en-GB")
        await page.goto("https://www.ryanair.com/gb/en")
        # įvedam miestus
        await page.fill("input[placeholder='From']", ORIGIN)
        await page.keyboard.press("Enter")
        await page.fill("input[placeholder='To']", DEST)
        await page.keyboard.press("Enter")
        # Datos
        await page.click("input[placeholder='Depart']")
        await page.fill("input[placeholder='Depart']", DEP_DATE)
        await page.fill("input[placeholder='Return']", RET_DATE)
        # Paieška
        await page.click("button:has-text('Search')")
        await page.wait_for_selector(".fare-card__fare-price", timeout=15000)
        price_text = await page.inner_text(".fare-card__fare-price")
        await browser.close()
        return float(price_text.replace("€", "").strip())

def append_csv(price):
    os.makedirs("data", exist_ok=True)
    file_exists = os.path.isfile(CSV_PATH)
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(
                ["date_checked", "origin", "destination", "depart", "return", "price_eur"]
            )
        writer.writerow(
            [datetime.utcnow().strftime("%Y-%m-%d"), ORIGIN, DEST, DEP_DATE, RET_DATE, price]
        )

if __name__ == "__main__":
    price_val = asyncio.run(fetch_price())
    append_csv(price_val)
    print(f"Saved price €{price_val}")
