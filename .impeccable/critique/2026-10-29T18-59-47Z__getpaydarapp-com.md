---
target: site-ul getpaydarapp.com
total_score: 26
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 3
target_identity: "url:https://getpaydarapp.com/"
timestamp: 2026-10-29T18-59-47Z
slug: getpaydarapp-com
---
Method: dual-agent (A: design review · B: detector + browser, isolated)

## Critique: getpaydarapp.com (homepage, 5 cancel guides, /price-increases/; 1440 and 390 px)

| # | Heuristic | Score | Key issue |
|---|---|---|---|
| 1 | Visibility of system status | 3 | Dated data; hatched gold "upcoming" chart bar has no legend |
| 2 | Match with real world | 3 | "Formerly Subsly" means nothing to new visitors; "Paramount Plus" vs "Paramount+" |
| 3 | User control and freedom | 2 | `.price-cta` looks like an in-article link but leaves for the App Store; 5,600 px /price-increases/ with no jump links |
| 4 | Consistency and standards | 2 | Increases gold on guides, green on `.upcoming-card`; 8px buttons vs app pills; 3 labels for one action |
| 5 | Error prevention | 2 | "Get Paydar, free" hides the 4-sub limit; "iPhone" never stated (Android dead end) |
| 6 | Recognition rather than recall | 3 | Good numbered steps + "Fastest way"; 19 guides alphabetical only |
| 7 | Flexibility and efficiency | 3 | "Fastest way" shortcut good; 31-row increases list has no filter |
| 8 | Aesthetic and minimalist design | 3 | Guides clean; homepage hero mixes CTA with gmail and "Formerly Subsly" |
| 9 | Error recovery | 3 | Strong troubleshooting copy styled in the most muted `.billing-note` |
| 10 | Help and documentation | 2 | Nothing about Paydar itself (price, privacy, platform); support = personal gmail |
| **Total** | | **26/40** | **Acceptable** |

Design specificity: category-interchangeable (white 760px column, system font, mint callout, dark CTA slab, green 8px button); none of 2.0's radar, card fan, Aura colour field, glass, pills; still 1.x deep green #123A2C. Only the content (sourced prices, gold tag, history chart) is Paydar-specific.

Detector: 81 findings / 3 rules. False positives: cramped-padding ×58 (not reproduced in browser), repeating-stripes-gradient ×21 (shared stylesheet; chart gridlines and "announced" hatch = data encoding). True positive: border-accent-on-rounded on `.upcoming-card` (site.css:299). Browser-only: stragglers / unbalanced headings (no text-wrap balance/pretty). Objective: all text ≥4.5:1, 4 requests ~50 KB, load ~0.23 s, no overflow, heading order fine, alt present; small targets: inline source links, "Every recent and announced US price increase →" 19px tall at desktop; card CTA focus ring ~2.4:1.

Priority issues:
- [P1] Homepage never shows the product: H1 "Paydar", benefit in small grey text, no screenshot/features/price, below the hero a 19-link sitemap. Fix: benefit H1, 2.0 phone frame (radar + "Spotify is going up" pill), 3 proof rows, price line, grouped compact guides. Command: /impeccable shape
- [P1] Price and best trust claim missing; trust signals undercut: no "free for 4, then $9.99 once, no subscription", no "no account / no ads", gmail + gist privacy + "Formerly Subsly" under the main CTA. Fix: one line under every CTA; /privacy/ on the domain; support@ address; remove from hero. Command: /impeccable clarify
- [P1] Platform never stated; no persistent mobile CTA (`.desktop-app-link` hidden <760px, Smart App Banner absent in Chrome iOS / in-app browsers); desktop links to an uninstallable page. Fix: "Free on iPhone", "iPhone only" note for non-iOS, compact pill CTA in mobile header, QR on desktop. Command: /impeccable adapt
- [P2] Site matches 1.x, not 2.0 Aura. Fix: per-service aura tint on each guide's `.paydar-card`, service logo by H1, pill CTAs, dark scheme. Command: /impeccable colorize
- [P2] Colour/chart semantics inconsistent: increases gold vs green `.upcoming-card`; bar colour by position; unlabeled `.chart-key` dot; no hatch legend; values-then-dates screen reader order. Fix: one increase colour, "In effect / Announced" legend, colour by state, visually hidden table. Command: /impeccable polish

Persona red flags: Jordan (no product image, unclear price, unclear app vs help site); Riley (gist privacy, gmail support, free→paywall at 5th, Netflix steps differ from in-app guide, Amazon Prime lacks prices section, Hulu twice without guide, focus ring 2.4:1); Casey (no mobile header CTA, first CTA 850–1170px down, no banner on Android / Google app, 5,600px increases page).

Minor: guide columns misaligned ~20px; CTA arrow space-between reads like a field, no official App Store badge; `.tag-flat` looks disabled; Adobe early-termination fee buried in FAQ; single-link H2 section; og:image is the square icon.

Questions: per-service colour on guides? Is the guide card the real landing page? Why is "$9.99 once, no subscription" invisible? Why describe the price-change card instead of showing it?
