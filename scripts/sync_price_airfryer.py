#!/usr/bin/env python3
"""
Fetch the current price of the Philips Walita Air Fryer Serie 1000 XL NA130
from the ML catalog API and update all price occurrences in index.html.
"""
import json
import re
import sys
import urllib.request

PRODUCT_ID = "MLB39292059"
PRODUCT_URL = f"https://api.mercadolibre.com/products/{PRODUCT_ID}"
# Reference (store) price used to calculate discount %
STORE_PRICE = 499
HTML_FILE = "air-fryer/index.html"


def fetch_ml_price() -> int:
    req = urllib.request.Request(PRODUCT_URL, headers={"User-Agent": "price-sync-bot/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())

    # Catalog product returns buy_box_winner with the current price
    buy_box = data.get("buy_box_winner", {})
    price = buy_box.get("price") or data.get("price")
    if price is None:
        print("ERROR: no price in ML API response", file=sys.stderr)
        print(json.dumps(data, indent=2), file=sys.stderr)
        sys.exit(1)

    print(f"Fetched: {data.get('name', PRODUCT_ID)} → R$ {price}")
    return int(price)


def update_html(price: int) -> bool:
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    original = html
    discount = round((STORE_PRICE - price) / STORE_PRICE * 100)

    # 1. Hero price-big
    html = re.sub(
        r'(<span class="price-big">R\$&nbsp;)\d+(<\/span>)',
        rf'\g<1>{price}\2',
        html,
    )

    # 2. Discount badge
    html = re.sub(
        r'(<span class="price-hero-badge">-)\d+(%<\/span>)',
        rf'\g<1>{discount}\2',
        html,
    )

    # 3. Hero subtext "Achei R$XXX no ML"
    html = re.sub(
        r'(Achei <strong>R\$)\d+(</strong>)',
        rf'\g<1>{price}\2',
        html,
    )

    # 4. Compare table ML row (no style attribute = ML row)
    html = re.sub(
        r'(<div class="compare-price">R\$ )\d+(</div>)',
        rf'\g<1>{price}\2',
        html,
    )

    # 5. CTA button text
    html = re.sub(
        r'(Comprar por R\$ )\d+( →)',
        rf'\g<1>{price}\2',
        html,
    )

    # 6. JSON-LD structured data price
    html = re.sub(
        r'("price":\s*")\d+\.\d+(")',
        rf'\g<1>{price}.00\2',
        html,
    )

    # 7. Recalculate competitor % differences
    known_competitors = [399, 359, 420, 389]
    for comp in known_competitors:
        if comp > price:
            pct = round((comp / price - 1) * 100)
            html = re.sub(
                r'(<div class="compare-status status-high">\+)\d+(%)',
                rf'\g<1>{pct}\2',
                html,
                count=1,
            )

    if html == original:
        print("No changes — price already up to date.")
        return False

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"index.html updated → R$ {price} (-{discount}%)")
    return True


if __name__ == "__main__":
    price = fetch_ml_price()
    changed = update_html(price)
    sys.exit(0 if changed else 2)
