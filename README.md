# IPO 打新因子看板

港股 IPO 打新因子研究看板（静态站点）。7 模块 29 因子对首日（D1）/30 日超额（D30）与破发的预测力，可下钻到 214 只个股全量数据。

**线上地址**：https://idddddddd2046.github.io/ipo-factor-dashboard/

## 仓库结构（数据 / 渲染 分离）

| 文件 | 作用 | 谁改 |
|---|---|---|
| `dashboard_data.json` | 看板的**全部数据**（模块、因子统计、个股）。数据快照，冻结口径 | 数据层：ipo-tool 私有仓导出，见 `DATA_SCHEMA.md` |
| `template.html` | 页面**模板**：CSS（`<style>`）+ 交互逻辑（`<script>`）+ 结构。含占位符 `__DATA__` | 渲染层：直接改这里 |
| `build.py` | 把 data 塞进 template，包 doctype 骨架 → `index.html`。纯 Python stdlib | 一般不用改 |
| `index.html` | **构建产物**，GitHub Pages 直接读它。不要手改 | 由 build.py 生成 |
| `DATA_SCHEMA.md` | dashboard_data.json 的字段字典 + 如何重新导出 | 参考 |

## 本地开发

```bash
python build.py            # 重新构建 index.html
# 浏览器打开 index.html 预览（纯静态，无需服务器）
```

改样式/文案/图表/交互 → 改 `template.html` → 跑 `build.py` → 提交 `template.html` **和** `index.html`。

## 部署

推 `main` 分支即自动触发 GitHub Pages 重建（约 1-2 分钟）。验证：
```bash
curl -s https://idddddddd2046.github.io/ipo-factor-dashboard/ | grep -c "你改动里的关键字"
```

## 约束

- **纯静态、单文件**：所有 CSS/JS/数据内联进 index.html，不引任何外部 CDN/字体/图片（Pages 无构建管线）。
- **无框架**：原生 HTML/CSS/JS，不要引入 React/Vue/构建工具。
- **明暗双主题**：CSS 变量在 `:root` / `@media(prefers-color-scheme)` / `[data-theme]` 三处定义，改色只改变量。
- **不改数据口径**：`dashboard_data.json` 是 ipo-tool 冻结报告的快照，渲染层不得篡改数值；要改口径去数据层。
