// OpenDuckFrame website. Plain script, no build step, no third-party requests.

// One place for every outbound link and the current release.
const SITE = {
  version: "0.3.0",
  links: {
    repo: "https://github.com/Jun-bao/OpenDuckFrame",
    readme: "https://github.com/Jun-bao/OpenDuckFrame#readme",
    releases: "https://github.com/Jun-bao/OpenDuckFrame/releases",
    // GitHub serves the asset named OpenDuckFrame.dmg from the newest release.
    dmg: "https://github.com/Jun-bao/OpenDuckFrame/releases/latest/download/OpenDuckFrame.dmg",
    guide: "https://github.com/Jun-bao/OpenDuckFrame/blob/v0.3.0/docs/quick-start.md",
    features: "https://github.com/Jun-bao/OpenDuckFrame/blob/v0.3.0/docs/features.md",
    discussions: "https://github.com/Jun-bao/OpenDuckFrame/discussions",
    source: "https://github.com/Jun-bao/OpenDuckFrame#build-from-source",
    issues: "https://github.com/Jun-bao/OpenDuckFrame/issues",
    feedback: document.documentElement.lang === "en" ? "/feedback/?lang=en" : "/feedback/",
    privacy: "https://github.com/Jun-bao/OpenDuckFrame/blob/v0.3.0/PRIVACY.md",
    license: "https://github.com/Jun-bao/OpenDuckFrame/blob/v0.3.0/LICENSE",
  },
  clone: "git clone https://github.com/Jun-bao/OpenDuckFrame",
};

const root = document.documentElement;
const store = {
  get(key) { try { return localStorage.getItem(key); } catch (e) { return null; } },
  set(key, value) { try { localStorage.setItem(key, value); } catch (e) {} },
};

// Keep the static HTML and structured data in sync when updating a release.
document.querySelectorAll("[data-link]").forEach((a) => {
  const href = SITE.links[a.dataset.link];
  if (href) a.href = href;
});
document.querySelectorAll("[data-version]").forEach((el) => { el.textContent = SITE.version; });

// Language versions have separate static URLs; the header link works without JavaScript.

// Theme: follows the system until the visitor chooses.
document.querySelector('[data-action="theme"]').addEventListener("click", () => {
  const current = root.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  const next = current === "dark" ? "light" : "dark";
  root.dataset.theme = next;
  store.set("odf-theme", next);
});

// Install box: app download or source clone.
const tabs = document.querySelectorAll(".cmd-tabs [data-tab]");
tabs.forEach((tab) => tab.addEventListener("click", () => {
  tabs.forEach((t) => t.setAttribute("aria-selected", String(t === tab)));
  document.querySelectorAll("[data-cmd]").forEach((line) => { line.hidden = line.dataset.cmd !== tab.dataset.tab; });
}));
const copyBtn = document.querySelector('[data-action="copy"]');
copyBtn.addEventListener("click", async () => {
  const source = document.querySelector('.cmd-tabs [aria-selected="true"]').dataset.tab === "src";
  const text = source ? SITE.clone : SITE.links.dmg;
  try { await navigator.clipboard.writeText(text); } catch (e) { return; }
  copyBtn.classList.add("done");
  setTimeout(() => copyBtn.classList.remove("done"), 1400);
});

// Uses gallery: frame generation or upscaling.
const useTabs = document.querySelectorAll("[data-uses]");
useTabs.forEach((tab, index) => tab.addEventListener("click", () => {
  useTabs.forEach((t) => t.setAttribute("aria-selected", String(t === tab)));
  document.querySelectorAll("[data-panel]").forEach((panel) => { panel.hidden = panel.dataset.panel !== tab.dataset.uses; });
  document.querySelector("[data-pager]").textContent = String(index + 1);
}));

// Header hairline once the page scrolls.
const header = document.querySelector("header.top");
const onScroll = () => header.classList.toggle("scrolled", window.scrollY > 8);
addEventListener("scroll", onScroll, { passive: true });
onScroll();

// Film player.
const dialog = document.querySelector("dialog.player");
const film = dialog.querySelector("video");
document.querySelector('[data-action="watch"]').addEventListener("click", () => {
  if (!film.getAttribute("src")) {
    film.poster = film.dataset.poster;
    film.src = film.dataset.src;
  }
  dialog.showModal();
  film.currentTime = 0;
  film.play().catch(() => {});
});
dialog.addEventListener("close", () => film.pause());
dialog.addEventListener("click", (event) => { if (event.target === dialog) dialog.close(); });

// Respect reduced motion: keep the hero still.
const hero = document.querySelector(".app-frame video");
if (matchMedia("(prefers-reduced-motion: reduce)").matches) { hero.removeAttribute("autoplay"); hero.pause(); }
