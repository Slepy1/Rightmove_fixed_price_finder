# Rightmove_fixed_price_finder

Web scraper used to search Rightmove for fixed price proerties, their keyword search does not work for this

You feed it a Rightmove search URL:

base_url = (
    "https://www.rightmove.co.uk/property-for-sale/find.html?minBedrooms=1&maxBedrooms=2&sortType=2&minPrice=50000&areaSizeUnit=sqft&viewType=LIST&channel=BUY&index=0&maxPrice=70000&radius=1.0&locationIdentifier=REGION%5E550"
)

it slices through the listings, ignoring everything except “Fixed Price” properties. No offers over. No guides. Just cold, hard, fixed numbers.

If Rightmove changes its structure, the selectors may break. When that happens… you'll need to dissect the new HTML and rewire the script.

Just past this code and rightmove source page code into chat gpt and you should be good

It scrapes:
The address
The price
The price qualifier
And a direct link to the listing

You’ll need:
Python 3.8 or higher
selenium undetected-chromedriver (pip install selenium undetected-chromedriver)
