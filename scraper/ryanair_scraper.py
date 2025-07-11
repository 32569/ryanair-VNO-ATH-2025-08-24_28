import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from datetime import datetime

URL = "https://www.ryanair.com/gb/en"
ORIGIN = "Vilnius"
DESTINATION = "Athens"
DEPART_DATE = "2025-08-24"

async def fetch_price():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(URL, timeout=60000)

        # Laukiam kol įkels formą
        await page.wait_for_selector("input[placeholder='From']")

        # Įvedam maršrutą
        await page.fill("input[placeholder='From']", ORIGIN)
        await page.keyboard.press("Enter")
        await page.fill("input[placeholder='To']", DESTINATION)
        await page.keyboard.press("Enter")

        # Pasirinkti datą
        await page.click("input[placeholder*='Depart']")
        await page.wait_for_timeout(1000)
        await page.keyboard.type(DEPART_DATE)
        await page.keyboard.press("Enter")

        await page.click("button[type='submit']")
        await page.wait_for_load_state("networkidle", timeout=60000)

        # Paieškom kainos
        await page.wait_for_selector(".fare-card__price .price", timeout=15000)
        price = await page.inner_text(".fare-card__price .price")

        await browser.close()
        return price

def save_to_csv(price):
    today = datetime.today().strftime("%Y-%m-%d")
    data = pd.DataFrame([{
        "date_scraped": today,
        "origin": ORIGIN,
        "destination": DESTINATION,
        "departure_date": DEPART_DATE,
        "price": price
    }])
    path = "data/flights.csv"
    try:
        old = pd.read_csv(path)
        data = pd.concat([old, data], ignore_index=True)
    except FileNotFoundError:
        pass
    data.to_csv(path, index=False)

if __name__ == "__main__":
    price = asyncio.run(fetch_price())
    save_to_csv(price)
