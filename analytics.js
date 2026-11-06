// Anonymous website analytics. Never delay navigation or read feedback fields.
(() => {
  const optedOut = navigator.doNotTrack === "1" || navigator.globalPrivacyControl === true;
  const local = ["localhost", "127.0.0.1"].includes(location.hostname);
  const config = document.querySelector("script[data-odf-analytics]");
  if (!config || optedOut || location.pathname.startsWith("/feedback") || (local && !config.dataset.testWebsiteId)) return;

  const utm = {
    utm_source: ["google", "bing", "baidu", "chatgpt", "perplexity", "gemini", "github", "bilibili", "douyin", "xiaohongshu", "newsletter"],
    utm_medium: ["organic", "cpc", "social", "referral", "email"],
    utm_campaign: ["release030", "seo20261106"],
  };
  const path = document.querySelector('link[rel="canonical"]')?.href
    ? new URL(document.querySelector('link[rel="canonical"]').href).pathname
    : location.pathname;
  window.odfAnalyticsBeforeSend = (type, payload) => {
    if (type !== "event") return null;
    const url = new URL(location.href);
    const query = new URLSearchParams();
    for (const [key, values] of Object.entries(utm)) {
      const value = url.searchParams.get(key);
      if (values.includes(value)) query.set(key, value);
    }
    let referrer = "";
    try {
      const ref = new URL(payload.referrer || "", location.origin);
      if (payload.referrer) referrer = ref.origin === location.origin ? ref.pathname : ref.origin;
    } catch (error) { /* No referrer is an honest unknown. */ }
    return { ...payload, url: path + (query.size ? `?${query}` : ""), referrer };
  };

  const track = (name, element, extra = {}) => {
    const position = element?.closest("#top") ? "hero" : element?.closest("#download") ? "download" : element?.closest("footer") ? "footer" : path.includes("/guides/") ? "guide" : "nav";
    if (window.umami) {
      window.umami.track(name, { page_path: path, lang: document.documentElement.lang, position, ...extra }).catch(() => {});
    }
  };
  document.addEventListener("click", event => {
    const link = event.target.closest?.("a[href]");
    if (!link) return;
    const target = new URL(link.href, location.href);
    if (target.hostname === "github.com" && target.pathname === "/Jun-bao/OpenDuckFrame/releases/latest/download/OpenDuckFrame.dmg") {
      track("download_click", link, { target: "dmg", release: "unknown" });
    } else if (target.hostname === "github.com" && /^\/Jun-bao\/OpenDuckFrame\/releases(?:\/|$)/.test(target.pathname)) {
      track("github_release_click", link);
    } else if (target.origin === location.origin && target.hash === "#download") {
      track("download_section_click", link);
    }
  });
  document.addEventListener("odf:download-link-copied", event => track("download_link_copy", event.target));

  const script = document.createElement("script");
  script.src = "/stats/script.js?v=3.4.1";
  script.defer = true;
  script.dataset.websiteId = config.dataset.testWebsiteId || "5cb912d0-d735-4c0f-9ae1-c06a1c2e93ea";
  script.dataset.domains = config.dataset.testWebsiteId ? "localhost,127.0.0.1" : "openduckframe.cn";
  script.dataset.beforeSend = "odfAnalyticsBeforeSend";
  script.dataset.excludeHash = "true";
  script.dataset.doNotTrack = "true";
  document.head.append(script);
})();
