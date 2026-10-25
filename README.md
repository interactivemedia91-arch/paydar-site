# Paydar website

Source of https://getpaydarapp.com: cancel guides (`/cancel/<slug>/`), US subscription price
increases (`/price-increases/`) and the Paydar homepage.

- `content/site.json`: base URL, App Store id and campaign provider token, links.
- `content/services/<serviceId>.json`: one cancel guide per service. FAQ answers can use
  `{price:Plan}`, `{monthly:Plan}` and `{yearly:Plan}`, filled from the current price.
- `content/held/`: guides that are written but not published yet (steps not verified).
- Prices come from the shared list at https://interactivemedia91-arch.github.io/prices.json,
  the same one the app's Price watch reads.
- `tools/build.py` builds everything into `_site/` (not committed):
  `python3 -I tools/build.py`. Tests: `python3 -I -m unittest discover -s tools/tests -t tools`.
- `.github/workflows/site.yml` tests, builds and deploys to GitHub Pages on every push to `main`
  and once a day, so announced price increases switch to "in effect" on their date.
