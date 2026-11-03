# 帧生成产品官网

Mac 实时补帧应用的官网单页。产品名和 logo 待定，页面里先留白。

纯静态页面，不需要构建：直接用浏览器打开 `index.html`。

## 怎么改产品名和 logo

产品名和 logo 只改 `main.js` 顶部这一处：

```js
const BRAND = { name: null, logo: null };
```

- `name` 写成字符串后，顶栏、页脚、正文和标签页标题里的 `〔产品名〕` 会一起换成它。保持 `null` 时显示占位；切换中英文也不会翻译这几个字。
- `logo` 写成站内 SVG 的路径，例如 `assets/logo.svg`。顶栏和页脚的虚线方块会换成这张图。保持 `null` 时仍是占位。图片请只用 SVG。
