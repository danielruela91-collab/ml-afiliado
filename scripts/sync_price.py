#!/usr/bin/env python3
"""
Fetch the current Growth Creatina 250g price from Mercado Livre
and update all price occurrences in index.html.
"""
import json
import re
import sys
import urllib.request

SEARCH_URL = (
    "https://api.mercadolibre.com/sites/MLB/search"
    "?q=creatina+growth+monohidratada+250g&limit=10"
)
# Reference (store) price used to calculate discount %
STORE_PRICE = 62
HTML_FILE = "index.html"


def fetch_ml_price() -> int:
    req = urllib.request.Request(SEARCH_URL, headers={"User-Agent": "price-sync-bot/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())

    results = data.get("results", [])
    if not results:
        print("ERROR: no results from ML API", file=sys.stderr)
        sys.exit(1)

    # Prefer results whose title contains "growth" and "250"
    for item in results:
        title = item.get("title", "").lower()
        if "growth" in title and "250" in title:
            price = int(item["price"])
            print(f"Matched: {item['title']} → R$ {price}")
            return price

    # Fallback: first result
    price = int(results[0]["price"])
    print(f"Fallback: {results[0]['title']} → R$ {price}")
    return price


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

    # 3. Hero subtext "Achei R$XX no ML"
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

    # 6. Recalculate competitor % differences in compare-status
    competitor_prices = {62: None, 54: None, 67: None, 59: None}
    def recalc_status(m):
        raw = m.group(0)
        # extract the compare-price from the same row isn't possible with a single
        # regex pass; instead rebuild the known competitor rows
        return raw

    # Simpler: replace each known "+XX% mais caro" with recalculated value
    known_competitors = [62, 54, 67, 59]
    for comp in known_competitors:
        if comp > price:
            pct = round((comp / price - 1) * 100)
            # Replace the status for this competitor
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
