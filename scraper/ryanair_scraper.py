import csv
import datetime
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

# Konstantos
ORIGIN = "Vilnius"
DESTINATION = "Athens"
DEPARTURE_DATE = "2025-08-24"
CSV_FILE = Path("data/flights.csv")

async def fetch_price():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto("https://www.ryanair.com/")

            # Pasirenkame kalbą ir uždarome slapukų sutikimą (jei yra)
            try:
                await page.click("button[aria-label='Consent']")
            except:
                pass

            # Įvedame duomenis
            await page.click("input[placeholder='From']")
            await page.fill("input[placeholder='From']", ORIGIN)
            await page.keyboard.press("Enter")

            await page.click("input[placeholder='To']")
            await page.fill("input[placeholder='To']", DESTINATION)
            await page.keyboard.press("Enter")

            await page.click("input[placeholder*='Departure']")
            await page.click(f"[data-id='{DEPARTURE_DATE}']")

            await page.click("button[aria-label='Search']")

            # Palaukime kol įkels rezultatą
            await page.wait_for_selector(".fare-card-price", timeout=15000)

            # Gauti kainą
            price_element = await page.query_selector(".fare-card-price")
            price_text = await price_element.inner_text()
            price_eur = "".join([c for c in price_text if c.isdigit() or c == "."])

        except Exception as e:
            print(f"Klaida ieškant kainos: {e}")
            price_eur = "N/A"

        await browser.close()
        return price_eur

def save_to_csv(price_eur):
    today = datetime.date.today().isoformat()

    if not CSV_FILE.exists():
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["date_scraped", "origin", "destination", "departure_date", "price_eur"])

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([today, ORIGIN, DESTINATION, DEPARTURE_DATE, price_eur])

def main():
    price = asyncio.run(fetch_price())
    save_to_csv(price)

if __name__ == "__main__":
    main()
