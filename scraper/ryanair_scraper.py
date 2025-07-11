import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
import csv
import os

ROUTE = {"from": "Vilnius", "to": "Athens", "date": "2025-08-24"}
CSV_PATH = "data/flights.csv"

async def fetch_price():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.ryanair.com/gb/en")
        await page.locator('input[placeholder="From"]').fill(ROUTE["from"])
        await page.locator('input[placeholder="To"]').fill(ROUTE["to"])
        await page.keyboard.press("Enter")

        await page.locator('input[placeholder*="Depart"]').click()
        await page.locator(f'[data-id="{ROUTE["date"]}"]').click()
        await page.wait_for_timeout(4000)

        price_elem = await page.locator(".flight-header__min-price").first.text_content()
        price = price_elem.strip().replace("€", "").replace(",", ".")

        await browser.close()

        today = datetime.today().strftime("%Y-%m-%d")
        os.makedirs("data", exist_ok=True)
        file_exists = os.path.isfile(CSV_PATH)

        with open(CSV_PATH, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["date_checked", "flight_date", "from", "to", "price"])
            writer.writerow([today, ROUTE["date"], ROUTE["from"], ROUTE["to"], price])

asyncio.run(fetch_price())
