# IPO 打新因子看板

港股 IPO 打新因子研究看板（静态站点）。7 模块 29 个基础因子对首日（D1）及
“D1 收盘→D30 后续超额”的历史关联，可下钻到 214 只个股全量数据；另有现行引擎新增的
基石机构份额证据、方法稳健性、D180/D365 长期核验和前瞻双跑进度。页面同时展示冻结的 v2 策略对决和固定卡档位试算；
不把相关性写成因果或个股建议。

**线上地址**：https://idddddddd2046.github.io/ipo-factor-dashboard/

## 仓库结构（数据 / 渲染 分离）

| 文件 | 作用 | 谁改 |
|---|---|---|
| `dashboard_data.json` | 模块、因子统计与个股研究数据。只读快照，冻结口径 | 数据层：ipo-tool 私有仓导出，见 `DATA_SCHEMA.md` |
| `strategy_data.json` | v2 冻结卡边界与策略对决结果的**只读快照** | 数据层：来自 ipo-tool 注册协议下的冻结对决报告 |
| `forward_status.json` | F4 前瞻样本进度、现行基线版本、三类资产日期与新鲜度策略的**只读快照** | 数据层：来自 ipo-tool 双跑周报、版本补充说明与新鲜度审计 |
| `long_horizon_data.json` | 2024–2025 专家规则长期复演、长期因子池及关系/锁定证据补齐进度的**只读快照** | 数据层：来自 ipo-tool 三份 2026-07-23 审计报告 |
| `template.html` | 页面**模板**：CSS（`<style>`）+ 交互逻辑（`<script>`）+ 结构。含三份只读数据占位符 | 渲染层：直接改这里 |
| `build.py` | 校验三份快照的日期/计数契约，再塞进 template → `index.html`。纯 Python stdlib | 数据契约变化时才改 |
| `test_build.py` | 构建契约回归：拒绝越过 Gate 的计数、来源日期错配和模板漏占位 | 渲染层自检 |
| `index.html` | **构建产物**，GitHub Pages 直接读它。不要手改 | 由 build.py 生成 |
| `DATA_SCHEMA.md` | dashboard_data.json 的字段字典 + 如何重新导出 | 参考 |

## 本地开发

```bash
python -m unittest -v test_build.py
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
- **不改数据口径**：`dashboard_data.json` 与 `strategy_data.json` 都是 ipo-tool 冻结报告的快照，渲染层不得篡改统计数值；要改口径去数据层。
- **浏览器只查表**：固定卡试算只应用已导出的方向、边界、档分和缺失归一规则；所有 IC、类别组、基石证据与前瞻进度均来自冻结导出，不在浏览器重估。
- **新鲜度不等于样本增长**：页面只按 `forward_status.json` 的周报节奏动态提示“正常等待/更新延迟”，不读取生产日志，也不会自行增加前瞻样本数。
