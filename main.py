# main.py
import requests
from bs4 import BeautifulSoup
import re
import time
import pandas as pd

HEADERS = {
    "User-Agent": "market-scan-agent/1.0 (+https://github.com/your-username)"
}

# Put your supplier product URLs here (change names & URLs to the pages you want)
PAGES = [
    {"supplier": "KK E-Trades", "url": "https://kketrades.com/shop/ppr-pipe-20mm-8552", "note": "20mm product page"},
    {"supplier": "Randtech", "url": "https://www.randtech.co.ke/product/ppr-pipe-3-4/", "note": "20 mm product"},
    {"supplier": "Metro Concepts", "url": "https://metroconcepts.co.ke/ppr-pipes/", "note": "catalog - may need manual selector"},
    # Add more pages...
]

# Common CSS selectors to try for price elements
PRICE_SELECTORS = [
    "span.price", "p.price", "div.price",
    ".woocommerce-Price-amount", ".amount",
    "span[class*=price]", "div[class*=price]",
    ".product-price", ".price-including-tax"
]

# Regex to find price amounts followed or preceded by KSh/KES/KES.
PRICE_RE = re.compile(r"(?<!\d)(\d{1,3}(?:[,\d]{0,3})*(?:\.\d+)?)[\s]*(?:KSh|KES|KES\.)?", re.IGNORECASE)

def fetch(url, timeout=12):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"[fetch] ERROR for {url}: {e}")
        return None

def parse_price_from_text(text):
    # Try to find currency with KSh or bare numbers
    # First try patterns with KSh
    m = re.search(r"(\d{1,3}(?:[,\d]{3})*(?:\.\d+)?)\s*(?:KSh|KES|kes|ksh)", text)
    if not m:
        # general numeric fallback
        m = PRICE_RE.search(text)
    if not m:
        return None
    raw = m.group(1)
    # Normalize: remove commas
    val = raw.replace(",", "")
    try:
        return float(val)
    except:
        return None

def extract_price(soup, page_text):
    # 1) Try selectors
    for sel in PRICE_SELECTORS:
        el = soup.select_one(sel)
        if el:
            txt = el.get_text(" ", strip=True)
            price = parse_price_from_text(txt)
            if price is not None:
                return price, txt

    # 2) Try looking for elements that contain "KSh"
    elems = soup.find_all(text=re.compile(r"(KSh|KES|kes|ksh)"))
    for t in elems:
        txt = t.strip()
        price = parse_price_from_text(txt)
        if price is not None:
            return price, txt

    # 3) Fallback: parse the whole page text
    price = parse_price_from_text(page_text)
    if price is not None:
        return price, str(price)

    return None, None

def scrape_page(supplier, url):
    print(f"[scrape] {supplier} -> {url}")
    html = fetch(url)
    if not html:
        return {"supplier": supplier, "url": url, "price": None, "raw": None, "error": "fetch failed"}

    soup = BeautifulSoup(html, "lxml")
    page_text = soup.get_text(" ", strip=True)

    price, raw = extract_price(soup, page_text)
    if price is None:
        return {"supplier": supplier, "url": url, "price": None, "raw": None, "error": "price not found"}
    return {"supplier": supplier, "url": url, "price": price, "raw": raw, "error": None}

def main():
    results = []
    for p in PAGES:
        r = scrape_page(p["supplier"], p["url"])
        results.append(r)
        time.sleep(1.5)  # be polite; don't hammer servers

    df = pd.DataFrame(results)
    # Keep only successful scrapes
    ok = df[df["price"].notnull()].copy()
    if not ok.empty:
        ok = ok.sort_values("price")
        ok.to_csv("output.csv", index=False)
        ok.to_excel("output.xlsx", index=False)
        cheapest = ok.iloc[0].to_dict()
        print("[result] Cheapest supplier:", cheapest)
    else:
        print("[result] No prices found; see results dataframe")
        df.to_csv("output.csv", index=False)
        df.to_excel("output.xlsx", index=False)

    print("Saved output.csv and output.xlsx")

if __name__ == "__main__":
    main()
