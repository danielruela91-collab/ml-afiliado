# Landing Page Preferences

## Stack & Deployment
- Single `index.html` — no build system
- Deploy via Vercel GitHub integration: push to `main` → auto-deploy
- All changes: git commit + push to `main`

## Design System

### Colors
- Background: `#060608`
- Surface: `#0f0f12`, `#18181e`
- Accent (Mercado Livre yellow): `#FFE600`
- Accent dim: `#FFE60015`
- Accent glow: `#FFE60030`
- Border glow: `#FFE60044`
- Text: `#f0f0f5`
- Muted: `#6b6b7a`
- CTA hover: `#ffd000`

### Typography
- Headings: Syne 700 (Google Fonts)
- Body: Inter 400/500/600/700 (Google Fonts)
- Language: Portuguese (Brazil)

### Layout
- Topbar: accent background, black text, centered, 13px/600
- Hero: 2-column grid (`1fr 1fr`), text left / image right; collapses to 1 column on mobile (image on top, `order: -1`)
- Product image: `max-width: 240px` desktop, `200px` mobile — keep small so text/buttons have room
- Max content width: 900px centered

### CTA Button
- Background: `var(--accent)`, color: `#000`, font-weight: 700
- Hover: background `#ffd000`, translateY(-2px), glow shadow
- Box shadow: `0 0 24px var(--accent-glow)`

## Sections

### Ranking Section
- Top 4 products ranked by custo-benefício
- Each card: rank number + "Lugar" label, brand name, product description, tags, CTA
- `#1`: `rank-first` class + "Vencedora" badge (accent color button)
- `#2–4`: `btn-rank-secondary` + "#N Recomendada" badge

### Price Compare Section
- Compare ML price vs: Loja Oficial, Shopee, Amazon, Magazine Luiza
- ML row: no inline style (inherits accent color)
- Competitor rows: `style="color:#f0f0f5"` + `+XX% mais caro` status badge
- Competitor % is calculated relative to ML price

### Dates
- All dates (last verified, compare date) are injected dynamically via JS on page load
- Use `dd/mm/yyyy` format in pt-BR

## Nightly Price Sync (GitHub Actions)

Always include these two files for any ML affiliate landing page:

### `.github/workflows/sync-price.yml`
```yaml
name: Sync ML Price
on:
  schedule:
    - cron: '0 6 * * *'  # 3 AM BRT = 6 AM UTC
  workflow_dispatch:
permissions:
  contents: write
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Fetch price and update page
        id: sync
        run: python scripts/sync_price.py
        continue-on-error: true
      - name: Commit and push if changed
        if: steps.sync.outcome == 'success'
        run: |
          git config user.name "price-bot"
          git config user.email "noreply@github.com"
          git add index.html
          git diff --cached --quiet && echo "Nothing to commit" || \
            (git commit -m "chore: sync ML price $(date +'%Y-%m-%d')" && git push)
```

### `scripts/sync_price.py`
- Use exact ML catalog product ID (ask user for it — found in the product page URL as `MLB-XXXXXXXX`)
- Full ID format: `MLBXXXXXXXX` (e.g. `MLBUY0QGQ841V`)
- API endpoint: `https://api.mercadolibre.com/products/{PRODUCT_ID}`
- Price field: `response["buy_box_winner"]["price"]` (fallback: `response["price"]`)
- Elements to update in `index.html`:
  - `<span class="price-big">R$&nbsp;{price}</span>`
  - `<span class="price-hero-badge">-{discount}%</span>`
  - `Achei <strong>R${price}</strong> no ML`
  - `<div class="compare-price">R$ {price}</div>` (ML row — no style attribute)
  - `Comprar por R$ {price} →` (CTA button text)
  - Competitor `+XX% mais caro` badges (recalculate from known competitor prices)
- Exit 0 if changed, exit 2 if no change (not an error)
