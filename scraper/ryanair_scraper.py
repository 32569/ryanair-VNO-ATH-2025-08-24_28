"""
Ryanair scraper – kasdien paima skrydžio kainą
Vilnius (VNO) ➜ Athens (ATH) 2025-08-24 ir įrašo į data/flights.csv
"""

import asyncio, csv, os
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PWTimeout

# --- konfigūracija -----------------------------------------------------------
URL          = "https://www.ryanair.com/gb/en"
ORIGIN       = "Vilnius"
DESTINATION  = "Athens"
DEPART_DATE  = "2025-08-24"            # yyyy-mm-dd
CSV_PATH     = Path("data/flights.csv")
WAIT_TIMEOUT = 60_000                  # 60 s laukimo limitas
# -----------------------------------------------------------------------------

async def fetch_price() -> str | None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page    = await browser.new_page()

        # 1️⃣  atidarom puslapį ir laukiam pilno užkrovimo
        await page.goto(URL, timeout=WAIT_TIMEOUT)
        await page.wait_for_load_state("networkidle")

        try:
            # 2️⃣  laukiam formos laukelio „From“ (placeholder gali keistis,
            #     todėl ieškome pagal aria-label, kuris Ryanair’e stabilus)
            await page.wait_for_selector("input[aria-label='Departure airport']",
                                         timeout=WAIT_TIMEOUT)

            # 3️⃣  pildom skrydžio duomenis
            await page.fill("input[aria-label='Departure airport']", ORIGIN)
            await page.keyboard.press("Enter")
            await page.fill("input[aria-label='Destination airport']", DESTINATION)
            await page.keyboard.press("Enter")

            # 4️⃣  datą įvedame paprastesniu būdu (search mygtukas pats parenka)
            await page.click("button[type='submit']")

            # 5️⃣  laukiame kainos elemento (mažiausia kaina – `aria-label='Price'`)
            await page.wait_for_selector("[data-ref='flight-card-price']", timeout=WAIT_TIMEOUT)
            price_raw = await page.inner_text("[data-ref='flight-card-price']")
            price     = price_raw.replace("€", "").replace(",", ".").strip()

        except PWTimeout:
            print("⚠️ Nepavyko rasti laukelio ar kainos per nurodytą laiką.")
            price = None
        finally:
            await browser.close()

        return price


def save_to_csv(price: str | None) -> None:
    CSV_PATH.parent.mkdir(exist_ok=True)
    today = datetime.utcnow().strftime("%Y-%m-%d")

    header_needed = not CSV_PATH.exists()
    with CSV_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if header_needed:
            writer.writerow(["date_scraped", "origin", "destination", "departure_date", "price_eur"])
        writer.writerow([today, ORIGIN, DESTINATION, DEPART_DATE, price or "N/A"])


if __name__ == "__main__":
    price_val = asyncio.run(fetch_price())
    save_to_csv(price_val)
    print(f"✅ Išsaugota kaina: {price_val or 'N/A'} €")
