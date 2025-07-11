# scraper/ryanair_scraper.py
import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from datetime import datetime

ORIGIN = "Vilnius"
DESTINATION = "Athens"
DEPART_DATE = "2025-08-24"
CSV_PATH = "data/flights.csv"

async def fetch_price():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.ryanair.com/gb/en")

        await page.fill("input[placeholder='From']", ORIGIN)
        await page.keyboard.press("Enter")
        await page.fill("input[placeholder='To']", DESTINATION)
        await page.keyboard.press("Enter")

        await page.click("input[placeholder='Depart']")
        await page.wait_for_timeout(1000)
        await page.click(f"[data-id='{DEPART_DATE}']")

        await page.click("button[data-ref='flight-search-widget__cta']")
        await page.wait_for_timeout(8000)

        price_elem = await page.query_selector("span.price__value")
        price = await price_elem.inner_text() if price_elem else "N/A"

        await browser.close()

        return {
            "date_checked": datetime.now().strftime("%Y-%m-%d"),
            "from": ORIGIN,
            "to": DESTINATION,
            "travel_date": DEPART_DATE,
            "price": price
        }

def save_to_csv(data):
    t
