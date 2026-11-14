import { readFile, writeFile, mkdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";

// The Chinese homepage and this translation dictionary are the source of truth.
const base = new URL("../", import.meta.url);
const translations = JSON.parse(await readFile(new URL("translations/en.json", base), "utf8"));
const escape = (value) => value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
let html = await readFile(new URL("index.html", base), "utf8");

html = html.replace(/<([a-z][\w-]*)([^>]*\bdata-i18n="([^"]+)"[^>]*)>[\s\S]*?<\/\1>/g, (element, tag, attrs, key) => {
  if (!(key in translations)) throw new Error(`Missing English text: ${key}`);
  return `<${tag}${attrs}>${escape(translations[key])}</${tag}>`;
});
html = html.replace(/<([a-z][\w-]*)([^>]*\bdata-i18n-(aria|alt)="([^"]+)"[^>]*)>/g, (element, tag, attrs, kind, key) => {
  if (!(key in translations)) throw new Error(`Missing English attribute: ${key}`);
  const attr = kind === "aria" ? "aria-label" : "alt";
  return `<${tag}${attrs.replace(new RegExp(`${attr}="[^"]*"`), `${attr}="${escape(translations[key])}"`)}>`;
});
html = html
  .replace('<html lang="zh-CN">', '<html lang="en">')
  .replace(/<title>[^<]*<\/title>/, `<title>${escape(translations.title)}</title>`)
  .replace(/(<meta (?:name|property)="(?:description|og:description|twitter:description)" content=")[^"]*(">)/g, `$1${escape(translations.description)}$2`)
  .replace(/(<meta (?:property|name)="(?:og:title|twitter:title)" content=")[^"]*(">)/g, `$1${escape(translations.title)}$2`)
  .replace('<link rel="canonical" href="https://openduckframe.cn/">', '<link rel="canonical" href="https://openduckframe.cn/en/">')
  .replace('<meta property="og:url" content="https://openduckframe.cn/">', '<meta property="og:url" content="https://openduckframe.cn/en/">')
  .replace('<meta property="og:locale" content="zh_CN">', '<meta property="og:locale" content="en_US">')
  .replace('<meta property="og:locale:alternate" content="en_US">', '<meta property="og:locale:alternate" content="zh_CN">')
  .replace('href="/en/" data-language-switch', 'href="/" data-language-switch')
  .replace('<span class="lang-label">EN</span>', '<span class="lang-label">中文</span>')
  .replace(/<a href="\/guides\/([^"]+)" hreflang="zh-CN"/g, '<a href="/en/guides/$1" hreflang="en"')
  .replace(/\b(href|src|poster)="(?![a-z]+:|\/|#)([^"]+)"/g, '$1="/$2"');

html = html.replace(/(<script type="application\/ld\+json" id="site-schema">)([\s\S]*?)(<\/script>)/, (_, open, json, close) => {
  const data = JSON.parse(json);
  for (const node of data["@graph"]) {
    if (node["@type"] === "WebPage") {
      Object.assign(node, { "@id": "https://openduckframe.cn/en/#webpage", url: "https://openduckframe.cn/en/", name: translations.title, description: translations.description, inLanguage: "en" });
    }
    if (node["@type"] === "SoftwareApplication") {
      node.description = translations.description;
      node.softwareRequirements = "Apple interpolation and super resolution require supported macOS versions, hardware and input.";
      node.featureList = ["Real-time frame generation (video interpolation)", "Real-time upscaling", "Window, display and local video inputs", "Local video playback and subtitles"];
    }
  }
  return `${open}\n${JSON.stringify(data, null, 2)}\n${close}`;
});

await mkdir(new URL("en/", base), { recursive: true });
await writeFile(new URL("en/index.html", base), html);
console.log(`Built ${fileURLToPath(new URL("en/index.html", base))}`);
