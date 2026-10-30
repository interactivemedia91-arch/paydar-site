---
version: 1
slug: "tools-sitegen-render-py"
primary_target: "tools/sitegen/render.py"
related_targets: ["static/site.css"]
---

# Surface brief: homepage (getpaydarapp.com/)

Scope: the homepage (`home_page` in tools/sitegen/render.py, styles in static/site.css). Mode: Persuade.
The cancel guides (`/cancel/<slug>/`) and `/price-increases/` are Read surfaces that inherit this
world in the same redesign; their URLs, guide texts and the increases page's content and structure
stay (owner, 29 Oct 2026), and every App Store link keeps its per-page campaign tag.

Audience: referred visitors (Reddit, App Store, word of mouth) deciding whether to download; Google
searchers who land on guides and click through. Action: Download on the App Store (iPhone only).
Belief to leave: "I'll see every renewal before it charges me" (owner's choice), then "not another
subscription": free for 4, $9.99 once, no bank login, no account.
Proof on hand: the app's real mechanism (the colour field made from your subscriptions, the radar,
the total), real 2.0 screens in ~/Code/scratchpad/paydar-store-2.0/, sourced US prices.
Constraints: light + dark follow the system (owner); no "Subsly"; privacy moves to /privacy/;
support email stays; no invented ratings, reviews, counts or press; Lenis smooth scroll stays (owner).

## Direction contract

THESIS: The visitor paints Paydar with their own subscriptions: tapping what they pay for reseeds
the Aura field, fills the radar and counts their monthly total. It refuses the category default of a
headline beside a phone screenshot over a row of feature cards in the first viewport. Below the
hero the owner kept the explanatory sections as built (reminders and value each beside a real app
screen, then a row of three screens), carried by the fixed field and by the phone notice that names
the visitor's own soonest pick; owner's decision 2026-10-30 at the finish review: "Repar regresiile
și închid" (fix the regressions and close; the lower sections stay as they are).

OWN-WORLD: Aura from the 2.0 app. Base #0B0A12 / #F3F1F8, ink #F4F2FA / #15131F, sub #A9A4BD /
#5F5A73; a radial colour field made from the picked services (hue-deduped, softened, weighted to
the top, veiled toward the bottom); glass pills, glass lens and frost panels with 1px white borders;
SF Pro and SF Pro Rounded; heavy, tightly tracked numerals; every control a pill; red only for
price rises, accent green only for good news.

STORY: The visitor recognises their own subscriptions, sees what they cost a month and when each
renews on a radar, learns that Paydar does this on their iPhone with reminders, no bank login and a
one-time $9.99, and taps the App Store pill.

FIRST VIEWPORT: Header: radar mark + "Paydar", Cancel guides, Price increases, ink pill "Get it on
iPhone". Left column: H1 "Every charge, 3 days early." (two lines at every width; the owner's
message, no kicker above it), the lede saying what Paydar is, the App Store pill "Get Paydar free on
iPhone" with the facts line "Free for 4 subscriptions · $9.99 once for unlimited · No bank login",
then the chip group "Tap what you pay for" (14 services with their App Store icons, the first four
picked; glass chips, picked = ink fill). Right column: a glass panel with "$X a month" (~90px
numerals, no label above them), "About $Y a year for what you picked", a Pro note past 4 picks, and
the radar: a half-disc with the app's 7d / 14d / 30d rings, the picked logos at their spots (the
app's RadarLayout) and "Today" at the centre; then "Typical US prices and example dates". On narrow
screens the chips follow the copy, a compact total stays pinned while picking, and the panel follows.
Signature interaction: tapping a chip cross-fades the field to the new palette (0.6s), drops the
logo into the radar with a spring, and counts the total to its new value. Reduced motion: instant.

FORM: Fused challenger "generative parametric identity" (seed-derived palette restyling the whole
surface), chosen by the owner over the dealt structures. seed:d30b186abd557418

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
