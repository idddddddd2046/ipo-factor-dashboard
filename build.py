# -*- coding: utf-8 -*-
"""构建看板：冻结数据快照 + template.html -> index.html（纯 stdlib，无外部依赖）。

用法：
    python build.py

原理：template.html 里有 `__DATA__` / `__STRATEGY_DATA__` 两个占位符，
本脚本把 dashboard_data.json 与 strategy_data.json 原样塞进去，再包上 <!doctype> 骨架，输出 index.html。
GitHub Pages 读取的就是仓库根目录的 index.html，push 后自动重建。

修改看板：
    - 只改样式/文案/交互/图表  -> 改 template.html（CSS 在 <style>、逻辑在 <script>），重跑 build.py
    - 改数据/新增因子/新增字段  -> 见 DATA_SCHEMA.md，需在 ipo-tool 私有仓重新导出 dashboard_data.json
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent
data = json.loads((ROOT / "dashboard_data.json").read_text(encoding="utf-8"))
strategy = json.loads((ROOT / "strategy_data.json").read_text(encoding="utf-8"))
template = (ROOT / "template.html").read_text(encoding="utf-8")

body = template.replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
body = body.replace("__STRATEGY_DATA__", json.dumps(strategy, ensure_ascii=False, separators=(",", ":")))
page = (
    '<!doctype html><html lang="zh-Hans"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width, initial-scale=1">'
    '<meta name="description" content="港股 IPO 打新因子看板：29 因子对 D1/D30 与破发的预测力，可下钻个股">'
    + body[: body.index("</style>") + 8]
    + "</head><body>"
    + body[body.index("</style>") + 8 :]
    + "</body></html>"
)
(ROOT / "index.html").write_text(page, encoding="utf-8")
print(f"built index.html {len(page)//1024} KB  (stocks={len(data['stocks'])}, factors={len(data['factors'])})")
