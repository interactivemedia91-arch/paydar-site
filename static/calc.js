/* The cost calculator: ticking a plan updates the totals, and the address keeps the list so it can be
   shared (#netflix:standard-monthly,spotify:individual-monthly). The page is complete without it: the
   server renders four picks and their totals. */
(() => {
  const list = document.querySelector(".calc-list");
  const panel = document.querySelector(".calc-total");
  if (!list || !panel) return;

  const boxes = [...list.querySelectorAll('input[type="checkbox"]')];
  const year = panel.dataset.year;
  const out = (name) => panel.querySelector(`[data-total="${name}"]`);
  const live = panel.querySelector(".calc-live");
  const share = panel.querySelector(".calc-share");
  const money = (x) => "$" + x.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const short = (x) => "$" + (Math.round(x * 100) % 100 ? x.toFixed(2) : Math.round(x).toString());

  // A shared list replaces the default picks (when at least one of its plans still exists).
  const wanted = new Set(decodeURIComponent(location.hash.slice(1)).split(",").filter(Boolean));
  if (boxes.some((b) => wanted.has(b.value))) boxes.forEach((b) => { b.checked = wanted.has(b.value); });

  const update = (fromUser) => {
    const on = boxes.filter((b) => b.checked);
    const month = on.reduce((t, b) => t + Number(b.dataset.monthly), 0);
    const added = on.reduce((t, b) => t + Number(b.dataset.added), 0);
    out("month").textContent = money(month);
    out("year").textContent = money(month * 12);
    out("added").textContent = !on.length ? "Tick what you pay for to see your total."
      : added > 0.004 ? `${year}'s price increases add ${short(added)} a year to these.`
      : `None of these went up in ${year}.`;
    if (fromUser) {
      live.textContent = `${money(month)} a month, ${money(month * 12)} a year`;
      history.replaceState(null, "", on.length ? "#" + on.map((b) => b.value).join(",") : location.pathname);
    }
  };
  list.addEventListener("change", (e) => { if (e.target.matches('input[type="checkbox"]')) update(true); });
  update(false);

  // Sharing: the system sheet on phones, else a copied link.
  if (navigator.share || navigator.clipboard) {
    share.hidden = false;
    share.addEventListener("click", async () => {
      const url = location.href;
      try {
        if (navigator.share && matchMedia("(pointer: coarse)").matches) {
          await navigator.share({ title: "What my subscriptions cost", url });
        } else {
          await navigator.clipboard.writeText(url);
          share.textContent = "Link copied";
          setTimeout(() => { share.textContent = "Copy link to this list"; }, 2000);
        }
      } catch { /* dismissed */ }
    });
  }
})();
