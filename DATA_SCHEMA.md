# 看板冻结数据字段字典

看板使用两份数据：`dashboard_data.json` 保存因子与个股研究快照，`strategy_data.json` 保存冻结 v2 卡及策略对决快照。**两者都是 ipo-tool 私有仓冻结报告的只读导出**——渲染层可以增删展示、重排、加解释，但不得改写统计数值或在浏览器重估它们。

## dashboard_data.json 顶层结构

```jsonc
{
  "modules": [ ... ],   // 7 个因子模块
  "factors": [ ... ],   // 29 个因子（含统计）
  "stocks":  [ ... ],   // 214 只个股（含各因子取值 + 表现）
  "meta":    { ... }    // 样本量、窗口、引擎对比
}
```

## modules[]

| 字段 | 含义 |
|---|---|
| `id` | 模块标识（funding/supply/anchor/env/growth/value/research）|
| `name` | 中文名（资金热度 / 供给稀缺 / 基石与保荐 / 市场环境 / 财务·成长 / 财务·估值 / 研究对照）|
| `story` | 模块一句话叙述 |
| `engine` | 与现行评分引擎五维的对应关系 |

CSS 里每个模块有配色变量 `--m-<id>`。

## factors[]

| 字段 | 含义 |
|---|---|
| `id` | 因子标识（= 个股 `f` 字典的 key，= 数据集原始字段名）|
| `zh` | 中文名 |
| `m` | 所属模块 id |
| `fmt` | 展示格式：`x`倍 / `yi`亿 / `p1`比例转% / `pv`数值即% / `mc`市值 / `sh`股数 / `hk`港元 / `b`是否 / `tier`保荐档 |
| `know` | 申购截止时点是否可知（false = 研究对照，禁入模型，页面标 🔒）|
| `v2` | 若已入 v2 因子卡，标注权重（如 "主因子 80%"），否则 null |
| `verdict` | 判定：入选候选 / v2 卡在役 / 淘汰 / 研究对照 |
| `why` | 一句话结论 |
| `dir` | 先验方向（+1 越大越好 / −1 越小越好）；IC 已按此归一 |
| `d1` / `d30` | 该因子对 D1 / D30超额 的统计对象（见下），可能为 null（样本不足）|

### factors[].d1 / .d30 统计对象

| 字段 | 含义 |
|---|---|
| `ic` | 归一后 RankIC（正=方向符合先验，负=相反）|
| `n` | 有效样本数 |
| `p` | 置换检验 p 值 |
| `seg` | 分段 IC：`{"2025H1":..,"2025H2":..,"2026":..}` |
| `hot` / `cold` | 火热期 / 非火热期 IC |
| `mono` | 五分位是否单调（bool/null）|
| `monoRho` | 档序 Spearman ρ |
| `bins` | 五分位明细数组：每档 `{bin:1-5, n, median(收益中位,小数), break_rate(破发/跑输率,小数)}` |

`fmt=b` 与 `fmt=tier` 是二元/类别因子；现有 `bins` 不能当成带语义标签的五分位。渲染层必须隐藏这类伪 Q 图，直到数据层显式导出 `groups[{value,label,n,median,break_rate}]`。

## stocks[]

| 字段 | 含义 |
|---|---|
| `t` | 代码（如 "00068"）|
| `nm` | 中文名 |
| `ld` | 上市日 |
| `d1`/`d5`/`d30` | 首日/5日/30日涨幅（小数，相对发行价）|
| `dx` | D30 超额（减同期恒指，小数）；可能 null（未满 30 日）|
| `sp` | 保荐人（拼接串，截断）|
| `f` | **因子取值字典**：key = factor.id，value = 原始数值（缺失则不含该 key）|

## strategy_data.json

这份文件原样承载 `reports/factor_card_v2_duel_2026-07-12.json` 的冻结结果，并补充前端应用固定卡所需的单位与方向元数据。页面只做确定性查表。

| 路径 | 含义 |
|---|---|
| `source` / `generated_at` / `protocol` | 私有仓来源、冻结时间、已注册验证协议 |
| `n_train` | 固定边界与权重的训练窗样本数（114）|
| `n_valid_intersection` | v2 与 expert_v1 公平比较的 2026 验证交集（98）|
| `card.weights` | 三因子固定权重：0.80 / 0.15 / 0.05 |
| `card.directions` | 归一方向；供给因子乘 −1 后再查边界 |
| `card.input_scales` | UI 输入单位到原始因子单位的固定换算；如“亿股”乘 1e8 |
| `card.edges_normalized` | 2025 训练窗冻结的四条归一分位边界 |
| `card.bin_scores` | Q1~Q5 固定档分 `[15,30,50,72,90]` |
| `metrics.rank_ic` | v2 / expert_v1 在验证交集的 RankIC 与差值 95% CI |
| `metrics.buy_tier` | 同覆盖率买入档的 D1 中位、正收益率、破发规避率与差值 CI |
| `verdict` | 冻结对决各门槛是否通过 |

重要口径：`buy_tier.baseline` 是 **expert_v1 旧引擎买入档**，不是全样本或“无脑全打”；两边 `buy_n=68`。`n_breaks=20` 是验证交集的全部破发数，不是任一买入档的破发数。当前没有导出每手损益、费用、策略成员或收益直方图，渲染层不得自行补算或暗示这些结果。

固定卡试算步骤仅为：输入单位换算 → 乘冻结方向 → 对冻结边界查 Q 档 → 取固定档分 → 对在场因子权重归一。输出是固定卡分数和档位，不是收益率、破发概率或买入建议。

## 如何重新导出（数据层，在 ipo-tool 私有仓）

两份公开 JSON 由 ipo-tool 的冻结产物导出，数据源为：

| 数据源（ipo-tool 私有仓路径） | 提供 |
|---|---|
| `data/factor_dataset.json` | 214 只个股的所有因子原始取值 + D1/D5/D30（冻结于 2026-07-12）|
| `reports/factor_signal_library_2026-07-12.json` | F2 信号库：16 个市场/供给/基石/环境因子的四件套统计 |
| `reports/quality_signal_library_2026-07-13.json` | v3 财务因子体检：11 个财务因子的四件套统计 |
| `reports/factor_card_v2_duel_2026-07-12.json` | v2 固定卡边界、权重、2026 对决结果与置信区间 |

新一期数据（如双跑周报满 30 只、v3 卡上线）到位后，由 ipo-tool 侧重新导出对应 JSON，复制到本仓覆盖，跑 `build.py`，推 main。

**注意口径纪律**（详见 ipo-tool `CLAUDE.md` 与 `docs/factor_v2_validation_protocol.md`）：
- 因子取值只能用申购截止日前可知的口径；`know=false` 的字段永远只作研究对照。
- 财务因子只取「申购截止日前最后一个完整财年」（招股书已披露口径）。
- IC、分位边界、分组中位、胜率、破发率、置信区间等统计不在渲染层计算，一律来自冻结报告。
