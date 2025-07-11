import asyncio
from datetime import datetime
from pathlib import Path
import csv
from playwright.async_api import async_playwright

# Nuostatos
ORIGIN = "Vilnius"
DESTINATION = "Athens"
DEPARTURE_DATE = "2025-08-24"
CSV_FILE = Path("data/flights.csv")

async def fetch_price():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto("https://www.ryanair.com/gb/en")
            await page.wait_for_selector('input[placeholder="From"]', timeout=15000)

            # Įvedam skrydžio kryptį
            await page.fill('input[placeholder="From"]', ORIGIN)
            await page.keyboard.press("Enter")
            await page.fill('input[placeholder="To"]', DESTINATION)
            await page.keyboard.press("Enter")

            # Pasirenkam datą
            await page.click('input[placeholder="Departure"]')
            await page.keyboard.type(DEPARTURE_DATE)
            await page.keyboard.press("Enter")

            await page.wait_for_selector('button[type="submit"]', timeout=5000)
            await page.click('button[type="submit"]')

            # Palaukiam kainos
            await page.wait_for_selector('[data-ref="flight-card-price"]', timeout=15000)
            price_text = await page.inner_text('[data-ref="flight-card-price"]')
            price_value = ''.join(c for c in price_text if c.isdigit() or c == '.')
        except Exception as e:
            price_value = "N/A"
        finally:
            await browser.close()

        return price_value

def save_to_csv(price):
    CSV_FILE.parent.mkdir(exist_ok=True)
    row = [
        datetime.now().strftime("%Y-%m-%d"),
        ORIGIN,
        DESTINATION,
        DEPARTURE_DATE,
        price
    ]

    # Sukuriam failą su antrašte jei dar neegzistuoja
    if not CSV_FILE.exists():
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["date_scraped", "origin", "destination", "departu_]()
