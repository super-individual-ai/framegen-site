# OpenDuckFrame 官网

OpenDuckFrame（开源小鸭）的静态产品页：Mac 实时补帧、超分和本地播放。

产品源码、构建说明、隐私政策和反馈入口：
[Jun-bao/OpenDuckFrame](https://github.com/Jun-bao/OpenDuckFrame)。

## 本地预览

纯静态页面，不需要构建，也不向第三方发请求。直接用浏览器打开 `index.html`，或运行：

```sh
python3 -m http.server 4178 --bind 127.0.0.1
```

然后访问 `http://127.0.0.1:4178`。

## 发版时要改的地方

链接和版本号只在 `main.js` 顶部的 `SITE` 里改。

- `SITE.version`：页面上显示的版本号。
- `SITE.links.dmg`：指向 `releases/latest/download/OpenDuckFrame.dmg`。GitHub 会把它解析到最新 Release 里名为 `OpenDuckFrame.dmg` 的附件。只要每次发版都带上这个固定文件名的附件，就不用改链接。产品仓库里的 `Scripts/publish_github_release.sh` 会自动上传它。
- 第一个 Release 发出来之前，“下载 Mac 版”按钮会返回 404。

## 内容与资源

- `index.html`：页面结构和默认中文内容。
- `main.js`：链接、版本、英文文案、主题和语言切换、播放器。
- `styles.css`：浅色和深色主题，桌面端和移动端样式。
- `assets/openduckframe-library.webp`：v0.1.0 技术库实机截图。
- `assets/media/hero.mp4`、`promo.mp4`：首屏动画和宣传片，由程序生成，页面上标为示意。
- `assets/media/*.jpg`：场景卡片配图，均为示意图。
- `assets/icon.png`、`favicon.png`、`og.jpg`：图标和分享卡片。
