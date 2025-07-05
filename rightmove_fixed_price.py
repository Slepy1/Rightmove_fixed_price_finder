import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def add_or_update_url_param(url, param_name, param_value):
    url_parts = list(urlparse(url))
    query = dict(parse_qs(url_parts[4]))
    query[param_name] = [str(param_value)]
    url_parts[4] = urlencode(query, doseq=True)
    return urlunparse(url_parts)

def create_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")  # Optional: headless mode
    driver = uc.Chrome(options=options)
    return driver

def scrape_fixed_price_properties(base_url, max_pages=24, restart_every=5):
    all_properties = []
    seen = set()  # to track (address.lower(), price) pairs

    driver = create_driver()
    try:
        for page in range(max_pages):
            if page > 0 and page % restart_every == 0:
                try:
                    driver.quit()
                except Exception as e:
                    print(f"⚠️ Error quitting driver: {e}")
                driver = create_driver()

            url = add_or_update_url_param(base_url, "index", page * 24)
            print(f"\n🔍 Scraping page {page + 1}...")
            driver.get(url)

            if page == 0:
                try:
                    cookie_btn = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
                    )
                    cookie_btn.click()
                    print("✅ Cookie consent accepted.")
                except Exception:
                    print("⚠️ Cookie consent not found or already accepted.")

            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class^='PropertyCard_propertyCard']"))
            )

            cards = driver.find_elements(By.CSS_SELECTOR, "div[class^='PropertyCard_propertyCard']")
            print(f"📦 Found {len(cards)} cards on this page.")

            for card in cards:
                try:
                    price_qualifier = card.find_element(By.CSS_SELECTOR, "div[class^='PropertyPrice_priceQualifier']").text
                except:
                    price_qualifier = ""

                if "Fixed Price" not in price_qualifier:
                    continue

                try:
                    address = card.find_element(By.CSS_SELECTOR, "address[class^='PropertyAddress_address']").text
                except:
                    address = "N/A"

                try:
                    price = card.find_element(By.CSS_SELECTOR, "div[class^='PropertyPrice_price__']").text
                except:
                    price = "N/A"

                try:
                    link_element = card.find_element(By.XPATH, ".//a[@href]")
                    href = link_element.get_attribute("href")
                except:
                    href = "N/A"

                key = (address.strip().lower(), price.strip())
                if address != "N/A" and key in seen:
                    continue
                elif address == "N/A" and any(p == price.strip() for (_, p) in seen):
                    continue

                seen.add(key)
                all_properties.append((address, price, price_qualifier, href))
                print(f"🏠 {address} — 💷 {price} ({price_qualifier}) 🔗 {href}")

            if len(cards) < 24:
                print("⚠️ Less than 24 cards, probably last page.")
                break

            time.sleep(1)

    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                print(f"⚠️ Error quitting driver in finally: {e}")
            driver = None

    print(f"\n📊 Scraping Summary\n─────────────────────────────")
    print(f"🔹 Total cards scanned:         {len(all_properties) + len(seen)}")  # Approximate
    print(f"🔹 Fixed price listings found:  {len(all_properties)}")
    print(f"🔹 Skipped (duplicates):        {len(seen) - len(all_properties)}")
    print("─────────────────────────────")
    print("✅ Scraping complete.\n")

    for i, (address, price, qualifier, href) in enumerate(all_properties, 1):
        print(f"{i:02d}. 🏠 {address} — 💷 {price} ({qualifier}) 🔗 {href}")

    return all_properties

# Start scraping
base_url = (
    "https://www.rightmove.co.uk/property-for-sale/find.html?minBedrooms=1&maxBedrooms=2&sortType=2&minPrice=50000&areaSizeUnit=sqft&viewType=LIST&channel=BUY&index=0&maxPrice=70000&radius=1.0&locationIdentifier=REGION%5E550"
)

scrape_fixed_price_properties(base_url)
