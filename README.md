# OpenDuckFrame 官网

OpenDuckFrame（开源小鸭）的静态产品页：Mac 实时补帧、超分和本地播放。

正式网址：[https://openduckframe.cn/](https://openduckframe.cn/)。

产品源码、构建说明、隐私政策和反馈入口：
[Jun-bao/OpenDuckFrame](https://github.com/Jun-bao/OpenDuckFrame)。

## 本地预览

纯静态页面，不需要构建，也不向第三方发请求。直接用浏览器打开 `index.html`，或运行：

```sh
python3 -m http.server 4178 --bind 127.0.0.1
```

然后访问 `http://127.0.0.1:4178`。

## 发版时要改的地方

运行时链接和版本号在 `main.js` 顶部的 `SITE` 中管理。发版时同时更新 `index.html` 里的默认版本号、JSON-LD 的 `softwareVersion` 和截图说明，保证不开 JavaScript 时的信息也准确。

- `SITE.version`：页面上显示的版本号。
- `SITE.links.dmg`：指向 `releases/latest/download/OpenDuckFrame.dmg`。GitHub 会把它解析到最新 Release 里名为 `OpenDuckFrame.dmg` 的附件。只要每次发版都带上这个固定文件名的附件，就不用改链接。产品仓库里的 `Scripts/community_release.py` 会自动上传它。
- 当前提供 0.3.0 社区版（未经过 Apple 公证），支持签名验证的应用内更新。

## 内容与资源

- `index.html`：页面结构和默认中文内容。
- `main.js`：链接、版本、主题和播放器。
- `translations/en.json`：英文文案；修改首页或翻译后运行 `node scripts/build-en.mjs` 更新 `en/index.html`，生成后即可静态发布，无需服务器构建。
- `guides/` 和 `en/guides/`：中英文帧生成与实时补帧教程、视频超分教程、补帧与超分对照。核心结论与步骤写在 HTML 正文中，附项目文档依据。
- `styles.css`：浅色和深色主题，桌面端和移动端样式。
- `assets/openduckframe-library.webp`：v0.1.0 技术库实机截图。
- `assets/media/hero.mp4`：首屏示意动画；`assets/media/promo-web-v3.mp4`：网页使用的 52 秒宣传片；`promo-v2.mp4` 保留为原始版本。
- `assets/media/*.webp`：网页使用的场景卡片配图，均为示意图；原始 JPG 保留。
- `assets/icon.png`、`favicon.png`、`og.jpg`：图标和分享卡片。

## 搜索与 AI 搜索

- `index.html` 的标题、摘要、规范网址和绝对分享图片地址统一使用正式 HTTPS 域名。
- JSON-LD 描述网站、网页及软件的身份、系统要求、免费价格、MIT 许可与官方源码。不填写虚构评分，也不保证软件富媒体搜索结果。
- 首页“开源构建”提供中英文名称、官网域名、唯一源代码仓库、版本发布与反馈入口，便于读者及搜索系统核对项目身份。结构化数据将首页的主要对象明确为 OpenDuckFrame 应用，指南也在本页标记中写出产品名称和官网地址。
- 核心产品介绍、安装要求、使用步骤和 FAQ 都在原始 HTML 中，抓取不依赖 JavaScript。中文首页 `/`、英文首页 `/en/` 有独立规范网址、静态正文与双向 `hreflang`。语言按钮使用普通链接，不按浏览器语言或旧偏好自动改写页面。
- 三篇指南均有独立中英文版本、标题、摘要、规范网址、文章和面包屑结构化数据；从对应语言首页和彼此之间直接链接，通过双向 `hreflang` 关联。只有实际更新内容时才更新站点地图的 `lastmod`。
- `robots.txt` 允许搜索引擎和搜索用途的 AI 爬虫访问，并公布 `sitemap.xml`；抓取服务还必须能通过 Cloudflare 和源站访问。
- GEO 依靠可核对的产品事实、直接回答问题的正文与源码文档链接；不把倍率、演示动画或单一设备测量写成普遍效果承诺。
- 上线后可将站点地图提交到搜索引擎站长平台。完成技术设置或提交网址，都不等于已经收录、获得排名或被 AI 推荐。
- 首页中的 Google 与 Bing 公开验证标记用于保持当前站点所有权，请勿移除。验证标记可以公开，不是登录令牌或提交 API 密钥。
- `/favicon.ico` 与 `/favicon.png` 沿用现有图标，兼容请求根目录图标的客户端；页面同时声明 64 × 64 PNG 图标。
- 搜索表现使用站长平台的曝光、点击、查询词和索引数据判断；GEO 另外观察品牌是否被提及、是否推荐、是否引用本站，不能用提交成功代替效果。

## 发布

生产服务应只提供官网公开文件，不要把含 `.git` 的整个仓库用作公网服务目录。需发布 `index.html`、`en/`、`guides/`、`main.js`、`styles.css`、`assets/`、`favicon.ico`、`favicon.png`、`robots.txt`、`sitemap.xml`，以及站长平台要求的公开验证文件。`scripts/` 与 `translations/` 属于源码，不需要发布。

本机运行路径、后台服务配置和隧道令牌属于部署环境，保存在仓库外；令牌不得放入公开目录或提交 Git。

`server.py` 用于生产服务，启动时必须显式传入只含公开文件的 `--directory`。它把 `www` 与 `index.html` 别名合并到正式 HTTPS 网址，保留路径和查询参数；中文、英文与三篇指南仍各有独立规范地址。服务脚本不放入公开文件目录。

### 完整发布包与回退

先完成 `node scripts/build-en.mjs`、`python3 scripts/check-performance.py` 和 `git diff --check`，核对并提交本轮改动。然后从已提交版本生成一个全新的发布目录：

```sh
python3 scripts/stage-release.py --output /absolute/private/runtime/releases/release-id
```

`--output` 必须在源码目录以外且尚不存在。`HEAD` 模式拒绝未提交的工作区；如需从历史提交回退，可显式使用 `--ref <commit>`。脚本直接读取 Git 提交中的文件，不把当前工作区或机器私有配置混进发布物。

发布包包含 `site/` 下的公开文件，以及公开目录之外的 `server.py`、`performance_http.py`、`feedback_service.py` 和协议检查脚本。脚本先校验白名单、八个站点地图页面、服务模块导入及 HTTP 回归测试，全部通过才写出 `release-manifest.json`（提交、文件 SHA-256 和检查结果）。含 `INCOMPLETE` 的目录不得部署。脚本本身只准备发布包，不切换服务、不读取反馈配置或隧道凭据。

切换时先保留现有 HTTP 服务配置。将服务的程序路径、`--directory` 和工作目录一并指向同一个已验证发布目录；`--feedback-config` 继续使用公开目录外的原有私有配置。仅重载官网 HTTP 服务。不要边覆盖单个服务文件边重启，否则可能出现主文件已更新、依赖模块尚未到位的启动失败。

切换后检查源站与正式域名的八个 SEO 页面、反馈页的 `no-store`、视频 Range、规范重定向和服务启动日志，并将运行中的程序参数与发布清单对照。保留切换前的发布目录和服务配置；失败时恢复该配置并重载 HTTP 服务，再验证同一组路径。Cloudflare 缓存更新与源站切换分别核对，源站成功不代表边缘已经更新。

### 网页性能

- `performance_http.py` 与 `server.py` 一起放在服务目录，不放进公开目录。它为 MP4 提供字节范围读取，让未命中缓存的视频也能按需播放和拖动进度。运行 `python3 scripts/check-performance.py` 检查范围响应、缓存策略与规范重定向。
- 中文、英文首页与指南允许 Cloudflare 缓存 5 分钟，浏览器每次重新验证；Cloudflare 的 Cache Rule 只对正式域名的这些公开路径及 GET/HEAD 生效，并遵循源站缓存标头。反馈表单、API 和错误响应不缓存。修改页面后，最多约 5 分钟刷新边缘缓存；需要立即更新时，在 Cloudflare 按 URL 清除对应页面。
- 静态资源在源站声明浏览器缓存 1 小时、边缘缓存 1 天（Cloudflare 现有浏览器 TTL 设置可能延长客户端缓存）；替换资源时更新 URL。首页脚本使用查询版本号，图片和宣传片使用独立文件名，避免新 HTML 误用旧缓存。
- 网页宣传片使用 `assets/media/promo-web-v3.mp4`（1080p、60 fps、52 秒），保留原始 `promo-v2.mp4`。宣传片和封面在点击观看时才加载，页面下方的场景图按需加载；新增 WebP 文件需随页面发布。

## 用户反馈

`feedback/` 是中英文反馈表单，沿用产品字体与颜色，按提供的参考图排布。支持 2000 字问题描述、选填的联系邮箱、一张不超过 5 MB 的 PNG/JPEG/WebP 截图，以及图片粘贴、拖入、预览和移除。仅点击发送时提交；失败会保留当前填写内容。

`server.py` 的 `POST /api/feedback` 通过 `feedback_service.py` 调用已登录的 `lark-cli` 用户身份，写入开发者私有的飞书多维表格，并把截图加入附件字段。应用通过不会随页面请求发送的网址片段传入版本信息，仅在点击发送时提交。启动时传 `--feedback-config` 指向公开目录以外的配置文件，其中只指定 `base_token`、`table_id` 和 `lark_cli` 可执行文件；不把飞书登录信息、收集表坐标或部署路径写入浏览器代码。服务器限制正文、图片大小和提交频率，不在反馈表格保存来源地址。

部署时还需将 `feedback/` 放入公开目录，将 `feedback_service.py` 与 `server.py` 放在服务目录，并在服务启动参数中提供私有配置文件。隐私说明位于 `/feedback/privacy/`。如果没有配置收集端，接口返回不可用，不能显示发送成功。
