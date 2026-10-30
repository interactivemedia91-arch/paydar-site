/* The motion layer. Smooth scrolling everywhere (Lenis); on the homepage, GSAP adds one entrance per
   section (heading, then text, then picture, once) and a slow drift on the app screens. The hero's
   arrival is CSS (site.css), so it starts with the first paint. Content is visible by default:
   nothing hides unless this script runs, and Reduce Motion skips all of it, GSAP's download included
   (the field's colour change and the counted total stay instant). */
(() => {
  // iOS only paints :active (every control's press feedback) while the page listens for touches.
  document.addEventListener("touchstart", () => {}, { passive: true });
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const anchors = { duration: .6 }; // a link the visitor clicked lands quickly
  const smooth = () => window.Lenis && new Lenis({ anchors, autoRaf: true });
  if (!document.body.classList.contains("page-home")) return void smooth();

  const load = (src) => new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = src;
    script.onload = resolve;
    script.onerror = reject;
    document.head.append(script);
  });

  const start = () => {
    gsap.registerPlugin(ScrollTrigger);
    if (window.Lenis) {
      const lenis = new Lenis({ anchors, autoRaf: false });
      lenis.on("scroll", ScrollTrigger.update);
      gsap.ticker.add((time) => lenis.raf(time * 1000));
      gsap.ticker.lagSmoothing(0);
    }
    const ease = "expo.out";

    // Each later section: heading, then its text, then its picture. A section already on screen, or
    // the one a link landed on, stays as it is.
    const landed = document.getElementById(location.hash.slice(1));
    document.querySelectorAll(".page-home main > section + section").forEach((section) => {
      if (section.getBoundingClientRect().top < innerHeight * .82 || landed && section.contains(landed)) return;
      const parts = [...section.querySelectorAll("[data-rv], :scope > .pill, :scope > .facts")]
        .sort((a, b) => (Number(a.dataset.rv) || 3) - (Number(b.dataset.rv) || 3));
      if (!parts.length) return;
      gsap.from(parts, {
        y: 28, opacity: 0, duration: .8, ease, stagger: .08, clearProps: "transform,opacity",
        scrollTrigger: { trigger: section, start: "top 82%", once: true },
      });
    });

    // The app screens drift at slightly different speeds as they pass, each with its caption; only
    // while they sit side by side, and undone when the window narrows.
    gsap.matchMedia().add("(min-width: 761px)", () => {
      gsap.utils.toArray(".screen-row .screen").forEach((screen, i) => {
        gsap.fromTo(screen, { yPercent: [4, -2, 6][i] ?? 0 }, {
          yPercent: [-4, 2, -6][i] ?? 0, ease: "none",
          scrollTrigger: { trigger: ".screen-row", start: "top bottom", end: "bottom top", scrub: true },
        });
      });
    });
  };

  load("/gsap.min.js").then(() => load("/ScrollTrigger.min.js")).then(start, smooth);
})();
