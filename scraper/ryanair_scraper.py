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

        print("🔗 Opening Ryanair...")
        await page.goto("https://www.ryanair.com/gb/en")

        # ❗ Wait until the input fields appear
        await page.wait_for_selector('input[placeholder="From"]', timeout=15000)
        await page.fill('input[placeholder="From"]', ROUTE["from"])
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(1000)  # small wait

        await page.fill('input[placeholder="To"]', ROUTE["to"])
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(1000)

        # Click date input and select date
        await page.click('input[placeholder*="Depart"]')
        await page.wait_for_timeout(1000)
        await page.click(f'[data-id="{ROUTE["date"]}"]')
        await page.wait_for_timeout(4000)  # wait for price to load

        # Extract price
        try:
            price_elem = await page.locator(".flight-header__min-price").first.text_content()
            price = price_elem.strip().replace("€", "").replace(",", ".")
        except:
            price = "Not found"

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
