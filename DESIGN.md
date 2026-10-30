---
name: Paydar
description: The web home of Paydar, in the iPhone app's Aura look. A colour field made from your own subscriptions, controls on glass, content on calm frost.
colors:
  base: "#F3F1F8"
  base-dark: "#0B0A12"
  ink: "#15131F"
  ink-dark: "#F4F2FA"
  on-ink: "#FFFFFF"
  on-ink-dark: "#12101A"
  sub: "#5F5A73"
  sub-dark: "#A9A4BD"
  sheet: "#FAF9FD"
  sheet-dark: "#16141F"
  well: "rgba(21, 19, 31, .05)"
  well-dark: "rgba(255, 255, 255, .06)"
  hairline: "rgba(21, 19, 31, .08)"
  hairline-dark: "rgba(255, 255, 255, .08)"
  ring: "rgba(21, 19, 31, .13)"
  ring-dark: "rgba(255, 255, 255, .16)"
  glass: "rgba(255, 255, 255, .42)"
  glass-dark: "rgba(30, 27, 44, .34)"
  glass-border: "rgba(255, 255, 255, .75)"
  glass-border-dark: "rgba(255, 255, 255, .14)"
  frost: "rgba(255, 255, 255, .86)"
  frost-dark: "rgba(22, 20, 32, .86)"
  frost-border: "rgba(255, 255, 255, .95)"
  frost-border-dark: "rgba(255, 255, 255, .08)"
  accent: "#16A374"
  accent-dark: "#3DD6A6"
  accent-text: "#086B52"
  rise: "#E5484D"
  rise-dark: "#FF6B70"
  rise-text: "#B4232F"
  coin: "#E8B04B"
  coin-text: "#946413"
  lavender: "#B9A8F0"
  lavender-dark: "#7A5AF8"
typography:
  display:
    fontFamily: "-apple-system, BlinkMacSystemFont, SF Pro Display, Helvetica Neue, Segoe UI, Roboto, sans-serif"
    fontSize: "clamp(2.6rem, 1.5rem + 4.4vw, 5.6rem)"
    fontWeight: 800
    lineHeight: 0.96
    letterSpacing: "-0.04em"
  numeral:
    fontFamily: "-apple-system, BlinkMacSystemFont, SF Pro Display, Helvetica Neue, Segoe UI, Roboto, sans-serif"
    fontSize: "clamp(3rem, 1.8rem + 3.4vw, 5.6rem)"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: "-0.045em"
    fontFeature: "tnum"
  headline:
    fontFamily: "-apple-system, BlinkMacSystemFont, SF Pro Display, Helvetica Neue, Segoe UI, Roboto, sans-serif"
    fontSize: "clamp(2.2rem, 1.4rem + 2.6vw, 3.6rem)"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: "-0.035em"
  page-title:
    fontFamily: "-apple-system, BlinkMacSystemFont, SF Pro Display, Helvetica Neue, Segoe UI, Roboto, sans-serif"
    fontSize: "clamp(2.4rem, 1.4rem + 3.4vw, 4.2rem)"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: "-0.04em"
  section-title:
    fontFamily: "-apple-system, BlinkMacSystemFont, SF Pro Display, Helvetica Neue, Segoe UI, Roboto, sans-serif"
    fontSize: "clamp(1.6rem, 1.2rem + 1.2vw, 2.2rem)"
    fontWeight: 800
    lineHeight: 1.1
    letterSpacing: "-0.03em"
  title:
    fontFamily: "-apple-system, BlinkMacSystemFont, SF Pro Display, Helvetica Neue, Segoe UI, Roboto, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 800
    letterSpacing: "-0.02em"
  statement:
    fontFamily: "-apple-system, BlinkMacSystemFont, SF Pro Text, Helvetica Neue, Segoe UI, Roboto, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 400
    lineHeight: 1.5
  body:
    fontFamily: "-apple-system, BlinkMacSystemFont, SF Pro Text, Helvetica Neue, Segoe UI, Roboto, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.55
  small:
    fontFamily: "-apple-system, BlinkMacSystemFont, SF Pro Text, Helvetica Neue, Segoe UI, Roboto, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 400
  label:
    fontFamily: "ui-rounded, SF Pro Rounded, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 600
  caption:
    fontFamily: "ui-rounded, SF Pro Rounded, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 600
  wordmark:
    fontFamily: "ui-rounded, SF Pro Rounded, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: "-0.02em"
rounded:
  bar: "4px"
  tile: "9px"
  logo: "15px"
  callout: "20px"
  card: "24px"
  meter: "32px"
  panel: "clamp(28px, 3vw, 40px)"
  device: "44px"
  pill: "999px"
spacing:
  gutter: "clamp(20px, 4vw, 48px)"
  section: "clamp(112px, 9vw + 40px, 200px)"
  container: "1280px"
  article: "820px"
  chip-gap: "10px"
  preset-gap: "8px"
  card-pad: "20px 22px"
components:
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.on-ink}"
    typography: "{typography.body}"
    rounded: "{rounded.pill}"
    padding: "0 26px"
    height: "54px"
  button-primary-large:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.on-ink}"
    rounded: "{rounded.pill}"
    padding: "0 30px"
    height: "58px"
  button-primary-small:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.on-ink}"
    typography: "{typography.small}"
    rounded: "{rounded.pill}"
    padding: "0 18px"
    height: "44px"
  chip:
    backgroundColor: "{colors.glass}"
    textColor: "{colors.ink}"
    typography: "{typography.small}"
    rounded: "{rounded.pill}"
    padding: "0 18px 0 8px"
    height: "48px"
  chip-on:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.on-ink}"
    rounded: "{rounded.pill}"
  preset:
    backgroundColor: "{colors.well}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "0 16px"
    height: "44px"
  preset-checked:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.on-ink}"
    rounded: "{rounded.pill}"
  meter:
    backgroundColor: "{colors.glass}"
    textColor: "{colors.ink}"
    rounded: "{rounded.meter}"
    padding: "30px 30px 22px"
  frost-card:
    backgroundColor: "{colors.frost}"
    textColor: "{colors.ink}"
    rounded: "{rounded.card}"
    padding: "20px 22px"
  pricing-panel:
    backgroundColor: "{colors.frost}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "clamp(24px, 6vw, 88px)"
  price-alert-up:
    backgroundColor: "color-mix(in srgb, {colors.rise} 12%, {colors.sheet})"
    textColor: "{colors.rise-text}"
    rounded: "{rounded.pill}"
    padding: "8px 14px"
  price-alert-down:
    backgroundColor: "color-mix(in srgb, {colors.accent} 12%, {colors.sheet})"
    textColor: "{colors.accent-text}"
    rounded: "{rounded.pill}"
    padding: "8px 14px"
---

# Design System: Paydar

## Overview

**Creative North Star: "The Visitor's Own Aura"**

The site is painted by the person looking at it. Paydar's 2.0 iPhone app draws its Aura from the subscriptions you track; the site does the same with the services the visitor taps. A fixed radial colour field sits behind every page, made from those services' brand colours: biggest monthly cost first, greys skipped, one colour per 20 degrees of hue, at most five spots, each softened so text stays readable, each spot's radius weighted by price, a lavender glow at the top and a veil darkening toward the bottom. Past the hero, and on every reading page, the field steps back to half strength. Light and dark follow the system; nothing is themed by hand.

Over the field, two materials and one shape do all the work. Controls and the live meter sit on glass (translucent, heavily blurred, a 1px white edge). Content that must be read sits on frost (near-opaque, the same 1px edge). Every control is a pill. Type is SF Pro at heavy weights with tight tracking, so prices and totals read as the loudest thing on the screen, with SF Pro Rounded reserved for labels, captions and the wordmark, exactly as in the app. Colour beyond the field is semantic and scarce: red means a price went up, green means good news or the way out, gold means the one-time Pro price.

Density is calm and generous: one idea per section, large type, long section gaps. The homepage is the one place with live behaviour (picker, radar, counted total, the reminder preview); guides and the price-increase feed are reading pages and stay still apart from smooth scrolling.

**Key Characteristics:**
- A generative colour field from the visitor's own picks, fixed behind the page, quieter (0.5) past the hero and on reading pages.
- Glass for controls and the meter; frost for content panels, cards and lists.
- Every control a pill (999px); ink fill means primary or selected.
- Heavy, tightly tracked, tabular numerals as the loudest element.
- Semantic colour only: rise red, accent green, coin gold.
- Real app screens and real App Store service icons, never mock imagery.

## Colors

A near-neutral lavender-grey frame (light) or near-black violet (dark), with all saturated colour supplied by the visitor's field and three strictly semantic hues.

### Primary
- **Aura Ink** (ink / ink-dark): the text colour and the primary fill. Primary pills, picked chips and checked presets are filled with ink and lettered in On Ink, so "ink fill" reads as "act" or "selected" everywhere.
- **On Ink** (on-ink / on-ink-dark): text on an ink fill.

### Secondary
- **Good-News Green** (accent / accent-dark, text use accent-text): price drops (hatched bars, the down tag), the guide's "Fastest way" callout heading and step numbers, the billing note tint, and the radar beam that the app icon carries. In dark mode the bright accent doubles as its own text colour.
- **Rise Red** (rise / rise-dark, text use rise-text): announced or applied price increases only: the up tag and change chips, hatched announced bars, the "Announced" line and dates in the increase feed.

### Tertiary
- **Coin Gold** (coin; text use coin-text): the one-time $9.99 Pro price numeral (coin-text) and the Pro hint tint under the meter (coin at 18%). It is the gold coin of the app icon; it marks the one-time purchase and nothing else.
- **Aura Lavender** (lavender / lavender-dark): the fixed glow at the top of the field, present even with nothing picked.

### Neutral
- **Aura Base** (base / base-dark): the page background beneath the field.
- **Muted Sub** (sub / sub-dark): secondary text, captions, dates, chart's in-effect bars and its "now" key. Under `prefers-contrast: more` it becomes ink at 80%.
- **Sheet** (sheet / sheet-dark): the opaque fallback surface (Reduce Transparency) and the base that tag tints mix into.
- **Well** (well / well-dark): recessed fills: unchecked presets, step counters, the radar disc, flat tags, inline code.
- **Hairline** (hairline / hairline-dark): row dividers inside frost lists.
- **Ring** (ring / ring-dark): the radar's 7d, 14d and 30d rings and the chart baseline.
- **Glass and Frost** (glass, glass-border, frost, frost-border and their dark pairs): the two materials; see Elevation & Depth.

### Named Rules
**The Visitor Paints Rule.** Saturated colour in the frame comes from the field, and the field comes from the services picked (or the page's own service), softened in light to lightness 0.60 to 0.72 and in dark to 0.45 to 0.58, saturation clamped 0.45 to 0.80. With nothing picked it falls back to green, amber and violet (#16A374, #F2B35A, #8A6BD6). Never paint a decorative gradient by hand.

**The Semantic Colour Rule.** Red appears only for price increases; green only for good news and the way out of a charge; gold only for the one-time Pro price. Brand logos and the field may carry any hue, because they are the visitor's content, not interface colour.

**The Texture Not Only Colour Rule.** Wherever red or green marks a price change in a chart, it also carries a hatch (135 degrees) and an inset outline, so the meaning never rests on hue alone.

## Typography

**Display Font:** SF Pro Display (system stack: -apple-system, BlinkMacSystemFont, Helvetica Neue, Segoe UI, Roboto)
**Body Font:** SF Pro Text (same stack)
**Label Font:** SF Pro Rounded (ui-rounded, then the same stack)

**Character:** The app's own faces, used the way the app uses them: SF Pro at 800 with negative tracking for anything that should hit hard (headlines, totals, prices), regular SF Pro for reading, and SF Pro Rounded at 600 for the small friendly labels around data. On non-Apple systems the stack falls back gracefully; the world was chosen for iPhone owners.

### Hierarchy
- **Display** (800, clamp(2.6rem, 1.5rem + 4.4vw, 5.6rem), 0.96, -0.04em): the homepage H1 only, two lines at every width.
- **Numeral** (800, clamp(3rem, 1.8rem + 3.4vw, 5.6rem), 1, -0.045em, tabular): the meter's monthly total; the pricing panel's big prices use the same voice larger (clamp(3.5rem, 2rem + 4.5vw, 6.5rem)) with their unit at 0.35em, 700.
- **Headline** (800, clamp(2.2rem, 1.4rem + 2.6vw, 3.6rem), 1, -0.035em, max 14ch): homepage section H2s, written as short full sentences.
- **Page Title** (800, clamp(2.4rem, 1.4rem + 3.4vw, 4.2rem), 1, -0.04em): the H1 of guides, price increases and privacy.
- **Section Title** (800, clamp(1.6rem, 1.2rem + 1.2vw, 2.2rem), 1.1, -0.03em): H2s on reading pages.
- **Title** (800, 1.5rem, -0.02em): service names in cards and the "watch" H3.
- **Statement** (400, 1.25rem, 1.5, max 34 to 36em): ledes and the paragraphs beside homepage headlines.
- **Body** (400, 1.0625rem, 1.55; prose capped at 68ch): everything read.
- **Small** (400, 0.9375rem): facts lines, footnotes, sources.
- **Label** (Rounded 600, 0.9375rem): picker legend, meta lines, chart caption, dates, preset text, callout headings.
- **Caption** (Rounded 600, 0.8125rem): radar "Today" and blip names, change chips, notice app line; radar ring labels go to 0.6875rem.
- **Wordmark** (Rounded 800, 1.5rem, -0.02em): "Paydar" beside the radar mark; the footer repeats it huge (clamp(5rem, 22vw, 20rem), 0.8, -0.06em) at 9% ink as a quiet sign-off.

### Named Rules
**The Loud Numbers Rule.** A price or total is set heavier and larger than the words around it, always with tabular figures, so columns of prices align and a counted total does not jitter.

**The Rounded Is For Labels Rule.** SF Pro Rounded never sets a headline or body paragraph; it labels data and names the brand.

## Layout

A centred container (max 1280px) with a fluid gutter (clamp(20px, 4vw, 48px)) that also honours the left and right safe-area insets. Homepage sections are separated by a long fluid gap (clamp(112px, 9vw + 40px, 200px)) and mostly split in two asymmetric columns (1.05fr / 0.95fr in the hero, 0.9fr / 1.1fr and 1.1fr / 0.9fr below) with a wide column gap (clamp(40px, 7vw, 120px)). The hero puts copy and picker on the left and the glass meter on the right; above 960px wide and 700px tall the meter is sticky (top 96px).

Reading pages are a single column (820px, 940px for the increase feed) with the field at half strength. Guides open with the service logo and title, then the "Fastest way" callout, numbered steps, a billing note, the Paydar card, price list and chart, FAQ and sources; the searcher's answer always comes first.

Responsive steps observed in the build: 960px (hero stacks to copy, picker, meter; a compact glass total pins under the header while picking; guide groups go to two columns), 760px (two-column sections and plan grids stack, the tilted phone straightens, the screen row becomes a staggered single column at 78% width), 720px (header nav hides, leaving brand and the small pill), 520px and 480px (tighter meter, chips and panels), 374px and 360px (short pill labels, pills may wrap). Header, skip link and footer respect the top and bottom safe-area insets.

## Elevation & Depth

Depth is material, not stacked shadow. The fixed field is the deepest layer; glass and frost float over it with a 1px white border (strong in light, faint in dark) and one long, soft, violet-tinted ambient shadow pulled up under the element. The sticky header is a blurred band of base at 85% that fades out at its lower 10px instead of drawing a line.

### Shadow Vocabulary
- **Glass lift** (`box-shadow: 0 18px 50px -24px var(--shadow)`): glass controls, the meter, the notice, the Paydar card.
- **Frost lift** (`box-shadow: 0 12px 36px -22px var(--shadow)`): frost panels, cards and lists; slightly lower than glass.
- **Device** (`box-shadow: 0 40px 80px -40px var(--shadow), 0 0 0 1px var(--glass-border)`): the app screenshots (36px to 44px corners); the hairline ring is their edge.
- **Logo drop** (`box-shadow: 0 8px 18px -8px rgba(0,0,0,.55)`): radar blips, so logos sit above the disc.
- The shadow colour is rgba(60, 40, 120, .12) in light and rgba(0, 0, 0, .45) in dark.

### Named Rules
**The Glass For Hands, Frost For Eyes Rule.** Anything the visitor operates or watches change (chips, the meter, the pinned total, the notice, the Paydar card) is glass: blur(28px) saturate(1.6). Anything the visitor reads (pricing panel, cards, plan lists, charts, FAQ) is frost. Under Reduce Transparency both become opaque Sheet with no blur.

## Shapes

Soft, continuous, app-like corners. Every control is a full pill (999px): primary buttons, chips, presets, price alerts, the pinned total, the skip link. Containers step down in radius with their size: pricing panel clamp(28px, 3vw, 40px), meter 32px (28px under 520px), Paydar card 30px, the notice and lists and charts 24px, the billing note 20px. Service logos are circles on the picker and radar, rounded squares in lists (9px at 32px, 15px at 52px, 18px at 64px). The radar is a half-disc with three hairline rings; chart bars are square on the baseline and rounded 4px at the data end.

## Components

### Buttons
Confident ink pills with a trailing arrow, the only way to the App Store.
- **Shape:** full pill (999px), 600 weight, label never wraps except under 360px.
- **Primary:** ink fill, On Ink text; 54px tall with 26px sides by default, 58px / 30px for the large hero and close pills, 44px / 18px in the header.
- **Hover / Press:** on fine pointers only, a slight tint; on press every pill scales to 0.97 in 80ms and returns in 160ms on cubic-bezier(.23, 1, .32, 1).
- **Facts line:** every App Store pill is followed by its facts (free for 4, $9.99 once, no bank login), in Small.

### Chips (service picker)
- **Style:** glass pills 48px tall (44px under 520px), a 32px circular App Store icon at the left, 600 label.
- **State:** picked = ink fill with On Ink text (and a Highlight outline in forced colours); unpicked hover tints toward ink on fine pointers; press scales to 0.96. They are toggle buttons with aria-pressed.

### Presets (reminder lead times)
Real radio inputs drawn as small pills: Well fill, Rounded 600 label, checked = ink fill. They drive the phone notice.

### Cards / Containers
- **Corner Style:** 24px for cards and lists, 30px for the Paydar card, up to 40px for the pricing panel.
- **Background:** frost for reading content; glass for the Paydar call-to-action card.
- **Shadow Strategy:** Frost lift or Glass lift (see Elevation & Depth).
- **Border:** 1px frost or glass border; rows inside lists are divided by Hairline.
- **Internal Padding:** about 20px 22px for cards and rows, clamp(24px, 6vw, 88px) for the pricing panel.

### Navigation
A sticky blurred header: radar mark and Rounded 800 wordmark at left, two Sub-coloured text links (ink on hover) and a small ink pill at right. Under 720px the links hide. The footer repeats the links in 600 weight and closes on the giant faint wordmark.

### The Meter (signature)
A glass panel with the monthly total in Numeral type and "a month" beside it, the yearly figure under it, the radar below: a half-disc on Well with 7d, 14d and 30d rings, a 35 degree green beam turning once every 7s (paused off-screen, held still at 60 degrees under Reduce Motion), each pick's logo at the app's RadarLayout spot, "Today" at the centre. A Pro hint on a coin tint appears past four picks. Picking cross-fades the field in 0.6s, drops a blip in over 300ms, removes one over 150ms, and counts the total in 520ms with an ease-out cubic.

### Price Chart (guides)
Neutral Sub bars for prices in effect; an announced price is a red hatch with a red inset outline, a drop a green hatch. The legend appears only when an announced price exists. Values sit above bars in tabular 700; dates sit under the baseline. A visually hidden table carries the same data for screen readers.

### Phone Notice
A glass iOS-style notification laid over a real app screen: the app line (radar mark, "PAYDAR", "now"), a bold title, one line. It names the visitor's soonest pick at the chosen lead time.

### Tags and Change Chips
Price alerts are pills (8px 14px) and change chips small rounded rectangles (9px): up = rise at 12% over Sheet with rise-text, down = accent at 12% with accent-text, flat = Well.

## Do's and Don'ts

### Do:
- **Do** derive the field from real services through the shared steps (aura.py, home.js): at most 5 spots, 20 degree hue gap, greys skipped, radius 0.30 + 0.18 times weight over the biggest weight.
- **Do** drop the field to 0.5 opacity past the hero and on every reading page.
- **Do** put controls and live readouts on glass and reading content on frost, with the 1px white border.
- **Do** make every control a pill; fill it with ink when it is primary or selected.
- **Do** set prices and totals in heavy, tightly tracked, tabular SF Pro.
- **Do** keep hover effects inside (hover: hover) and (pointer: fine), drop the tap highlight, and give every pill, chip and card a press scale (0.96 to 0.985, 80ms in, 160ms out, cubic-bezier(.23, 1, .32, 1)).
- **Do** make every motion instant under Reduce Motion and skip loading GSAP; keep content visible without any script.
- **Do** honour safe-area insets on the header, gutters and footer.
- **Do** show real app screens (light and dark via picture sources) and real service icons with recorded provenance.

### Don't:
- **Don't** use red for anything but a price increase, green for anything but good news or the way out, or gold for anything but the one-time Pro price.
- **Don't** let a chart's meaning rest on colour alone; announced and dropped prices are hatched.
- **Don't** put a kicker or eyebrow above a headline; headlines stand alone.
- **Don't** draw hard offset shadows or stacked heavy shadows; depth is the soft material lift.
- **Don't** hand-paint gradients or add colour that the field did not produce.
- **Don't** set headlines or body copy in SF Pro Rounded.
- **Don't** use em dashes in user-facing text.
- **Don't** show ratings, reviews, download counts, testimonials or press that do not exist.
- **Don't** show the old name "Subsly".
