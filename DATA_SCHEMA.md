# 看板冻结数据字段字典

看板使用四份数据：`dashboard_data.json` 保存因子与个股研究快照，`strategy_data.json` 保存冻结 v2 卡及策略对决快照，`forward_status.json` 保存 F4 前瞻进度与运营基线版本，`long_horizon_data.json` 保存 D180/D365 核验与证据补齐进度。**四者都是 ipo-tool 私有仓冻结报告/补充说明的只读导出**——渲染层可以增删展示、重排、加解释，但不得改写统计数值或在浏览器重估它们。

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

### 2026-07-13 数据层已交付的新字段（codex 审阅后修正，可接线渲染）

数据层已按上面 codex 契约补齐，以下字段现存在于 dashboard_data.json：

| 字段（factors[]/stocks[]/meta） | 含义 |
|---|---|
| `factors[].d30after` | **对齐口径「D1收盘→D30后续超额」四件套**（结构同 d1/d30：ic/n/p/seg/hot/cold/mono/monoRho/bins）。修正现口径 D30 从发行价起算、含首日跳涨、与 HSI 起点不对齐的 bug。可能为 null。**建议渲染层用它替代/并列现有 d30 图**，回答「首日炒作结束后是否继续跑赢」。实测：孖展 d30after IC=−0.03（现口径 +0.375 全是首日功劳），营收增速仍 +0.18。|
| `factors[].groups` | 类别因子真实分组（履约 line-55 契约），按目标分键：`{d1:[...], d30:[...], d30after:[...]}`，每元素 `{value,label,n,median,break_rate}`。仅 `is_zero_cornerstone/sponsor_tier/h_share/is_profitable` 有；连续因子为 null。**渲染层可用它替换类别占位符**。保荐档次已用中英别名修正档重算。|
| `factors[].d1.fixed`（仅 sponsor_tier） | =true，标记该因子 D1 IC 已用别名修正档覆盖（−0.057→+0.03，证伪「定价激进」负向机制）。|
| `stocks[].dxa` | 该股「D1收盘→D30后续超额」（对齐口径），供散点/表格增加剥离首日目标。可能 null。|
| `stocks[].f.margin_final` | 已 +1（RateOver→认购倍数），不再出现负值。|
| `meta.corrections` | 本次修正说明字典（d30_dual_target/sponsor/cornerstone/evidence_tiers/margin_final），**建议渲染成首屏级披露横幅**。|
| `meta.window` | 已改为「211 主板 + 3 GEM」。|

因子 `verdict` 现含 `口径重构中·降级`（sponsor_tier）与 `行情依赖·观察信号`（is_zero_cornerstone）；`why` 文案已去掉「定价激进」「货源归边」等经不起追问的因果断言。

### 2026-07-14 新增字段（基石身份/集中度因子全样本落地）

| 字段（meta.p2_hardening） | 含义 |
|---|---|
| `meta.p2_hardening.cornerstone_identity` | **已更正**：旧串曾判「基石名单待抓取、数据阻塞」——系误判（全样本名单+每家配售股数早已缓存）。新串为全样本结论。|
| `meta.p2_hardening.cornerstone_factors` | 新增结构化证据块：`coverage`（172 具名/214 总/42 零基石）、`asof_note`、`block_permutation.cs_inst_share_d1`，及 `factors` 字典（`cs_inst_share`/`cs_hhi`/`cs_n_named`/`cs_opaque_share`，各含 `ic_d1/p_d1/n_d1/ic_d30after/break_q1_q5/break_rank/drop20_rank` + 中文名）。**主结论**：`cs_inst_share`（机构/主权基石份额，股数加权）经词边界修正后 D1 归一 IC=**+0.184**（perm-p=0.012，block-p=0.036），d30after +0.181，破发率 29%→18%，**as-of 干净的显著因子**；集中度 `cs_hhi` 越高→严重破发越多（仅破发模型见效）；`cs_opaque_share` 无预测力。`render_hint` 给了建议渲法。该因子已按用户签字 K=16 进入现行 cornerstone 维度；集中度与不透明标签仍只披露。|

`cornerstone_factors.card_status` 已在 2026-07-14 更新为用户签字 K=16 后的生产状态：
`cs_inst_share` 微调现行 `cornerstone` raw 分，维度权重表不变。它不属于 DataDriven_v2 的三因子冻结卡，
页面必须同时标明两套引擎归属。

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

## forward_status.json

| 字段 | 含义 |
|---|---|
| `as_of` / `source_report` | 快照日期与 ipo-tool 权威双跑周报 |
| `forward_n` / `target_n` | 已有前瞻 D1 真值的干净样本数 / 触发终裁附录门槛 |
| `status` | 当前阶段，现为 `collecting` |
| `protocol_date` | 注册协议生效日；仅披露，不修改注册文件 |
| `asset_dates.factor_research/strategy_duel` | 因子研究快照与策略对决各自的冻结日期，避免用一个“更新时间”掩盖不同数据年龄 |
| `freshness_policy` | 周报时区、每周计划时点、宽限小时数与快照告警天数。页面只据此提示延迟，不读取生产日志 |
| `operational_baseline.effective_from/commit/label` | 现行 expert_v1 运营基线版本边界 |
| `operational_baseline.no_mixed_actual_samples` | 版本变化时是否尚无已实现前瞻样本 |
| `operational_baseline.addendum` | 私有仓版本偏差补充说明 |

当前来源为 `ipo-tool/reports/dashboard_forward_status_2026-07-19.json`，该文件依据只读双跑周报和
`docs/f4_forward_baseline_addendum_2026-07-19.md` 生成/登记。公开仓只复制快照，不读取或改写生产日志。
`build.py` 会交叉核对上述资产日期、`strategy_data.generated_at`、`dashboard_data.meta.p2_hardening.date`
与周报来源日期；任一错配即停止构建。浏览器访问时会按新加坡时间动态判断是否已经越过下一次周报
时点及 6 小时宽限期，越界后显示“数据更新延迟”，但不会擅自改写 `forward_n`。

## long_horizon_data.json

该快照由私有仓 `scripts/export_long_horizon_dashboard_snapshot.py` 从四份冻结产物导出：长期因子池、
专家规则审计级历史仿真、关系/锁定证据 dry-run 计划及 5 只招股书逐页审阅试点。关键边界：

- `expert_rule_replay.not_historical_production_predictions=true`：2024–2025 没有当时的完整生产留痕，页面必须称“历史仿真”，不能称实盘预测。
- `long_factor_pool.production_change=false`：通过 D180 联合筛选只代表长期候选，不得写成已入生产。
- `display_factors[].d180_post_d1_excess`：D1 收盘后到 D180、相对恒指的主要长期目标。
- `evidence_backfill.database_writes=false`：关联方、客户/供应商、锁定压力仍在证据补齐阶段；0 覆盖不能解释为该风险为 0。
- `evidence_backfill.pilot.summary`：只展示 5/69 只首批样本的逐页进度、可入研究池值和剩余阻塞；`research_factor_ready_values=4` 不代表 4 个因子有效。
- `evidence_backfill.pilot.rows[].review_status`：逐票披露“原文明示为 0 / 证据缺失 / 口径冲突 / 无基石”等状态；浏览器不得自行推断关系。
- D365 基石类有效样本不足，只能展示“小样本/不足”，不能用来升级或淘汰因子。

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
