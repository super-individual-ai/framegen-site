// OpenDuckFrame website. Plain script, no build step, no third-party requests.

// One place for every outbound link and the current release.
const SITE = {
  version: "0.1.0",
  links: {
    repo: "https://github.com/Jun-bao/OpenDuckFrame",
    readme: "https://github.com/Jun-bao/OpenDuckFrame#readme",
    releases: "https://github.com/Jun-bao/OpenDuckFrame/releases",
    // GitHub serves the asset named OpenDuckFrame.dmg from the newest release.
    dmg: "https://github.com/Jun-bao/OpenDuckFrame/releases/latest/download/OpenDuckFrame.dmg",
    guide: "https://github.com/Jun-bao/OpenDuckFrame/blob/main/docs/quick-start.md",
    discussions: "https://github.com/Jun-bao/OpenDuckFrame/discussions",
    source: "https://github.com/Jun-bao/OpenDuckFrame#build-from-source",
    issues: "https://github.com/Jun-bao/OpenDuckFrame/issues",
    privacy: "https://github.com/Jun-bao/OpenDuckFrame/blob/main/PRIVACY.md",
    license: "https://github.com/Jun-bao/OpenDuckFrame/blob/main/LICENSE",
  },
  clone: "git clone https://github.com/Jun-bao/OpenDuckFrame",
};

const EN = {
  title: "OpenDuckFrame | Real-time frame generation and upscaling for Mac",
  ariaNav: "Page sections", ariaFoot: "Footer", ariaLang: "Change language", ariaTheme: "Toggle dark mode",
  ariaInstall: "How to install", ariaCopy: "Copy", ariaHero: "OpenDuckFrame Quality Workbench: choose a window, count down, start frame generation",
  ariaPlayer: "OpenDuckFrame film", ariaClose: "Close",
  navWhat: "Features", navUses: "Uses", navDownload: "Download", navFaq: "FAQ",
  h1a: "Real-time frame", h1b: "generation for Mac",
  heroSub: "Turn 24 fps video into 48 fps and upscale low-resolution pictures to your screen. Pick a window and go. Everything runs on your Mac.",
  tabDmg: "App", tabSrc: "Source", cmdDmg: "OpenDuckFrame.dmg · macOS 14+ · Apple silicon",
  star: "Star on GitHub", download: "Download for Mac", heroFine: "Free · Open source (MIT) · No account",
  watch: "Watch the film", heroCaption: "The Quality Workbench: choose a window, wait three seconds, frames are generated. Interface shown as an animation.",
  whatTitle: "What is OpenDuckFrame?",
  whatBody: "A Mac app. Choose a window and it lays an output picture over it: capture, frame-rate detection, frame generation, upscaling and display all happen on your Mac. Nothing is uploaded.",
  readDocs: "Read the quick start",
  f1t: "Detects the real frame rate", f1d: "Counts only frames that actually change, so 24 fps video counts as 24 even on a 120 Hz display.",
  f2t: "2× and 3× frame generation", f2d: "24 → 48, 30 → 60, with RIFE and Apple frame-rate conversion filling in new frames.",
  f3t: "Real-time upscaling", f3d: "Low-resolution pictures are upscaled to your screen as they play, with clearer detail.",
  f4t: "Steps down when the Mac can't keep up", f4d: "Falls back to a lower multiplier instead of stuttering.",
  f5t: "Passes through at the display limit", f5d: "When content × multiplier exceeds the refresh rate, the original is shown and the GPU rests.",
  f6t: "Frame rates at a glance", f6d: "A small overlay shows the content rate, the output rate and the current multiplier.",
  f7t: "Everything stays local", f7d: "Capture and models run on your Mac. No account, and the picture never leaves the machine.",
  insideTitle: "Pick by picture, not by parameter", insideSub: "The technology library says what each frame-generation and upscaling method suits and what it costs. Choose a preset and press Use.",
  insideChip: "Real screenshot", insideCaption: "v0.1.0 · Quality Workbench › Technology library", insideAlt: "OpenDuckFrame technology library",
  usesTitle: "What can you use it on?", usesSub: "Any moving picture in a window. These are the favourites.",
  tabFrames: "Frame generation", tabScale: "Upscaling",
  c1t: "Web video", c1d: "Video sites in the browser, in a normal window or full-page mode.",
  c2t: "Downloaded video", c2d: "Films and series in your player, with pans that no longer judder.",
  c3t: "Animation", c3d: "Low-frame-rate animation with smoother motion.",
  c4t: "Game upscaling", c4d: "Render games at a lower resolution for more frames, then upscale to your screen.",
  c5t: "Windows games streamed to Mac", c5d: "Stream games from a Windows PC and upscale them on the Mac for a sharper picture.",
  c6t: "Low-resolution sources", c6d: "Old films and low-bitrate video, upscaled to your screen.",
  usesNote: "Pictures are illustrations.",
  dlTitle: "Download", dlBody: "Release builds are published on GitHub, together with every earlier version.", allReleases: "All releases",
  reqs: "macOS 14 or later · Mac with Apple silicon", downloadDmg: "Download .dmg",
  s1t: "Drag to Applications", s1d: "Open the downloaded .dmg and drag OpenDuckFrame into Applications. This community build is not Apple notarized; macOS may block its first launch.",
  s2t: "Allow screen recording", s2d: "The first time you choose a window, turn on OpenDuckFrame in System Settings › Privacy & Security › Screen Recording.",
  s3t: "Choose a window and start", s3d: "Pick the source in the Quality Workbench and press Start. After three seconds the output covers the original window.",
  notesTitle: "In this version", limitsTitle: "Known limits",
  n1: "Real-time frame generation and upscaling for windows, displays and video files, with a frame-rate overlay.",
  n2: "Detects the content frame rate, steps down when needed and passes through at the display limit.",
  n3: "Local video playback, subtitles, Quick Look previews and an interface in 17 languages.",
  l1: "At 2×, capture to display takes about 70–80 ms: fine for video, not for competitive games.",
  l2: "macOS full screen (the green button) is not supported yet; use a normal window or full-page mode.",
  faqTitle: "FAQ", faqMore: "Something else?", faqAsk: "Join the discussion",
  q1: "What is OpenDuckFrame?", a1: "A Mac app for real-time frame generation and upscaling. It detects the real frame rate of a window, fills in frames with a local AI model, and can upscale low-resolution pictures as they play.",
  q2: "Which Macs does it run on?", a2: "Macs with Apple silicon on macOS 14 or later. Some engines, such as Apple frame-rate conversion, need macOS 26.",
  q3: "Does it add latency?", a3: "Yes. A new frame can only be made once the next one arrives. At 2× we measure about 70–80 ms from capture to display: fine for video, not for competitive games.",
  q4: "Does it work in full screen?", a4: "Normal windows and full-page video work today. macOS full screen is in development.",
  q5: "Is anything uploaded?", a5: "No. Capture, detection and frame generation all run on your Mac, and there is no account.",
  q6: "How much does it cost?", a6: "Nothing. The source code is on GitHub under the MIT License.",
  q7: "macOS says it can't verify the developer.", a7: "This community build is not Apple notarized. If you trust the download, review its blocked-launch message in System Settings → Privacy & Security and decide whether to allow it. The app does not change system security settings.",
  openTitle: "Built in the open", openBody: "OpenDuckFrame is free and MIT licensed. A star helps more people find it.",
  footReleases: "Releases", footPrivacy: "Privacy", footLicense: "License",
};

const root = document.documentElement;
const store = {
  get(key) { try { return localStorage.getItem(key); } catch (e) { return null; } },
  set(key, value) { try { localStorage.setItem(key, value); } catch (e) {} },
};

// Links and version come from SITE so a release only edits one object.
document.querySelectorAll("[data-link]").forEach((a) => {
  const href = SITE.links[a.dataset.link];
  if (href) a.href = href;
});
document.querySelectorAll("[data-version]").forEach((el) => { el.textContent = SITE.version; });

// Language: Chinese is in the HTML; English replaces it, and switching back restores it.
const ZH = { title: document.title };
document.querySelectorAll("[data-i18n]").forEach((el) => { ZH[el.dataset.i18n] = el.textContent; });
document.querySelectorAll("[data-i18n-aria]").forEach((el) => { ZH[el.dataset.i18nAria] = el.getAttribute("aria-label"); });
document.querySelectorAll("[data-i18n-alt]").forEach((el) => { ZH[el.dataset.i18nAlt] = el.getAttribute("alt"); });
function setLanguage(lang) {
  const dict = lang === "en" ? EN : ZH;
  root.lang = lang === "en" ? "en" : "zh-CN";
  document.title = dict.title;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const value = dict[el.dataset.i18n];
    if (value != null) el.textContent = value;
  });
  document.querySelectorAll("[data-i18n-aria]").forEach((el) => {
    const value = dict[el.dataset.i18nAria];
    if (value != null) el.setAttribute("aria-label", value);
  });
  document.querySelectorAll("[data-i18n-alt]").forEach((el) => {
    const value = dict[el.dataset.i18nAlt];
    if (value != null) el.setAttribute("alt", value);
  });
  document.querySelector(".lang-label").textContent = lang === "en" ? "中文" : "EN";
}
const saved = store.get("odf-lang");
const preferred = saved || ((navigator.language || "").toLowerCase().startsWith("zh") ? "zh" : "en");
setLanguage(preferred);
document.querySelector('[data-action="lang"]').addEventListener("click", () => {
  const next = root.lang === "en" ? "zh" : "en";
  setLanguage(next);
  store.set("odf-lang", next);
});

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
  dialog.showModal();
  film.currentTime = 0;
  film.play().catch(() => {});
});
dialog.addEventListener("close", () => film.pause());
dialog.addEventListener("click", (event) => { if (event.target === dialog) dialog.close(); });

// Respect reduced motion: keep the hero still.
const hero = document.querySelector(".app-frame video");
if (matchMedia("(prefers-reduced-motion: reduce)").matches) { hero.removeAttribute("autoplay"); hero.pause(); }
