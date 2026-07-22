# -*- coding: utf-8 -*-
"""构建看板：冻结数据快照 + template.html -> index.html（纯 stdlib，无外部依赖）。

用法：
    python build.py

原理：template.html 里有四个 JSON 占位符，
本脚本把 dashboard_data.json、strategy_data.json、forward_status.json 与
long_horizon_data.json 原样塞进去，
再包上 <!doctype> 骨架，输出 index.html。
GitHub Pages 读取的就是仓库根目录的 index.html，push 后自动重建。

修改看板：
    - 只改样式/文案/交互/图表  -> 改 template.html（CSS 在 <style>、逻辑在 <script>），重跑 build.py
    - 改数据/新增因子/新增字段  -> 见 DATA_SCHEMA.md，需在 ipo-tool 私有仓重新导出 dashboard_data.json
"""
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
PLACEHOLDERS = (
    "__DATA__",
    "__STRATEGY_DATA__",
    "__FORWARD_STATUS__",
    "__LONG_HORIZON_DATA__",
)


def validate_inputs(
    data: dict, strategy: dict, forward_status: dict, long_horizon: dict, template: str
) -> None:
    """阻止来源日期、前瞻计数或模板占位符失配后仍发布。"""
    for placeholder in PLACEHOLDERS:
        if template.count(placeholder) != 1:
            raise ValueError(f"{placeholder} 必须在模板中且只能出现一次")

    forward_n = forward_status.get("forward_n")
    target_n = forward_status.get("target_n")
    if not isinstance(forward_n, int) or not isinstance(target_n, int):
        raise ValueError("forward_n/target_n 必须为整数")
    if forward_n < 0 or target_n <= 0 or forward_n > target_n:
        raise ValueError("前瞻样本进度不合法")

    as_of = date.fromisoformat(forward_status["as_of"])
    asset_dates = forward_status["asset_dates"]
    factor_date = date.fromisoformat(asset_dates["factor_research"])
    strategy_date = date.fromisoformat(asset_dates["strategy_duel"])
    if factor_date != date.fromisoformat(data["meta"]["p2_hardening"]["date"]):
        raise ValueError("factor_research 日期与 dashboard_data 最新证据日期不一致")
    if strategy_date != date.fromisoformat(strategy["generated_at"][:10]):
        raise ValueError("strategy_duel 日期与 strategy_data 生成日期不一致")
    if max(factor_date, strategy_date) > as_of:
        raise ValueError("资产日期不能晚于公开状态快照日期")

    long_date = date.fromisoformat(long_horizon["as_of"])
    if long_date < date(2026, 7, 22):
        raise ValueError("长期核验快照早于 D180/D365 审计截止日")
    if long_horizon.get("long_factor_pool", {}).get("production_change") is not False:
        raise ValueError("长期因子池不得越过生产 Gate")
    scope = long_horizon.get("scope", {})
    if scope.get("rows") != 181 or scope.get("d180_mature") != 141:
        raise ValueError("长期核验样本契约不一致")
    backfill = long_horizon.get("evidence_backfill", {})
    if backfill.get("database_writes") is not False:
        raise ValueError("关系/锁定补齐必须保持 dry-run")

    report_match = re.search(r"(\d{4}-\d{2}-\d{2})", forward_status["source_report"])
    if not report_match or date.fromisoformat(report_match.group(1)) > as_of:
        raise ValueError("source_report 日期缺失或晚于公开状态快照")

    policy = forward_status["freshness_policy"]
    if policy.get("timezone") != "Asia/Singapore":
        raise ValueError("公开页新鲜度时区必须为 Asia/Singapore")
    if int(policy.get("grace_hours", -1)) < 0 or int(policy.get("snapshot_warn_days", 0)) <= 0:
        raise ValueError("新鲜度宽限策略不合法")


def main() -> None:
    data = json.loads((ROOT / "dashboard_data.json").read_text(encoding="utf-8"))
    strategy = json.loads((ROOT / "strategy_data.json").read_text(encoding="utf-8"))
    forward_status = json.loads((ROOT / "forward_status.json").read_text(encoding="utf-8"))
    long_horizon = json.loads((ROOT / "long_horizon_data.json").read_text(encoding="utf-8"))
    template = (ROOT / "template.html").read_text(encoding="utf-8")
    validate_inputs(data, strategy, forward_status, long_horizon, template)

    body = template.replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    body = body.replace("__STRATEGY_DATA__", json.dumps(strategy, ensure_ascii=False, separators=(",", ":")))
    body = body.replace("__FORWARD_STATUS__", json.dumps(forward_status, ensure_ascii=False, separators=(",", ":")))
    body = body.replace(
        "__LONG_HORIZON_DATA__", json.dumps(long_horizon, ensure_ascii=False, separators=(",", ":"))
    )
    page = (
        '<!doctype html><html lang="zh-Hans"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<meta name="description" content="港股 IPO 打新因子看板：D1/D30 因子、D180/D365 长期核验与基石证据进度">'
        + body[: body.index("</style>") + 8]
        + "</head><body>"
        + body[body.index("</style>") + 8 :]
        + "</body></html>"
    )
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    print(
        f"built index.html {len(page)//1024} KB  "
        f"(stocks={len(data['stocks'])}, factors={len(data['factors'])}, "
        f"forward={forward_status['forward_n']}/{forward_status['target_n']}, "
        f"long_d180={long_horizon['scope']['d180_mature']})"
    )


if __name__ == "__main__":
    main()
