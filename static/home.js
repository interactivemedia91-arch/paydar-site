/* The homepage's live part: tapping what you pay for repaints the colour field, fills the radar and
   counts the monthly total. The page is complete without it (the server renders four picks). */
(() => {
  const picker = document.querySelector(".picker");
  const meter = document.querySelector(".meter");
  const field = document.querySelector(".field");
  if (!picker || !meter || !field) return;

  const data = JSON.parse(document.getElementById("home-data")?.textContent || "{}");
  const reduce = matchMedia("(prefers-reduced-motion: reduce)");
  const monthEl = meter.querySelector(".total-month");
  const yearEl = meter.querySelector(".total-year");
  const hint = meter.querySelector(".pro-hint");
  const blips = meter.querySelector(".blips");
  const live = meter.querySelector(".meter-live");
  const mini = picker.querySelector(".mini-month");
  const FREE_LIMIT = 4;
  const money = (x) => "$" + x.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  // ---- The Aura field (the same steps as tools/sitegen/aura.py and the app's AuraPalette).
  const hsl = (hex) => {
    const n = parseInt(hex.slice(1), 16);
    const r = (n >> 16 & 255) / 255, g = (n >> 8 & 255) / 255, b = (n & 255) / 255;
    const max = Math.max(r, g, b), min = Math.min(r, g, b), l = (max + min) / 2, d = max - min;
    if (!d) return [0, 0, l];
    const s = l > .5 ? d / (2 - max - min) : d / (max + min);
    const h = max === r ? (g - b) / d + (g < b ? 6 : 0) : max === g ? (b - r) / d + 2 : (r - g) / d + 4;
    return [h * 60, s, l];
  };
  const hex = (h, s, l) => {
    const k = (n) => (n + h / 30) % 12, a = s * Math.min(l, 1 - l);
    const f = (n) => Math.round(255 * (l - a * Math.max(-1, Math.min(k(n) - 3, 9 - k(n), 1))));
    return "#" + [f(0), f(8), f(4)].map((v) => v.toString(16).padStart(2, "0")).join("").toUpperCase();
  };
  const clamp = (x, lo, hi) => Math.min(Math.max(x, lo), hi);
  const soften = (color, dark) => {
    const [h, s, l] = hsl(color);
    return hex(h, clamp(s, .45, .8), dark ? clamp(l, .45, .58) : clamp(l, .6, .72));
  };
  const hueGap = (a, b) => { const d = Math.abs(a - b) % 360; return Math.min(d, 360 - d); };
  const spots = (items) => {
    const kept = [];
    for (const it of [...items].sort((a, b) => b.price - a.price)) {
      if (kept.length >= 5) break;
      const [h, s] = hsl(it.color);
      if (s < .1 || kept.some((k) => hueGap(k.h, h) < 20)) continue;
      kept.push({ color: it.color, h, cost: it.price });
    }
    if (!kept.length) return ["#16A374", "#F2B35A", "#8A6BD6"].map((c) => ({ color: c, w: 1 / 3 }));
    const total = kept.reduce((t, k) => t + k.cost, 0);
    return kept.map((k) => ({ color: k.color, w: total > 0 ? k.cost / total : 1 / kept.length }));
  };
  const paint = (items) => {
    const list = spots(items), biggest = Math.max(...list.map((s) => s.w));
    for (let i = 1; i <= 5; i++) {
      const s = list[i - 1];
      field.style.setProperty(`--s${i}`, s ? soften(s.color, false) : "transparent");
      field.style.setProperty(`--d${i}`, s ? soften(s.color, true) : "transparent");
      field.style.setProperty(`--r${i}`, s ? (.3 + .18 * s.w / biggest).toFixed(3) : "0");
    }
  };

  // ---- The total counts to its new value (instant under Reduce Motion).
  let shown = Number(monthEl.textContent.replace(/[^0-9.]/g, "")) || 0, raf = 0;
  const dollars = (x) => "$" + Math.round(x).toLocaleString("en-US");
  const count = (to, note) => {
    cancelAnimationFrame(raf);
    const from = shown, start = performance.now(), dur = reduce.matches ? 0 : 520;
    const step = (now) => {
      const t = dur ? Math.min(1, (now - start) / dur) : 1;
      shown = from + (to - from) * (1 - Math.pow(1 - t, 3));
      monthEl.textContent = money(shown);
      if (mini) mini.textContent = money(shown);
      yearEl.textContent = dollars(shown * 12);
      if (t < 1) raf = requestAnimationFrame(step);
      else live.textContent = `${money(to)} a month, about ${dollars(to * 12)} a year. ${note}`.trim();
    };
    raf = requestAnimationFrame(step);
  };

  // ---- The radar: one blip per pick, at the spot the server worked out for every chip (the app's
  // RadarLayout), so picks never move when another is added. The sooner, the closer to Today.
  const blipFor = (chip) => {
    const id = chip.dataset.id, spot = data.spots?.[id];
    if (!spot) return null;
    const days = spot.d, angle = spot.a * Math.PI / 180, radius = spot.r * (data.inset ?? 1);
    const li = document.createElement("li");
    li.className = "blip";
    li.dataset.id = id;
    li.style.left = (50 + 50 * radius * Math.cos(angle)).toFixed(2) + "%";
    li.style.top = (100 - 100 * radius * Math.sin(angle)).toFixed(2) + "%";
    const logo = chip.querySelector(".chip-logo").cloneNode(true);
    logo.classList.replace("chip-logo", "blip-logo");
    const sr = document.createElement("span");
    sr.className = "sr-only";
    sr.textContent = `${chip.dataset.name} renews in ${days} days`;
    li.append(logo, sr);
    return li;
  };
  // Blips are updated in place, so a landing blip is never cut short by the next tap; a dropped one
  // leaves faster than it came (150 vs 300 ms) and comes back if re-picked on its way out.
  const drawRadar = (picked, added) => {
    const want = new Set(picked.map((chip) => chip.dataset.id));
    const have = new Set();
    for (const li of [...blips.children]) {
      const leaving = li.classList.contains("blip-out");
      if (want.has(li.dataset.id)) {
        if (leaving) { li.getAnimations().forEach((a) => a.cancel()); li.classList.remove("blip-out"); }
        have.add(li.dataset.id);
      } else if (reduce.matches || !li.animate) {
        li.remove();
      } else if (!leaving) {
        li.classList.add("blip-out");
        li.animate([{ opacity: 1 }, { opacity: 0, transform: "translate(-50%, -50%) scale(.85)" }],
          { duration: 150, easing: "cubic-bezier(.23, 1, .32, 1)", fill: "forwards" }).onfinish = () => li.remove();
      }
    }
    for (const chip of picked) {
      if (have.has(chip.dataset.id)) continue;
      const li = blipFor(chip);
      if (!li) continue;
      if (chip === added && !reduce.matches) li.classList.add("blip-in");
      blips.append(li);
    }
  };

  // ---- The reminder on the phone: the visitor's soonest pick, at the lead time chosen under it
  // (the same wording as render.py's _notice_text). With nothing picked it keeps the page's example.
  const notice = document.querySelector(".notice");
  const presets = document.querySelector(".presets");
  const drawNotice = () => {
    if (!notice) return;
    const picked = [...picker.querySelectorAll(".chip.on")].filter((c) => data.spots?.[c.dataset.id]);
    const soonest = picked.sort((a, b) => data.spots[a.dataset.id].d - data.spots[b.dataset.id].d)[0];
    const name = soonest ? soonest.dataset.name : notice.dataset.name;
    const price = Number(soonest ? soonest.dataset.price : notice.dataset.price);
    const days = Number(presets?.querySelector("input:checked")?.value ?? 3);
    const when = days === 0 ? "today" : days === 1 ? "tomorrow" : `in ${days} days`;
    const title = `${name} renews ${days === 0 ? "today" : "soon"}`, line = `On your radar: ${money(price)} renews ${when}`;
    notice.querySelector(".notice-title").textContent = title;
    notice.querySelector(".notice-line").textContent = line;
    notice.setAttribute("aria-label", `A Paydar reminder: ${title}. ${line}.`);
  };
  presets?.addEventListener("change", drawNotice);

  const update = (added) => {
    const picked = [...picker.querySelectorAll(".chip.on")];
    const items = picked.map((c) => ({ color: c.dataset.color, price: Number(c.dataset.price) }));
    const total = items.reduce((t, it) => t + it.price, 0);
    let note = "";
    if (picked.length > FREE_LIMIT) note = `That's ${picked.length}. Free tracks ${FREE_LIMIT}; Paydar Pro tracks all of them for $9.99, once.`;
    else if (!picked.length) note = "Tap a service to put it on your radar.";
    hint.textContent = note;
    hint.hidden = !note;
    paint(items);
    count(total, note);
    drawRadar(picked, added);
    drawNotice();
  };

  // The beam only turns while the radar is on screen.
  const beam = meter.querySelector(".beam");
  if (beam && "IntersectionObserver" in window) {
    new IntersectionObserver(([e]) => { beam.style.animationPlayState = e.isIntersecting ? "" : "paused"; })
      .observe(meter.querySelector(".radar"));
  }

  // Past the hero, the field steps back so text over it stays readable (the app's 0.6 strength).
  const hero = document.querySelector(".hero");
  if (hero && "IntersectionObserver" in window) {
    new IntersectionObserver(([e]) => document.body.classList.toggle("past-hero", !e.isIntersecting), { rootMargin: "-30% 0px 0px 0px" }).observe(hero);
  }

  picker.addEventListener("click", (e) => {
    const chip = e.target.closest(".chip");
    if (!chip) return;
    const on = !chip.classList.contains("on");
    chip.classList.toggle("on", on);
    chip.setAttribute("aria-pressed", String(on));
    update(on ? chip : null);
  });
})();
