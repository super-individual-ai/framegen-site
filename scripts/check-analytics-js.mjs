// Exercise event classification and privacy without making network requests.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

const source = readFileSync(new URL("../analytics.js", import.meta.url), "utf8");
function setup({ dnt = "", gpc = false, host = "openduckframe.cn", enabled = true, query = "" } = {}) {
  const calls = [], handlers = {}, scripts = [];
  const location = new URL(`https://${host}/guides/rife-mac/${query}`);
  const document = {
    documentElement: { lang: "zh-CN" },
    querySelector: selector => selector === "script[data-odf-analytics]" ? { dataset: {} } : { href: "https://openduckframe.cn/guides/rife-mac/" },
    addEventListener: (name, callback) => { handlers[name] = callback; },
    createElement: () => ({ dataset: {} }),
    head: { append: script => scripts.push(script) },
  };
  const window = enabled ? { umami: { track: (...args) => { calls.push(args); return Promise.resolve(); } } } : {};
  vm.runInNewContext(source, { document, window, location, navigator: { doNotTrack: dnt, globalPrivacyControl: gpc }, URL, URLSearchParams });
  const click = href => {
    const link = { href, closest: () => null };
    handlers.click?.({ target: { closest: () => link } });
  };
  return { calls, handlers, scripts, window, click };
}

const test = setup({ query: "?email=synthetic-secret&utm_source=google&utm_campaign=unapproved#private" });
for (let i = 0; i < 10; i++) test.click("https://github.com/Jun-bao/OpenDuckFrame/releases/latest/download/OpenDuckFrame.dmg");
assert.equal(test.calls.length, 10);
assert.ok(test.calls.every(([name, data]) => name === "download_click" && data.position === "guide" && data.release === "unknown"));
test.click("https://openduckframe.cn/#download");
test.click("https://github.com/Jun-bao/OpenDuckFrame/releases");
assert.equal(test.calls[10][0], "download_section_click");
assert.equal(test.calls[11][0], "github_release_click");
const sanitized = test.window.odfAnalyticsBeforeSend("event", { referrer: "https://search.example/private?q=secret", title: "Public page" });
assert.equal(sanitized.url, "/guides/rife-mac/?utm_source=google");
assert.equal(sanitized.referrer, "https://search.example");
assert.equal(test.window.odfAnalyticsBeforeSend("identify", {}), null);
assert.equal(setup({ dnt: "1" }).scripts.length, 0);
assert.equal(setup({ gpc: true }).scripts.length, 0);
assert.equal(setup({ host: "localhost" }).scripts.length, 0);
const blocked = setup({ enabled: false });
assert.doesNotThrow(() => blocked.click("https://github.com/Jun-bao/OpenDuckFrame/releases/latest/download/OpenDuckFrame.dmg"));
console.log("Analytics JS passed: exact event count, link categories, URL privacy, DNT/GPC, local exclusion and blocked-tracker fallback");
