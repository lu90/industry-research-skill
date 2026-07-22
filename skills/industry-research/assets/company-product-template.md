# Company/Product Report Template Metadata

Template metadata starts here. Do not output this metadata section to the user. The final report body starts at the dynamic H1 title immediately before `## 0. 研报前置区`.

## Output Contract

This template is the required output contract for standard or deep company/product reports. Start by copying the Markdown heading skeleton from the dynamic H1 title onward, then fill the sections. Do not use this file only as a reference.

The final report's first nonempty line must be exactly one dynamic H1 title. The next nonempty line must be `## 0. 研报前置区`. Do not output template metadata, template instructions, or internal contract text between them. A standard or deep company/product report must not start with `## 1. 目标公司/产品综合判断`. If a draft starts with section 1, rewrite it from this template before final output.

## Build Order

1. Classify the request and selected layers.
2. Build the internal research brief from `references/research-brief-builder.md`, including report type, source plan, conditional modules, and depth contract.
3. Copy only the required output skeleton from the dynamic H1 title onward.
4. Add conditional sections for multi-business or capital-market questions.
5. Fill every required section with analysis, source quality notes, and evidence gaps.
6. Run the heading scan in `references/company-product-output-contract.md` and the section-level depth gate in `references/report-compliance.md`.
7. Run v64 pre-report Claim admission before drafting. Build `report-claims.json`, audit every bound number, and save `truthfulness-audit.md` before formal registration.
8. If any required heading is missing, any required section is thin, or any Claim fidelity check fails, restore or rewrite the affected content before final output.

## Seven Modules Body Rule

The seven-module section may include a summary table, but the table is only an exhibit. The body must keep `5.1-5.7` as independent analytical subsections. Each subsection must contain `结论`, `证据`, `机制`, `研究含义`, and `关键指标和后续验证`. For listed-company capital-market reports, `5.4-5.7` must be visibly deeper than `5.1-5.3`.

## Mandatory Use

Use this template as the required section structure for standard or deep company/product reports. Keep the main sections unless the user explicitly asks for a short answer. Keep the five labels in every seven-module subsection: `结论`, `证据`, `机制`, `研究含义`, `关键指标和后续验证`. For capital-market reports, make `5.4-5.7` deeper than `5.1-5.3`. Do not merge a seven-module subsection into one sentence or a single summary table. If evidence is insufficient, write the evidence gap and next verification step. For standard and deep reports, include the formal report front and back sections in this template.

## Skeleton Lock

For standard or deep company/product reports, preserve this template's main skeleton before filling content. Do not replace it with a self-created structure.

Required core skeleton for standard company/product reports:

- `0. 研报前置区`
- `1. 目标公司/产品综合判断`
- `2. 研究边界`
- `2.1 研究计划摘要`
- `2.2 来源矩阵和证据质量`
- `2.3 检索缺口闭环结果`
- `3. 宏观环境分析`
- `4. 中观行业分析`
- `4.1 行业一句话定义`
- `4.2 行业关键指标`
- `4.3 行业地图`, with target position in the section body
- `4.4 生命周期判断`
- `5. 七个核心模块分析`
- `5.1 可行性`
- `5.2 规模性`
- `5.3 防守性`
- `5.4 盈利性`
- `5.5 估值`
- `5.6 外部因素`
- `5.7 景气度`
- `6. 微观公司/产品分析`
- `7. SWOT`
- `9. 竞争对手对比`
- `10. 事实, 观点和推断分层`
- `12. 多视角压力测试`
- `13. 风险, 机会和不确定性`
- `14. 后续行动建议`
- `15. 方法论和数据来源说明`
- `16. 后续验证清单`
- `17. 报告合规自检表`

Conditional skeleton:

- Multi-business companies must keep `4.0 多业务线中观拆分`.
- Listed-company capital-market questions must keep `4.0 多业务线中观拆分` by default; if the target is genuinely single-business, use `4.0` to explain why no material split is needed.
- Capital-market questions must keep `11. 资本市场表现与估值预期变化` and `11.1-11.4`.
- `8. 业务/产品组合分析` is required only for portfolio or multi-business portfolio questions; otherwise it may be removed.

Filling rule: non-priority sections may be concise, but required skeleton sections must not be removed or merged. Seven modules must never be merged into one table or paragraph.

# {公司/产品名称}{研究主题}研究报告

## 0. 研报前置区

### 0.1 报告摘要

{用 2-4 个短段落说明: 核心结论, 行业背景, 目标公司/产品位置, 主要风险和需要验证的关键问题.}

### 0.2 关键结论

| 结论 | 原因 | 证据指向 |
|---|---|---|
| {结论 1} | {原因} | {来源或章节} |
| {结论 2} | {原因} | {来源或章节} |
| {结论 3} | {原因} | {来源或章节} |
| {结论 4} | {原因} | {来源或章节} |

### 0.3 核心指标总览

| 指标 | 行业读数 | 目标公司/产品读数 | 判断 | 证据/来源 |
|---|---|---|---|---|
| 市场规模 | {内容} | {内容} | {判断} | {来源} |
| 增速/渗透率 | {内容} | {内容} | {判断} | {来源} |
| 竞争强度 | {内容} | {内容} | {判断} | {来源} |
| 盈利水平 | {内容} | {内容} | {判断} | {来源} |
| 景气度 | {内容} | {内容} | {判断} | {来源} |
| 关键风险 | {内容} | {内容} | {判断} | {来源} |

### 0.4 图表清单或图表占位

| 图表 | 类型 | 用途 |
|---|---|---|
| 图表 1: 行业地图与目标位置 | Mermaid | 展示产业链, 横向竞争和目标位置 |
| 图表 2: 核心指标总览 | 表格 | 展示行业和目标的关键读数 |
| 图表 3: 七模块判断矩阵 | 表格 | 展示七模块结论, 证据层级和证据质量 |
| 图表 4: 竞争对手对比 | 表格 | 展示目标与主要玩家的差异 |

## 1. 目标公司/产品综合判断

{目标公司/产品的行业位置, 核心优势, 核心风险, 初步判断. 先给结论, 不把判断埋在后文.}

## 2. 研究边界

| 项目 | 内容 |
|---|---|
| 地区 | {地区} |
| 时间范围 | {时间范围} |
| 行业口径 | {窄/中/宽口径} |
| 公司/产品范围 | {目标公司/产品/业务线} |
| 包括 | {包括内容} |
| 不包括 | {不包括内容} |
| 关键假设 | {假设} |

### 2.1 研究计划摘要

| 项目 | 内容 |
|---|---|
| 母问题 | {用户真正要回答的问题} |
| 子问题 | {宏观/中观/微观/资本市场的关键子问题} |
| 选择的分析层级 | {宏观/中观/微观/资本市场, 并说明为何选择或排除} |
| 必须验证的事项 | {最影响结论的 3-5 个事实或指标} |
| 条件模块 | multi_business_split={enabled/disabled}; portfolio_analysis={enabled/disabled}; capital_market={enabled/disabled} |

### 2.2 来源矩阵和证据质量

| 关键 Claim | 来源类型 | 本报告用途 | 证据层级 | 证据质量 | 来源状态 | 独立验证状态 | 限制和缺口处理 |
|---|---|---|---|---|---|---|---|
| `{claim_id}`: {读者可理解的 Claim} | 官方统计/监管/行业协会 | {宏观和中观事实} | {primary/near-primary/secondary/weak} | {high/medium/low} | {access_status} | {independence_status} | {口径或时效限制, 下一步来源} |
| `{claim_id}`: {读者可理解的 Claim} | 公司公告/财报/IR/交易所文件 | {公司和财务事实} | {primary/near-primary/secondary/weak} | {high/medium/low} | {access_status} | {independence_status} | {披露频率或分部口径限制, 下一步来源} |
| `{claim_id}`: {读者可理解的 Claim} | 交易所/可信市场数据库 | {股价, 估值, 市值, 交易表现} | {primary/near-primary/secondary/weak} | {high/medium/low} | {access_status} | {independence_status} | {行情口径限制, 下一步来源} |
| `{claim_id}`: {读者可理解的 Claim} | 可信数据库/国际组织/行业报告 | {趋势, 预测, 对比指标} | {primary/near-primary/secondary/weak} | {high/medium/low} | {access_status} | {independence_status} | {预测假设或商业立场, 下一步来源} |
| `{claim_id}`: {读者可理解的 Claim} | 媒体/财经网站/访谈 | {补充信号和观点, 不替代一手核心事实} | {secondary/weak} | {high/medium/low} | {access_status} | {independence_status} | {必须交叉验证, 标记为补充信号} |

### 2.3 检索缺口闭环结果

{本节只保留三轮闭环检索后仍未闭环的高影响缺口. 对每个高影响缺口, 必须先围绕一手或近一手来源最多执行三轮定向检索. 只有当来源不可访问, 需要付费库, 需要登录, 或公开环境没有可靠结果时, 才能保留为 `仍未补齐`, 并展示原因. 已补齐的缺口应移入正文证据, 不继续留在本节.}

| 缺口 | 已尝试轮次和来源 | 当前状态 | 为什么仍重要 | 未补齐原因 | 下一步来源 |
|---|---|---|---|---|---|
| `{gap_id}`: {缺少的指标/文件/数据集/监管原文} | {第1轮: 公司 IR/交易所/官方统计. 第2轮: 行业协会/监管/可信数据库. 第3轮: 替代关键词/本地语言/可信二手交叉验证} | {从 gaps.json 复制状态} | {对结论, 置信度或情景判断的影响} | {从对应 gap 复制 unresolved_reason} | {从对应 gap 复制 next_source_route} |

{对公司/产品和资本市场问题, 必须说明公司公告/IR/交易所/行情数据库/官方行业数据中哪些已按三轮尝试但未取得. 不允许只写“后续关注”或只列下一步来源而不展示三轮闭环尝试.}

## 3. 宏观环境分析

{说明与本问题相关的政策, 经济周期, 消费环境, 利率/汇率/通胀, 技术周期, 资本市场风险偏好等宏观因素. 不要机械展开完整 PEST, 按问题权重展开.}

| 宏观变量 | 当前判断 | 证据/来源 | 对行业和目标的影响 |
|---|---|---|---|
| 政策/监管 | {内容} | {来源} | {影响} |
| 经济/消费周期 | {内容} | {来源} | {影响} |
| 技术周期 | {内容} | {来源} | {影响} |
| 资金面/风险偏好 | {仅资本市场问题必填} | {来源} | {影响} |

## 4. 中观行业分析

### 4.0 多业务线中观拆分

{条件模块. 多业务目标或 company-capital 路线必须保留. 普通单业务公司删除本节. Company-capital 的单业务目标保留本节并说明不存在实质拆分.}

| 业务线/行业线 | 行业阶段 | 竞争格局 | 关键指标/景气信号 | 对目标公司的含义 |
|---|---|---|---|---|
| {业务线 1} | {阶段} | {竞争格局} | {指标} | {含义} |
| {业务线 2} | {阶段} | {竞争格局} | {指标} | {含义} |
| {业务线 3} | {阶段} | {竞争格局} | {指标} | {含义} |

### 4.1 行业一句话定义

{用一句话定义行业, 并说明本报告采用的口径.}

### 4.2 行业关键指标

| 指标 | 当前判断 | 证据/来源 | 对目标公司/产品的含义 |
|---|---|---|---|
| 市场规模 | {规模或代理指标} | {来源} | {影响} |
| 增速/渗透率 | {增速/渗透率} | {来源} | {影响} |
| 供需关系 | {供需判断} | {来源} | {影响} |
| 价格/成本 | {价格或成本变量} | {来源} | {影响} |
| 政策/监管 | {政策变量} | {来源} | {影响} |
| 区域/出口 | {区域或出口变量} | {来源} | {影响} |

### 4.3 行业地图

```mermaid
flowchart LR
  U[上游] --> M[中游]
  M --> T[{目标公司/产品}]
  T --> C[渠道/客户]
  C --> E[终端用户]
```

| 模块 | 内容 | 对目标公司/产品的含义 |
|---|---|---|
| 纵向产业链 | {上游/中游/下游/渠道/客户} | {影响} |
| 横向竞争结构 | {主要玩家/细分赛道/替代品/潜在进入者} | {影响} |
| 生产要素 | {劳动力/资源/资本/技术/数据} | {影响} |
| 生产关系 | {供应商/渠道/客户/监管/平台/资本} | {影响} |
| 关键流向 | {收入/成本/数据/流量/政策影响} | {影响} |
| 目标位置 | {目标所处环节和依赖关系} | {影响} |

### 4.4 生命周期判断

**阶段结论:** {目标所在行业的阶段及判断.}

**证据:** {支持阶段判断的事实, 数据和来源.}

**反证:** {不支持当前阶段判断的事实, 数据或证据缺口.}

**置信度:** {高/中/低及原因.}

**研究含义:** {该阶段对目标机会, 约束和风险的影响.}

## 5. 七个核心模块分析

七个模块必须全部以独立小节出现. 不要只选择其中几个, 也不要用一个汇总表替代本章节. 根据生命周期, 用户问题和目标位置调整篇幅和重点. 标准报告中每个模块应达到约 300-500 个中文字符; 深度报告中每个模块应达到约 600-1000 个中文字符. 每个模块的 `证据` 至少包含 2 个证据点, 数据点, 来源指向或明确证据缺口. 每个模块都必须包含 `关键指标和后续验证`, 用来说明该判断需要跟踪哪些指标, 以及下一步查证的一手或近一手来源. 如果证据不足, 写“证据缺口 + 下一步验证”, 不要用泛泛判断填充. 资本市场问题中, 盈利性, 估值, 外部因素和景气度必须比其它模块展开更深, 标准报告中这些重点模块应达到约 500-800 个中文字符.

### 5.1 可行性

**结论:** {需求真实性, 商业模式, 使用频率, UE 或关键前提的判断.}

**证据:** {事实, 数据, 来源支持的观点, 或明确的证据缺口.}

**机制:** {解释为什么这些依据能支持该可行性判断.}

**研究含义:** {说明行业可行性对目标的机会, 约束或风险.}

**关键指标和后续验证:** {列出需求真实性, 转化率, 留存, 使用频次, 单位经济模型, 产品质量或其它可行性指标, 并说明下一步查证来源.}

### 5.2 规模性

**结论:** {市场空间, 增速, 渗透率, TAM/SAM/SOM 或代理指标的判断.}

**证据:** {事实, 数据, 来源支持的观点, 或明确的证据缺口.}

**机制:** {解释需求驱动, 供给驱动或供需匹配如何影响规模.}

**研究含义:** {说明规模性对目标增长, 份额和资源投入的影响.}

**关键指标和后续验证:** {列出 TAM/SAM/SOM, 市场规模, 增速, 渗透率, 订单/销量或其它规模指标, 并说明下一步查证来源.}

### 5.3 防守性

**结论:** {护城河, 替代风险, 生产要素, 生产关系和竞争壁垒的判断.}

**证据:** {事实, 数据, 来源支持的观点, 或明确的证据缺口.}

**机制:** {解释哪些要素形成防守性, 哪些因素会削弱防守性.}

**研究含义:** {说明目标的相对壁垒, 可被替代风险和防守重点.}

**关键指标和后续验证:** {列出份额稳定性, 客户粘性, 转换成本, 供应链控制力, 渠道效率, 品牌或替代风险指标, 并说明下一步查证来源.}

### 5.4 盈利性

**结论:** {利润池, 议价能力, 毛利率, 成本结构, 资金占用和现金流的判断.}

**证据:** {事实, 数据, 来源支持的观点, 或明确的证据缺口.}

**机制:** {解释价值链利润如何分配, 供需和议价能力如何影响盈利.}

**研究含义:** {说明目标的利润改善空间, 利润压力和需要跟踪的会计/经营指标.}

**关键指标和后续验证:** {列出毛利率, 费用率, 现金流, 分部利润, 价格/成本变量或其它最关键指标, 并说明下一步查证来源.}

### 5.5 估值

**结论:** {生命周期对应估值逻辑, 基本面, 资金面和估值陷阱的判断.}

**证据:** {事实, 数据, 来源支持的观点, 或明确的证据缺口.}

**机制:** {解释为什么该阶段适用该估值逻辑, 哪些变量会改变估值锚.}

**研究含义:** {说明目标更适合用哪些估值或判断框架, 以及哪些指标会重估或杀估值.}

**关键指标和后续验证:** {列出估值倍数, 增长预期, 利润预期, 风险溢价, 同业对比或其它估值锚, 并说明下一步查证来源.}

### 5.6 外部因素

**结论:** {PEST: 政策, 经济, 社会文化, 技术因素的综合判断.}

**证据:** {事实, 数据, 来源支持的观点, 或明确的证据缺口.}

**机制:** {解释外部因素是驱动, 瓶颈, 触发器还是估值冲击.}

**研究含义:** {说明外部因素对目标增长, 成本, 合规, 海外化或技术路线的影响.}

**关键指标和后续验证:** {列出监管政策, 利率/汇率, 原材料, 消费信心, 技术路线或舆情风险等跟踪项, 并说明下一步查证来源.}

### 5.7 景气度

**结论:** {量, 价, 库存, 成本, 利润, 现金流和前瞻指标的判断.}

**证据:** {事实, 数据, 来源支持的观点, 或明确的证据缺口.}

**机制:** {解释哪些指标代表短期景气, 哪些指标代表结构趋势.}

**研究含义:** {说明目标应该重点跟踪哪些指标, 以及这些指标如何影响经营表现.}

**关键指标和后续验证:** {列出订单, 交付, ASP, 库存, 渠道动销, 利润率, 现金流或其它前瞻指标, 并说明下一步查证来源.}

## 6. 微观公司/产品分析

| 维度 | 分析 | 证据/依据 |
|---|---|---|
| 商业模式 | {内容} | {来源} |
| 产品/服务 | {内容} | {来源} |
| 客户和渠道 | {内容} | {来源} |
| 财务/运营指标 | {内容} | {来源} |
| 护城河 | {内容} | {来源} |

## 7. SWOT

| Strengths | Weaknesses |
|---|---|
| {优势} | {劣势} |

| Opportunities | Threats |
|---|---|
| {机会} | {威胁} |

## 8. 业务/产品组合分析

{仅当用户要求或目标有多个业务/产品线时使用波士顿矩阵.}

## 9. 竞争对手对比

| 对象 | 定位 | 优势 | 劣势 | 关键指标 |
|---|---|---|---|---|

## 10. 事实, 观点和推断分层

{本节必须展示证据层级, 证据质量和来源状态. 二手行情源或媒体转述支持的量化内容应标为 `待核验事实` 或在证据层级中标为 `secondary/weak`, 不要与公司公告, 交易所文件或官方统计同级.}

| 类型 | 内容 | 来源/依据 | 证据层级 | 证据质量 | 来源状态 | 置信度 |
|---|---|---|---|---|---|---|
| 事实 | {来自公司公告/交易所/官方统计的事实} | {来源} | {primary/near-primary/secondary/weak} | {high/medium/low} | {access_status} | {高/中/低} |
| 待核验事实 | {来自二手行情源或媒体转述的量化内容} | {来源} | {secondary/weak} | {high/medium/low} | {access_status} | {高/中/低} |
| 观点 | {观点} | {来源和立场} | {secondary/weak} | {high/medium/low} | {access_status} | {高/中/低} |
| 推断 | {推断} | {推理依据} | {基于哪些事实和证据层级} | {high/medium/low} | {受哪些一手缺口影响} | {高/中/低} |

## 11. 资本市场表现与估值预期变化

{仅当用户询问股价涨跌, 估值变化, 市场预期, 投资吸引力, 市值修复或上涨/下跌可能性时使用本章节. 如果不相关, 删除本章节. 本章节不是投资建议, 不给具体买卖点或收益保证. 标准上市公司资本市场报告中, 本章在 11.1-11.4 合计应达到约 1800-3000 个中文字符; 深度报告中应达到约 3000-5000 个中文字符.}

### 11.1 股价表现拆解

{至少用 2-3 个段落说明时间窗口, 股价变化, 对标指数/板块, 已知催化因素和证据缺口. 必须区分价格表现, 时间区间, 直接催化和仍待核验的行情/事件来源. 写明哪些是事实, 哪些是推断.}

### 11.2 基本面变化

{至少用 2-3 个段落拆解收入, 利润率, 现金流, 交付/订单/运营指标, 指引和业务结构变化. 必须区分基本面真实变化和市场预期变化, 并说明哪些指标已经由一手来源支持, 哪些仍需验证.}

### 11.3 估值逻辑和市场预期差

{至少用 3 个段落说明市场之前定价了什么, 当前哪些假设被下修或上修, 哪些指标需要重新证明. 必须解释估值锚, 预期差和重估/杀估值机制, 并说明市场可能过度反应或反应不足的地方.}

### 11.4 上涨触发器, 下跌风险和情景分析

{先用正文分别说明上涨触发器, 下跌风险, 情景假设和跟踪指标. 情景表只能作为摘要, 不能替代主体分析. 不给具体买卖点, 不承诺收益.}

| 情景 | 条件 | 需要跟踪的指标 |
|---|---|---|
| 乐观 | {内容} | {指标} |
| 中性 | {内容} | {指标} |
| 悲观 | {内容} | {指标} |

## 12. 多视角压力测试

{标准或深度公司/产品报告必须包含本章节. 先披露 review_mode: multi-agent 或 single-agent-simulated. 后者必须说明不是独立 Agent 审查. 本表从 challenges.json 压缩生成, 只展示所有 high, 所有 confirmed/partially_valid/unresolved, 以及实际改写报告的 medium/low Challenge.}

| 质疑 ID | 视角 | 目标 Claim/章节 | 重要性 | 核心质疑 | 裁决 | 证据/Gap | 报告改动 | 复核状态 |
|---|---|---|---|---|---|---|---|---|
| `{challenge_id}` | {行业专家/投资研究员/政策或监管研究者/经营者或创业者} | `{claim_id}` / {canonical 章节} | {high/medium/low} | {具体且可验证或可复核的质疑} | {confirmed/partially_valid/refuted/unresolved/out_of_scope} | {source_id 或 gap_id} | {最终报告中的具体改动} | {closed} |

## 13. 风险, 机会和不确定性

{分别写事实风险, 假设风险, 数据缺口, 上行机会和触发条件. 同时区分行业结构驱动与目标公司/产品自身驱动. 不要只写泛泛风险提示.}

## 14. 后续行动建议

{使用 SMART 写出可执行建议.}



## 15. 方法论和数据来源说明

{说明本报告采用的研究口径, 主要来源类型, 信息交叉验证方式, 以及哪些数据来自官方/公司文件/行业协会/媒体补充.}

| 来源类型 | 用途 | 证据层级 | 证据质量 | 备注 |
|---|---|---|---|---|
| 官方统计/监管/行业协会 | {行业事实和政策} | {primary/near-primary} | {high/medium/low} | {说明} |
| 公司公告/财报/IR/交易所文件 | {公司和财务事实} | {primary/near-primary} | {high/medium/low} | {说明} |
| 可信数据库/国际组织 | {行业趋势和预测} | {near-primary/secondary} | {high/medium/low} | {说明} |
| 媒体/财经网站/访谈 | {补充信号和观点} | {secondary/weak} | {high/medium/low} | {必须标记限制} |

## 16. 后续验证清单

{本章节必须是可执行验证清单. 每个待验证问题都要说明为什么重要, 推荐来源和优先级. 推荐来源应优先写公司公告/财报/IR/交易所文件/监管公告/行业协会/官方统计/可信数据库, 媒体只能作为补充.}

| 待验证问题 | 当前证据状态 | 为什么重要 | 推荐来源 | 优先级 |
|---|---|---|---|---|
| {问题 1} | {Evidence Ledger 或 Gap 状态} | {原因} | {来源} | {高/中/低} |
| {问题 2} | {Evidence Ledger 或 Gap 状态} | {原因} | {来源} | {高/中/低} |
| {问题 3} | {Evidence Ledger 或 Gap 状态} | {原因} | {来源} | {高/中/低} |

## 17. 报告合规自检表

{标准或深度报告必须输出本章节. 自检表用于确认报告是否满足模板, 深度, 证据和格式要求. 如果某项未通过, 先补齐正文, 再输出最终报告.}

| 检查项 | 是否通过 | 说明 |
|---|---|---|
| 模板骨架完整 | {通过/不适用} | {说明} |
| 研究简报转译已完成 | {通过/不适用} | {说明} |
| 未误触发显式短答模式 | {通过/不适用} | {说明} |
| Deep Research 可见痕迹完整 | {通过/不适用} | {说明} |
| 分析层级选择正确 | {通过/不适用} | {宏观/中观/微观/资本市场} |
| 多业务线中观拆分完成 | {通过/不适用} | {说明} |
| 七个核心模块全部出现 | {通过/不适用} | {说明} |
| 七模块结构完整 | {通过/不适用} | {五块结构完整; 资本市场重点模块更深} |
| 重点模块展开深度足够 | {通过/不适用} | {说明} |
| 宏观/中观/微观/资本市场章节深度足够 | {通过/不适用} | {说明} |
| 报告深度 rubric 达标 | {通过/不适用} | {说明} |
| 资本市场章节适用时已出现 | {通过/不适用} | {说明} |
| 来源层级, 证据质量和来源状态清楚 | {通过/不适用} | {说明} |
| 独立验证状态和缺口清楚 | {通过/不适用} | {说明} |
| 事实/观点/推断已分层且证据层级清楚 | {通过/不适用} | {说明} |
| Challenge Ledger 闭环和九列摘要一致 | {通过/不适用} | {无 pending, 无 open/disputed high, 与 challenges.json 一致} |
| Pressure Test 改写后重跑 v64 | {通过/不适用} | {受影响 Claim admission/binding 和 final fidelity 已重跑} |
| 后续验证清单具体 | {通过/不适用} | {说明} |
| Markdown 标题格式正确 | {通过/不适用} | {说明} |
| 逐 Claim 证据准入通过 | {通过/不适用} | {supported/refuted, 无 conflicted/gapped/orphaned} |
| 正文 Claim 和 Evidence 精确绑定通过 | {通过/不适用} | {report-claims.json 已通过最终忠实度审计} |
| 关键数字核对和抽样审计完成 | {通过/不适用} | {truthfulness-audit.md 的复核者类型和抽样 Claim} |

本报告仅供研究和信息参考, 不构成投资建议, 也不构成任何收益承诺.
