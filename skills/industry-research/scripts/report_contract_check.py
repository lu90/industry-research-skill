"""
维护用 Markdown 报告结构检查器.

本脚本只检查标题, 开头规则, 关键章节和粗略深度.
它不验证事实真伪, 来源可用性或投资判断质量.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


COMPANY_CORE_HEADINGS = [
    "## 0. 研报前置区",
    "### 0.1 报告摘要",
    "### 0.2 关键结论",
    "### 0.3 核心指标总览",
    "### 0.4 图表清单或图表占位",
    "## 1. 直接结论",
    "## 2. 研究边界",
    "### 2.1 研究计划摘要",
    "### 2.2 来源矩阵和证据质量",
    "### 2.3 二次检索缺口",
    "## 3. 宏观环境分析",
    "## 4. 中观行业分析",
    "### 4.3 行业地图和目标位置",
    "### 4.4 生命周期判断",
    "## 5. 七个核心模块加权分析",
    "### 5.1 可行性",
    "### 5.2 规模性",
    "### 5.3 防守性",
    "### 5.4 盈利性",
    "### 5.5 估值",
    "### 5.6 外部因素",
    "### 5.7 景气度",
    "## 6. 微观公司/产品分析",
    "## 10. 事实, 观点和推断分层",
    "## 12. 多视角压力测试",
    "## 13. 风险和机会",
    "## 15. 方法论和数据来源说明",
    "## 16. 附录: 后续验证清单",
    "## 17. 报告合规自检表",
]

CAPITAL_MARKET_HEADINGS = [
    "### 4.0 多业务线中观拆分",
    "## 11. 资本市场表现与估值预期变化",
    "### 11.1 股价表现拆解",
    "### 11.2 基本面变化",
    "### 11.3 估值逻辑和市场预期差",
    "### 11.4 上涨触发器, 下跌风险和情景分析",
]

OVERVIEW_HEADINGS = [
    "## 1. 行业一句话定义",
    "## 2. 研究边界",
    "### 2.1 研究计划摘要",
    "### 2.2 来源矩阵和证据质量",
    "### 2.3 二次检索缺口",
    "## 3. 行业地图",
    "## 4. 生命周期判断",
    "## 5. 七个核心模块",
    "### 5.1 可行性",
    "### 5.2 规模性",
    "### 5.3 防守性",
    "### 5.4 盈利性",
    "### 5.5 估值",
    "### 5.6 外部因素",
    "### 5.7 景气度",
    "## 8. 事实, 观点和推断分层",
    "## 9. 多视角压力测试",
    "## 11. 报告合规自检表",
]

SPECIFIC_HEADINGS = [
    "## 1. 直接回答",
    "## 2. 结论摘要",
    "## 3. 研究边界",
    "### 3.1 研究计划摘要",
    "### 3.2 来源矩阵和证据质量",
    "### 3.3 二次检索缺口",
    "## 4. 行业地图",
    "## 5. 问题拆解和议题树",
    "## 6. 证据链分析",
    "## 7. 生命周期判断",
    "## 8. 七个核心模块分析",
    "### 8.1 可行性",
    "### 8.2 规模性",
    "### 8.3 防守性",
    "### 8.4 盈利性",
    "### 8.5 估值",
    "### 8.6 外部因素",
    "### 8.7 景气度",
    "## 9. 多视角压力测试",
    "## 12. 报告合规自检表",
]


ENGLISH_HEADING_ALIASES = {
    "## 0. Research Front Matter": "## 0. 研报前置区",
    "### 0.1 Executive Summary": "### 0.1 报告摘要",
    "### 0.2 Key Conclusions": "### 0.2 关键结论",
    "### 0.3 Core Metrics Overview": "### 0.3 核心指标总览",
    "### 0.4 Exhibit List or Placeholders": "### 0.4 图表清单或图表占位",
    "## 1. Direct Conclusion": "## 1. 直接结论",
    "## 1. Direct Answer": "## 1. 直接回答",
    "## 1. One-Sentence Industry Definition": "## 1. 行业一句话定义",
    "## 2. Conclusion Summary": "## 2. 结论摘要",
    "## 2. Research Scope": "## 2. 研究边界",
    "### 2.1 Research Plan Summary": "### 2.1 研究计划摘要",
    "### 2.2 Source Matrix and Evidence Quality": "### 2.2 来源矩阵和证据质量",
    "### 2.3 Follow-up Retrieval Gaps": "### 2.3 二次检索缺口",
    "## 3. Research Scope": "## 3. 研究边界",
    "### 3.1 Research Plan Summary": "### 3.1 研究计划摘要",
    "### 3.2 Source Matrix and Evidence Quality": "### 3.2 来源矩阵和证据质量",
    "### 3.3 Follow-up Retrieval Gaps": "### 3.3 二次检索缺口",
    "## 3. Macro Environment Analysis": "## 3. 宏观环境分析",
    "## 3. Industry Map": "## 3. 行业地图",
    "## 4. Industry Map": "## 4. 行业地图",
    "## 4. Meso Industry Analysis": "## 4. 中观行业分析",
    "### 4.0 Multi-Business Meso Breakdown": "### 4.0 多业务线中观拆分",
    "### 4.1 One-Sentence Industry Definition": "### 4.1 行业一句话定义",
    "### 4.2 Key Industry Metrics": "### 4.2 行业关键指标",
    "### 4.3 Industry Map and Target Position": "### 4.3 行业地图和目标位置",
    "### 4.4 Lifecycle Assessment": "### 4.4 生命周期判断",
    "## 4. Lifecycle Assessment": "## 4. 生命周期判断",
    "## 5. Problem Decomposition and Issue Tree": "## 5. 问题拆解和议题树",
    "## 5. Seven Core Modules": "## 5. 七个核心模块",
    "## 5. Weighted Analysis of Seven Core Modules": "## 5. 七个核心模块加权分析",
    "### 5.1 Feasibility": "### 5.1 可行性",
    "### 5.2 Scalability": "### 5.2 规模性",
    "### 5.3 Defensibility": "### 5.3 防守性",
    "### 5.4 Profitability": "### 5.4 盈利性",
    "### 5.5 Valuation": "### 5.5 估值",
    "### 5.6 External Factors": "### 5.6 外部因素",
    "### 5.7 Prosperity": "### 5.7 景气度",
    "## 6. Evidence Chain Analysis": "## 6. 证据链分析",
    "## 6. Micro Company/Product Analysis": "## 6. 微观公司/产品分析",
    "## 6. Trend Outlook": "## 6. 趋势推演",
    "## 7. Lifecycle Assessment": "## 7. 生命周期判断",
    "## 7. Risks and Opportunities": "## 7. 风险和机会",
    "## 7. SWOT": "## 7. SWOT",
    "## 8. Business/Product Portfolio Analysis": "## 8. 业务/产品组合分析",
    "## 8. Fact, Opinion, and Inference Layers": "## 8. 事实, 观点和推断分层",
    "## 8. Seven Core Modules Analysis": "## 8. 七个核心模块分析",
    "### 8.1 Feasibility": "### 8.1 可行性",
    "### 8.2 Scalability": "### 8.2 规模性",
    "### 8.3 Defensibility": "### 8.3 防守性",
    "### 8.4 Profitability": "### 8.4 盈利性",
    "### 8.5 Valuation": "### 8.5 估值",
    "### 8.6 External Factors": "### 8.6 外部因素",
    "### 8.7 Prosperity": "### 8.7 景气度",
    "## 9. Multi-Perspective Pressure Test": "## 9. 多视角压力测试",
    "## 9. Competitor Comparison": "## 9. 竞争对手对比",
    "## 10. Fact, Opinion, and Inference Layers": "## 10. 事实, 观点和推断分层",
    "## 10. Follow-up Research Recommendations": "## 10. 后续研究建议",
    "## 10. Risks and Uncertainties": "## 10. 风险和不确定性",
    "## 11. Capital-Market Performance and Valuation Expectation Changes": "## 11. 资本市场表现与估值预期变化",
    "### 11.1 Share-Price Performance Breakdown": "### 11.1 股价表现拆解",
    "### 11.2 Fundamental Changes": "### 11.2 基本面变化",
    "### 11.3 Valuation Logic and Market Expectation Gap": "### 11.3 估值逻辑和市场预期差",
    "### 11.4 Upside Catalysts, Downside Risks, and Scenario Analysis": "### 11.4 上涨触发器, 下跌风险和情景分析",
    "## 11. Report Compliance Checklist": "## 11. 报告合规自检表",
    "## 11. Follow-up Verification Checklist": "## 11. 后续验证清单",
    "## 12. Multi-Perspective Pressure Test": "## 12. 多视角压力测试",
    "## 12. Report Compliance Checklist": "## 12. 报告合规自检表",
    "## 13. Risks and Opportunities": "## 13. 风险和机会",
    "## 14. Recommended Next Actions": "## 14. 后续行动建议",
    "## 15. Methodology and Data Sources": "## 15. 方法论和数据来源说明",
    "## 16. Appendix: Follow-up Verification Checklist": "## 16. 附录: 后续验证清单",
    "## 17. Report Compliance Checklist": "## 17. 报告合规自检表",
}


ENGLISH_TERM_ALIASES = {
    "This report is for research and informational purposes only. It does not constitute investment advice or any guarantee of returns.": "本报告仅供研究和信息参考, 不构成投资建议, 也不构成任何收益承诺.",
    "Multi-Perspective Pressure Test": "多视角压力测试",
    "Fact, Opinion, and Inference": "事实/观点/推断",
    "Research Front Matter": "研报前置区",
    "Key Metrics and Follow-up Verification": "关键指标和后续验证",
    "Follow-up Verification Checklist": "后续验证清单",
    "Implication for Target Company/Product": "对目标公司/产品的影响",
    "Implication for the Target Company": "对目标公司的含义",
    "Implication for the Question": "对该问题的含义",
    "Industry Implication": "行业含义",
    "Three-Round Closure Attempts": "三轮闭环已尝试",
    "Why It Still Matters": "为什么仍重要",
    "Why It Matters": "为什么重要",
    "Unresolved Reason": "未补齐原因",
    "Next Source": "下一步来源",
    "Current Status": "当前状态",
    "Research Plan Summary": "研究计划摘要",
    "Research Brief": "研究简报",
    "Seven Core Modules": "七个核心模块",
    "Source Matrix": "来源矩阵",
    "Follow-up Retrieval Gaps": "二次检索缺口",
    "Fact/Opinion/Inference": "事实/观点/推断",
    "Pressure Test": "压力测试",
    "Report Compliance Checklist": "报告合规自检表",
    "Report Route": "报告路由",
    "Must Use": "必须使用",
    "Structure Requirements": "结构要求",
    "Required Sections": "必需章节",
    "Depth Requirements": "深度要求",
    "Target Length": "目标字数",
    "Evidence Requirements": "证据要求",
    "Primary-Source-First": "一手来源优先",
    "Primary-Source Retrieval Status": "一手来源检索状态",
    "Compliance Requirements": "合规要求",
    "Rewrite": "重写",
    "Company/Product": "公司/产品",
    "Capital Market": "资本市场",
    "Capital-Market": "资本市场",
    "Listed Company": "上市公司",
    "Share Price": "股价",
    "Share-Price Performance": "股价",
    "Price Pattern": "价格表现",
    "Time Period": "时间区间",
    "One-Year": "时间区间",
    "Two-Year": "时间区间",
    "Fundamental Catalysts": "催化",
    "Catalysts": "催化",
    "Data Gap": "证据缺口",
    "Verification Gap": "待核验",
    "Market Expectations": "市场预期",
    "Expectation Gap": "预期差",
    "Business Mix": "业务组合",
    "Mix": "业务组合",
    "Fundamentals": "基本面",
    "Fundamental Change": "基本面变化",
    "Re-Rating": "重估",
    "Proof Required": "需要证明",
    "Proof": "需要证明",
    "Upside Catalyst": "上涨触发器",
    "Downside Risks": "下跌风险",
    "Metrics to Track": "跟踪指标",
    "Scenario": "情景",
    "Not Investment Advice": "不构成投资建议",
    "Micro Company/Product Analysis": "微观公司/产品分析",
    "Source Type": "来源类型",
    "Use in This Report": "本报告用途",
    "Evidence Tier": "证据等级",
    "Retrieval Status": "检索状态",
    "Limitations": "限制",
    "Primary-Source Status": "一手来源状态",
    "Source Status": "来源状态",
    "Gap Handling": "缺口处理",
    "Source/Basis": "来源/依据",
    "Evidence/Basis": "证据/依据",
    "Sub-question": "子问题",
    "Business Line": "业务线",
    "Industry Stage": "行业阶段",
    "Competitive Landscape": "竞争格局",
    "Core Metrics": "关键指标",
    "Metric": "指标",
    "Industry Reading": "行业读数",
    "Target Company/Product Reading": "目标公司/产品读数",
    "Judgment": "判断",
    "Evidence/Source": "证据/来源",
    "Market Size": "市场规模",
    "Growth Rate": "增速",
    "Penetration Rate": "渗透率",
    "Competitive Intensity": "竞争强度",
    "Profitability Level": "盈利水平",
    "Key Risk": "关键风险",
    "Lifecycle Phase": "阶段结论",
    "Introduction Phase": "导入期",
    "Growth Phase": "成长期",
    "Mature Phase": "成熟期",
    "Decline Phase": "衰退期",
    "Counterevidence": "反证",
    "Confidence": "置信度",
    "Basis": "依据",
    "Perspective": "视角",
    "Challenge": "质疑",
    "Impact": "影响",
    "Verification Needed": "需要验证",
    "Check": "检查项",
    "Passed": "是否通过",
    "Explanation": "说明",
    "Verification Item": "待验证问题",
    "Recommended Source": "推荐来源",
    "Business Line/Industry Line": "业务线/行业线",
    "Key Metrics/Prosperity Signal": "关键指标/景气信号",
    "Missing Evidence": "证据缺口",
    "Round 1": "第1轮",
    "Round 2": "第2轮",
    "Round 3": "第3轮",
    "Attempted Sources": "尝试来源",
    "Partially Closed": "部分补齐",
    "Still Open": "仍未补齐",
    "Paid Database": "付费库",
    "Login Required": "需要登录",
    "Definition Mismatch": "口径不匹配",
    "Primary Source": "一手来源",
    "Near-Primary Source": "近一手来源",
    "Official Source": "官方来源",
    "Industry Association": "行业协会",
    "Credible Database": "可信数据库",
    "Industry Expert": "行业专家",
    "Investment Researcher": "投资研究员",
    "Policy/Regulatory": "政策/监管",
    "Operator/Entrepreneur": "经营者/创业者",
    "Policy": "政策",
    "Regulation": "监管",
    "Economy": "经济",
    "Consumption": "消费",
    "Technology": "技术",
    "Cost": "成本",
    "Cycle": "周期",
    "Industry Definition": "行业定义",
    "Industry Map": "行业地图",
    "Lifecycle": "生命周期",
    "Business Model": "商业模式",
    "Product": "产品",
    "Service": "服务",
    "Customer": "客户",
    "Channel": "渠道",
    "Financials": "财务",
    "Operations": "运营",
    "Revenue": "收入",
    "Profit": "利润",
    "Cash Flow": "现金流",
    "Deliveries and Orders": "交付和订单",
    "Deliveries": "交付",
    "Shipments": "交付",
    "Orders": "订单",
    "Volume": "运营指标",
    "Moat": "护城河",
    "Competitive Advantage": "竞争优势",
    "Risk": "风险",
    "Opportunity": "机会",
    "Industry Risk": "行业风险",
    "Industry-Structure": "行业结构",
    "Industry Opportunity": "行业机会",
    "Company Risk": "目标公司风险",
    "Company Opportunity": "目标公司机会",
    "Target Company": "目标公司",
    "Company Filings": "公司公告",
    "Primary Company Disclosure": "一手来源",
    "Near-Primary": "近一手",
    "Peer-Reviewed Research": "近一手来源",
    "Peer-Reviewed": "近一手",
    "Verification": "验证",
    "Priority": "优先级",
    "Conclusion": "结论",
    "Evidence": "证据",
    "Mechanism": "机制",
    "Fact": "事实",
    "Opinion": "观点",
    "Inference": "推断",
    "Content": "内容",
    "Type": "类型",
    "Gap": "缺口",
    "Feasibility": "可行性",
    "Scalability": "规模性",
    "Defensibility": "防守性",
    "Profitability": "盈利性",
    "Valuation": "估值",
    "External Factors": "外部因素",
    "Prosperity": "景气度",
}


CANONICAL_DISCLAIMER = "本报告仅供研究和信息参考, 不构成投资建议, 也不构成任何收益承诺."


OVERVIEW_MODULE_HEADINGS = [
    "### 5.1 可行性",
    "### 5.2 规模性",
    "### 5.3 防守性",
    "### 5.4 盈利性",
    "### 5.5 估值",
    "### 5.6 外部因素",
    "### 5.7 景气度",
]

SPECIFIC_MODULE_HEADINGS = [
    "### 8.1 可行性",
    "### 8.2 规模性",
    "### 8.3 防守性",
    "### 8.4 盈利性",
    "### 8.5 估值",
    "### 8.6 外部因素",
    "### 8.7 景气度",
]

COMPANY_MODULE_HEADINGS = OVERVIEW_MODULE_HEADINGS

CANONICAL_FIELD_CONTRACTS = {
    "overview": {
        "zh": {
            "tables": [
                ("### 2.2 来源矩阵和证据质量", ["来源类型", "本报告用途", "证据层级", "检索状态", "限制"]),
                ("### 2.3 二次检索缺口", ["缺口", "三轮闭环已尝试", "当前状态", "为什么仍重要", "未补齐原因", "下一步来源"]),
                ("## 8. 事实, 观点和推断分层", ["类型", "内容", "来源/依据", "证据层级", "来源状态", "置信度"]),
                ("## 9. 多视角压力测试", ["视角", "质疑", "影响", "需要验证"]),
                ("## 11. 报告合规自检表", ["检查项", "是否通过", "说明"]),
            ],
            "labels": [
                ("## 4. 生命周期判断", ["阶段结论", "证据", "反证", "置信度", "行业含义"]),
                *[(heading, ["结论", "证据", "机制", "行业含义"]) for heading in OVERVIEW_MODULE_HEADINGS],
            ],
            "rounds": [("### 2.3 二次检索缺口", ["第1轮", "第2轮", "第3轮"])],
            "rows": [],
        },
        "en": {
            "tables": [
                ("### 2.2 Source Matrix and Evidence Quality", ["Source Type", "Use in This Report", "Evidence Tier", "Retrieval Status", "Limitations"]),
                ("### 2.3 Follow-up Retrieval Gaps", ["Gap", "Three-Round Closure Attempts", "Current Status", "Why It Still Matters", "Unresolved Reason", "Next Source"]),
                ("## 8. Fact, Opinion, and Inference Layers", ["Type", "Content", "Source/Basis", "Evidence Tier", "Source Status", "Confidence"]),
                ("## 9. Multi-Perspective Pressure Test", ["Perspective", "Challenge", "Impact", "Verification Needed"]),
                ("## 11. Report Compliance Checklist", ["Check", "Passed", "Explanation"]),
            ],
            "labels": [
                ("## 4. Lifecycle Assessment", ["Lifecycle Phase", "Evidence", "Counterevidence", "Confidence", "Industry Implication"]),
                *[(heading, ["Conclusion", "Evidence", "Mechanism", "Industry Implication"]) for heading in ENGLISH_HEADING_ALIASES if heading.startswith("### 5.")],
            ],
            "rounds": [("### 2.3 Follow-up Retrieval Gaps", ["Round 1", "Round 2", "Round 3"])],
            "rows": [],
        },
    },
    "specific": {
        "zh": {
            "tables": [
                ("### 3.2 来源矩阵和证据质量", ["来源类型", "本报告用途", "证据层级", "检索状态", "限制"]),
                ("### 3.3 二次检索缺口", ["缺口", "三轮闭环已尝试", "当前状态", "为什么仍重要", "未补齐原因", "下一步来源"]),
                ("## 6. 证据链分析", ["子问题", "结论", "事实", "观点", "推断", "证据层级", "来源状态", "置信度"]),
                ("## 9. 多视角压力测试", ["视角", "质疑", "影响", "需要验证"]),
                ("## 12. 报告合规自检表", ["检查项", "是否通过", "说明"]),
            ],
            "labels": [
                ("## 7. 生命周期判断", ["阶段结论", "证据", "反证", "置信度", "对该问题的含义"]),
                *[(heading, ["结论", "证据", "机制", "对该问题的含义"]) for heading in SPECIFIC_MODULE_HEADINGS],
            ],
            "rounds": [("### 3.3 二次检索缺口", ["第1轮", "第2轮", "第3轮"])],
            "rows": [],
        },
        "en": {
            "tables": [
                ("### 3.2 Source Matrix and Evidence Quality", ["Source Type", "Use in This Report", "Evidence Tier", "Retrieval Status", "Limitations"]),
                ("### 3.3 Follow-up Retrieval Gaps", ["Gap", "Three-Round Closure Attempts", "Current Status", "Why It Still Matters", "Unresolved Reason", "Next Source"]),
                ("## 6. Evidence Chain Analysis", ["Sub-question", "Conclusion", "Fact", "Opinion", "Inference", "Evidence Tier", "Source Status", "Confidence"]),
                ("## 9. Multi-Perspective Pressure Test", ["Perspective", "Challenge", "Impact", "Verification Needed"]),
                ("## 12. Report Compliance Checklist", ["Check", "Passed", "Explanation"]),
            ],
            "labels": [
                ("## 7. Lifecycle Assessment", ["Lifecycle Phase", "Evidence", "Counterevidence", "Confidence", "Implication for the Question"]),
                *[(heading, ["Conclusion", "Evidence", "Mechanism", "Implication for the Question"]) for heading in ENGLISH_HEADING_ALIASES if heading.startswith("### 8.")],
            ],
            "rounds": [("### 3.3 Follow-up Retrieval Gaps", ["Round 1", "Round 2", "Round 3"])],
            "rows": [],
        },
    },
}


COMPANY_FIELD_CONTRACT = {
    "zh": {
        "tables": [
            ("### 0.3 核心指标总览", ["指标", "行业读数", "目标公司/产品读数", "判断", "证据/来源"]),
            ("### 2.2 来源矩阵和证据质量", ["来源类型", "本报告用途", "证据等级", "一手来源状态", "缺口处理"]),
            ("### 2.3 二次检索缺口", ["缺口", "三轮闭环已尝试", "当前状态", "为什么仍重要", "未补齐原因", "下一步来源"]),
            ("### 4.0 多业务线中观拆分", ["业务线/行业线", "行业阶段", "竞争格局", "关键指标/景气信号", "对目标公司的含义"]),
            ("## 10. 事实, 观点和推断分层", ["类型", "内容", "来源/依据", "证据层级", "一手来源状态", "置信度"]),
            ("## 12. 多视角压力测试", ["视角", "质疑", "为什么重要", "需要验证"]),
            ("## 16. 附录: 后续验证清单", ["待验证问题", "为什么重要", "推荐来源", "优先级"]),
            ("## 17. 报告合规自检表", ["检查项", "是否通过", "说明"]),
        ],
        "labels": [
            ("### 4.4 生命周期判断", ["阶段结论", "证据", "反证", "置信度", "对目标公司/产品的影响"]),
            *[(heading, ["结论", "依据", "机制", "对目标公司/产品的影响", "关键指标和后续验证"]) for heading in COMPANY_MODULE_HEADINGS],
        ],
        "rounds": [("### 2.3 二次检索缺口", ["第1轮", "第2轮", "第3轮"])],
        "rows": [
            ("### 0.3 核心指标总览", ["市场规模", "增速/渗透率", "竞争强度", "盈利水平", "景气度", "关键风险"]),
        ],
    },
    "en": {
        "tables": [
            ("### 0.3 Core Metrics Overview", ["Metric", "Industry Reading", "Target Company/Product Reading", "Judgment", "Evidence/Source"]),
            ("### 2.2 Source Matrix and Evidence Quality", ["Source Type", "Use in This Report", "Evidence Tier", "Primary-Source Status", "Gap Handling"]),
            ("### 2.3 Follow-up Retrieval Gaps", ["Gap", "Three-Round Closure Attempts", "Current Status", "Why It Still Matters", "Unresolved Reason", "Next Source"]),
            ("### 4.0 Multi-Business Meso Breakdown", ["Business Line/Industry Line", "Industry Stage", "Competitive Landscape", "Key Metrics/Prosperity Signal", "Implication for the Target Company"]),
            ("## 10. Fact, Opinion, and Inference Layers", ["Type", "Content", "Source/Basis", "Evidence Tier", "Primary-Source Status", "Confidence"]),
            ("## 12. Multi-Perspective Pressure Test", ["Perspective", "Challenge", "Why It Matters", "Verification Needed"]),
            ("## 16. Appendix: Follow-up Verification Checklist", ["Verification Item", "Why It Matters", "Recommended Source", "Priority"]),
            ("## 17. Report Compliance Checklist", ["Check", "Passed", "Explanation"]),
        ],
        "labels": [
            ("### 4.4 Lifecycle Assessment", ["Lifecycle Phase", "Evidence", "Counterevidence", "Confidence", "Implication for Target Company/Product"]),
            *[(heading, ["Conclusion", "Basis", "Mechanism", "Implication for Target Company/Product", "Key Metrics and Follow-up Verification"]) for heading in ENGLISH_HEADING_ALIASES if heading.startswith("### 5.")],
        ],
        "rounds": [("### 2.3 Follow-up Retrieval Gaps", ["Round 1", "Round 2", "Round 3"])],
        "rows": [
            ("### 0.3 Core Metrics Overview", ["Market Size", "Growth Rate/Penetration Rate", "Competitive Intensity", "Profitability Level", "Prosperity", "Key Risk"]),
        ],
    },
}

CANONICAL_FIELD_CONTRACTS["company"] = COMPANY_FIELD_CONTRACT
CANONICAL_FIELD_CONTRACTS["company-capital"] = COMPANY_FIELD_CONTRACT


def read_text(path: Path) -> str:
    """
    读取 Markdown 文件内容.

    :param path: Markdown 文件路径.
    :return: 文件文本.
    """
    return path.read_text(encoding="utf-8")


def normalize_lines(text: str) -> list[str]:
    """
    规范化文本行.

    :param text: 原始文本.
    :return: 去除右侧空白后的行列表.
    """
    return [line.rstrip() for line in text.splitlines()]


def first_nonempty_line(text: str) -> str:
    """
    获取第一行非空文本.

    :param text: 原始文本.
    :return: 第一行非空文本, 不存在时返回空字符串.
    """
    for line in normalize_lines(text):
        if line.strip():
            return line.strip()
    return ""


def section_body(text: str, heading: str) -> str:
    """
    提取指定标题下方正文.

    :param text: Markdown 文本.
    :param heading: 要定位的标题.
    :return: 标题下方直到下一个同级或更高级标题前的正文.
    """
    pattern = re.escape(heading)
    match = re.search(rf"(?m)^{pattern}\s*$", text)
    if not match:
        return ""

    heading_level = len(heading) - len(heading.lstrip("#"))
    start = match.end()
    next_heading = re.search(rf"(?m)^#{{1,{heading_level}}}\s+", text[start:])
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].strip()


def parse_markdown_table_cells(line: str) -> list[str]:
    """
    解析 Markdown 表格行的单元格.

    :param line: Markdown 表格行.
    :return: 去除单元格两侧空白后的字段列表.
    """
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    return [cell.strip() for cell in stripped[1:-1].split("|")]


def is_markdown_separator_row(cells: list[str]) -> bool:
    """
    判断字段列表是否为 Markdown 表格分隔行.

    :param cells: 已解析的表格字段.
    :return: 全部字段均为分隔符时返回 True.
    """
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def markdown_table_headers(text: str, heading: str) -> list[list[str]]:
    """
    提取指定章节内所有 Markdown 表格表头.

    :param text: Markdown 报告文本.
    :param heading: 目标章节标题.
    :return: 按出现顺序排列的表头字段列表.
    """
    body = section_body(text, heading)
    lines = body.splitlines()
    headers: list[list[str]] = []
    for index in range(len(lines) - 1):
        current = parse_markdown_table_cells(lines[index])
        following = parse_markdown_table_cells(lines[index + 1])
        if current and is_markdown_separator_row(following) and len(current) == len(following):
            headers.append(current)
    return headers


def markdown_table_first_cells(text: str, heading: str) -> list[str]:
    """
    提取指定章节内所有 Markdown 表格数据行的首字段.

    :param text: Markdown 报告文本.
    :param heading: 目标章节标题.
    :return: 排除表头和分隔行后的首字段列表.
    """
    body = section_body(text, heading)
    lines = body.splitlines()
    first_cells: list[str] = []
    for index, line in enumerate(lines):
        cells = parse_markdown_table_cells(line)
        if not cells or is_markdown_separator_row(cells):
            continue
        following = parse_markdown_table_cells(lines[index + 1]) if index + 1 < len(lines) else []
        if is_markdown_separator_row(following):
            continue
        first_cells.append(cells[0])
    return first_cells


def validate_canonical_fields(text: str, profile: str, language: str) -> list[str]:
    """
    严格检查报告中的双语契约字段.

    本检查仅忽略 Markdown 表格单元格两侧空白. 字段拼写, 大小写,
    连字符, 顺序和段内标签必须与契约完全一致.

    :param text: 原始 Markdown 报告文本.
    :param profile: 已确定的正式报告类型.
    :param language: 已确定的报告语言, 可为 `zh` 或 `en`.
    :return: 精确字段契约错误列表.
    """
    contract = CANONICAL_FIELD_CONTRACTS.get(profile, {}).get(language)
    if not contract:
        return []
    errors: list[str] = []
    for heading, expected in contract["tables"]:
        if heading not in text:
            continue
        headers = markdown_table_headers(text, heading)
        if expected not in headers:
            actual = " | ".join(headers[0]) if headers else "<missing>"
            required = " | ".join(expected)
            errors.append(
                f"noncanonical contract header under {heading}: expected '{required}', got '{actual}'"
            )
    for heading, required_labels in contract["labels"]:
        if heading not in text:
            continue
        body = section_body(text, heading)
        actual_labels = set(re.findall(r"\*\*([^*\r\n]+):\*\*", body))
        missing = [label for label in required_labels if label not in actual_labels]
        if missing:
            errors.append(
                f"noncanonical contract labels under {heading}: missing {', '.join(missing)}"
            )
    for heading, required_rounds in contract["rounds"]:
        if heading not in text:
            continue
        body = section_body(text, heading)
        missing = [marker for marker in required_rounds if marker not in body]
        if missing:
            errors.append(
                f"noncanonical retrieval markers under {heading}: missing {', '.join(missing)}"
            )
    for heading, required_rows in contract["rows"]:
        if heading not in text:
            continue
        actual_rows = markdown_table_first_cells(text, heading)
        missing = [row for row in required_rows if row not in actual_rows]
        if missing:
            errors.append(
                f"noncanonical contract rows under {heading}: missing {', '.join(missing)}"
            )
    return errors


def rough_cjk_length(text: str) -> int:
    """
    估算中英文归一化内容长度.

    :param text: 文本.
    :return: CJK 字符和半数非空白字符的折中长度.
    """
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    non_space = len(re.sub(r"\s+", "", text))
    return max(cjk, non_space // 2)


def detect_report_language(text: str) -> str:
    """
    识别报告主要语言.

    优先使用正式契约标题, 再使用中英文字符占比.

    :param text: Markdown 文本.
    :return: `zh` 或 `en`.
    """
    heading_lines = {line.strip() for line in text.splitlines() if line.lstrip().startswith("#")}
    english_only = {source for source, target in ENGLISH_HEADING_ALIASES.items() if source != target}
    chinese_only = {target for source, target in ENGLISH_HEADING_ALIASES.items() if source != target}
    if heading_lines.intersection(english_only):
        return "en"
    if heading_lines.intersection(chinese_only):
        return "zh"
    cjk_count = len(re.findall(r"[\u4e00-\u9fff]", text))
    latin_count = len(re.findall(r"[A-Za-z]", text))
    return "en" if latin_count > cjk_count * 2 else "zh"


def require_language_consistency(text: str, language: str) -> list[str]:
    """
    检查正式契约标题是否混用中英文.

    :param text: Markdown 文本.
    :param language: 预期语言, 必须为 `zh` 或 `en`.
    :return: 语言一致性错误列表.
    """
    heading_lines = {line.strip() for line in text.splitlines() if line.lstrip().startswith("#")}
    english_only = {source for source, target in ENGLISH_HEADING_ALIASES.items() if source != target}
    chinese_only = {target for source, target in ENGLISH_HEADING_ALIASES.items() if source != target}
    if language == "en":
        mixed = sorted(heading_lines.intersection(chinese_only))
    else:
        mixed = sorted(heading_lines.intersection(english_only))
    return [f"mixed report language heading: {heading}" for heading in mixed]


def normalize_report_contract(text: str, language: str) -> str:
    """
    将英文报告契约词规范化为内部中文契约词.

    规范化只服务于确定性检查, 不修改原始报告文件.

    :param text: Markdown 文本.
    :param language: 报告语言, 必须为 `zh` 或 `en`.
    :return: 供现有检查规则使用的规范化文本.
    """
    if language == "zh":
        return text
    normalized_lines = [ENGLISH_HEADING_ALIASES.get(line.strip(), line) for line in text.splitlines()]
    normalized = "\n".join(normalized_lines)
    for source, target in sorted(ENGLISH_TERM_ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        pattern = rf"(?<![A-Za-z]){re.escape(source)}(?![A-Za-z])"
        normalized = re.sub(pattern, target, normalized, flags=re.IGNORECASE)
    return normalized


def require_headings(text: str, headings: list[str], errors: list[str]) -> None:
    """
    检查必需标题是否存在.

    :param text: Markdown 文本.
    :param headings: 必需标题列表.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    for heading in headings:
        if heading not in text:
            errors.append(f"missing heading: {heading}")


def require_report_shell(text: str, expected_opening: str, errors: list[str]) -> None:
    """
    检查正式报告的 H1, 路由开头和固定免责声明.

    :param text: Markdown 文本.
    :param expected_opening: H1 后必须紧接的路由章节.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    h1_lines = [line for line in lines if re.match(r"^#(?!#)\s+\S", line)]
    if not lines or not re.match(r"^#(?!#)\s+\S", lines[0]):
        actual = lines[0] if lines else ""
        errors.append(f"wrong report title: expected one H1 as the first nonempty line, got {actual!r}")
    elif "{" in lines[0] or "}" in lines[0]:
        errors.append(f"unresolved report title placeholder: {lines[0]!r}")
    if len(h1_lines) != 1:
        errors.append(f"wrong H1 count: expected 1, got {len(h1_lines)}")
    if len(lines) < 2 or lines[1] != expected_opening:
        actual = lines[1] if len(lines) >= 2 else ""
        errors.append(f"wrong route opening after H1: expected {expected_opening!r}, got {actual!r}")
    if not lines or lines[-1] != CANONICAL_DISCLAIMER:
        actual = lines[-1] if lines else ""
        errors.append(f"wrong report disclaimer: expected {CANONICAL_DISCLAIMER!r}, got {actual!r}")
    if text.count(CANONICAL_DISCLAIMER) != 1:
        errors.append(
            f"wrong canonical disclaimer count: expected 1, got {text.count(CANONICAL_DISCLAIMER)}"
        )


def require_report_min_length(text: str, minimum: int, errors: list[str]) -> None:
    """
    检查整篇报告粗略长度是否达到下限.

    :param text: Markdown 文本.
    :param minimum: 整篇报告粗略长度下限.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    length = rough_cjk_length(text)
    if length < minimum:
        errors.append(f"thin report length: length {length}, expected >= {minimum}")


def require_section_min(text: str, heading: str, minimum: int, errors: list[str]) -> None:
    """
    检查章节粗略长度是否达到下限.

    :param text: Markdown 文本.
    :param heading: 章节标题.
    :param minimum: 粗略长度下限.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    body = section_body(text, heading)
    if not body:
        errors.append(f"missing body: {heading}")
        return
    length = rough_cjk_length(body)
    if length < minimum:
        errors.append(f"thin section: {heading}, length {length}, expected >= {minimum}")


def require_labels(text: str, heading: str, labels: list[str], errors: list[str]) -> None:
    """
    检查章节内是否包含指定标签.

    :param text: Markdown 文本.
    :param heading: 章节标题.
    :param labels: 必需标签.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    body = section_body(text, heading)
    for label in labels:
        if label not in body:
            errors.append(f"missing label under {heading}: {label}")


def require_mermaid_block(text: str, errors: list[str]) -> None:
    """
    检查报告是否包含 Mermaid 图.

    :param text: Markdown 文本.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    if "```mermaid" not in text:
        errors.append("missing mermaid industry map")


def require_company_exhibit_list(text: str, errors: list[str]) -> None:
    """
    检查公司报告前置区是否包含足够图表清单.

    :param text: Markdown 文本.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    body = section_body(text, "### 0.4 图表清单或图表占位")
    if not body:
        errors.append("missing body: ### 0.4 图表清单或图表占位")
        return
    exhibit_rows = [
        line
        for line in body.splitlines()
        if line.strip().startswith("|") and ("图表" in line or "Exhibit" in line)
    ]
    if len(exhibit_rows) < 4:
        errors.append(f"thin exhibit list: found {len(exhibit_rows)}, expected >= 4")


def prose_paragraphs(text: str) -> list[str]:
    """
    提取可计入分析深度的正文段落.

    :param text: Markdown 章节正文.
    :return: 正文段落列表.
    """
    paragraphs: list[str] = []
    current: list[str] = []
    in_fence = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or line.startswith("#") or line.startswith("|") or line.startswith("- "):
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        if not line:
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        current.append(line)
    if current:
        paragraphs.append(" ".join(current))
    return [paragraph for paragraph in paragraphs if rough_cjk_length(paragraph) >= 40]


def require_prose_paragraphs(text: str, heading: str, minimum: int, errors: list[str]) -> None:
    """
    检查章节正文段落数量是否达到下限.

    :param text: Markdown 文本.
    :param heading: 章节标题.
    :param minimum: 正文段落数量下限.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    body = section_body(text, heading)
    if not body:
        errors.append(f"missing body: {heading}")
        return
    count = len(prose_paragraphs(body))
    if count < minimum:
        errors.append(f"thin prose paragraphs: {heading}, paragraphs {count}, expected >= {minimum}")


def require_capital_priority_depth_blocks(text: str, errors: list[str]) -> None:
    """
    检查资本市场优先模块是否包含第五深度块.

    :param text: Markdown 文本.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    for heading in [
        "### 5.4 盈利性",
        "### 5.5 估值",
        "### 5.6 外部因素",
        "### 5.7 景气度",
    ]:
        require_labels(text, heading, ["关键指标和后续验证"], errors)


def require_company_module_verification_blocks(text: str, errors: list[str]) -> None:
    """
    检查公司七模块是否均包含关键指标和后续验证块.

    :param text: Markdown 文本.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    for heading in [
        "### 5.1 可行性",
        "### 5.2 规模性",
        "### 5.3 防守性",
        "### 5.4 盈利性",
        "### 5.5 估值",
        "### 5.6 外部因素",
        "### 5.7 景气度",
    ]:
        require_labels(text, heading, ["关键指标和后续验证"], errors)


def require_capital_section_paragraph_density(text: str, errors: list[str]) -> None:
    """
    检查资本市场第 11 章小节的正文段落密度.

    :param text: Markdown 文本.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    for heading, minimum in [
        ("### 11.1 股价表现拆解", 2),
        ("### 11.2 基本面变化", 2),
        ("### 11.3 估值逻辑和市场预期差", 2),
        ("### 11.4 上涨触发器, 下跌风险和情景分析", 1),
    ]:
        require_prose_paragraphs(text, heading, minimum, errors)


def require_capital_section_concepts(text: str, errors: list[str]) -> None:
    """
    检查资本市场第 11 章小节是否覆盖必需概念.

    :param text: Markdown 文本.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    checks = [
        (
            "### 11.1 股价表现拆解",
            [
                ["股价", "价格表现"],
                ["时间窗口", "时间区间"],
                ["指数", "板块", "基准", "benchmark"],
                ["催化", "事件"],
                ["证据缺口", "待核验"],
            ],
        ),
        (
            "### 11.2 基本面变化",
            [
                ["收入", "营收"],
                ["利润", "毛利率", "利润率"],
                ["现金流"],
                ["交付", "订单", "运营指标"],
                ["指引", "业务结构", "业务组合"],
                ["基本面", "预期变化", "市场预期"],
            ],
        ),
        (
            "### 11.3 估值逻辑和市场预期差",
            [
                ["估值锚", "估值"],
                ["预期差", "市场预期"],
                ["之前定价", "priced"],
                ["重估", "杀估值", "rerating", "derating"],
                ["重新证明", "验证指标", "需要证明"],
            ],
        ),
        (
            "### 11.4 上涨触发器, 下跌风险和情景分析",
            [
                ["上涨触发器", "上行触发"],
                ["下跌风险", "下行风险"],
                ["情景", "乐观", "中性", "悲观"],
                ["跟踪指标", "需要跟踪"],
            ],
        ),
    ]
    for heading, groups in checks:
        require_any_terms(text, heading, groups, errors)


def require_company_research_trace_density(text: str, errors: list[str]) -> None:
    """
    检查公司报告研究追踪章节是否过薄.

    :param text: Markdown 文本.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    for heading, minimum in [
        ("### 2.1 研究计划摘要", 120),
        ("### 2.2 来源矩阵和证据质量", 160),
        ("### 2.3 二次检索缺口", 120),
        ("## 10. 事实, 观点和推断分层", 180),
        ("## 15. 方法论和数据来源说明", 120),
    ]:
        require_section_min(text, heading, minimum, errors)


def require_company_report_front_density(text: str, errors: list[str]) -> None:
    """
    检查公司报告前置区是否过薄.

    :param text: Markdown 文本.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    for heading, minimum in [
        ("### 0.1 报告摘要", 120),
        ("### 0.2 关键结论", 120),
        ("### 0.3 核心指标总览", 120),
        ("### 0.4 图表清单或图表占位", 80),
    ]:
        require_section_min(text, heading, minimum, errors)


def require_company_core_metrics_overview(text: str, errors: list[str]) -> None:
    """
    检查核心指标总览是否包含指标表和关键指标行.

    :param text: Markdown 文本.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    heading = "### 0.3 核心指标总览"
    require_evidence_table_columns(
        text,
        heading,
        [
            ["指标"],
            ["行业读数"],
            ["目标公司/产品读数", "目标公司读数", "目标产品读数"],
            ["判断"],
            ["证据/来源", "来源"],
        ],
        errors,
    )
    require_any_terms(
        text,
        heading,
        [
            ["市场规模"],
            ["增速", "渗透率"],
            ["竞争强度", "竞争格局"],
            ["盈利水平", "毛利率", "利润率"],
            ["景气度"],
            ["关键风险", "风险"],
        ],
        errors,
    )


def require_any_terms(text: str, heading: str, term_groups: list[list[str]], errors: list[str]) -> None:
    """
    检查章节内是否覆盖概念关键词组.

    :param text: Markdown 文本.
    :param heading: 章节标题.
    :param term_groups: 关键词组, 每组命中任一关键词即可.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    body = section_body(text, heading)
    if not body:
        errors.append(f"missing body: {heading}")
        return
    for terms in term_groups:
        if not any(term in body for term in terms):
            errors.append(f"missing checklist concept under {heading}: {'/'.join(terms)}")


def require_evidence_table_columns(
    text: str,
    heading: str,
    column_groups: list[list[str]],
    errors: list[str],
) -> None:
    """
    检查证据表是否包含必需列概念.

    :param text: Markdown 文本.
    :param heading: 章节标题.
    :param column_groups: 必需列概念, 每组命中任一词即可.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    body = section_body(text, heading)
    if not body:
        errors.append(f"missing body: {heading}")
        return
    table_lines = [line for line in body.splitlines() if line.strip().startswith("|")]
    table_text = "\n".join(table_lines)
    if not table_text:
        errors.append(f"missing evidence table under {heading}")
        return
    for terms in column_groups:
        if not any(term in table_text for term in terms):
            errors.append(f"missing evidence column under {heading}: {'/'.join(terms)}")


def require_source_matrix_columns(text: str, heading: str, errors: list[str]) -> None:
    """
    检查来源矩阵是否包含来源, 用途, 证据和检索状态列.

    :param text: Markdown 文本.
    :param heading: 章节标题.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    require_evidence_table_columns(
        text,
        heading,
        [
            ["来源类型"],
            ["本报告用途", "用途"],
            ["证据等级", "证据层级"],
            ["一手来源状态", "检索状态", "来源状态"],
            ["缺口处理", "限制"],
        ],
        errors,
    )


def require_fact_inference_columns(text: str, heading: str, errors: list[str]) -> None:
    """
    检查事实观点推断分层表是否包含关键证据列.

    :param text: Markdown 文本.
    :param heading: 章节标题.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    require_evidence_table_columns(
        text,
        heading,
        [
            ["类型"],
            ["内容"],
            ["来源/依据", "证据/依据"],
            ["证据层级", "证据等级"],
            ["一手来源状态", "来源状态"],
            ["置信度"],
            ["事实"],
            ["观点"],
            ["推断"],
        ],
        errors,
    )


def require_specific_evidence_chain_columns(text: str, errors: list[str]) -> None:
    """
    检查行业具体问题证据链是否包含事实观点推断列.

    :param text: Markdown 文本.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    require_evidence_table_columns(
        text,
        "## 6. 证据链分析",
        [
            ["子问题"],
            ["结论"],
            ["事实"],
            ["观点"],
            ["推断"],
            ["证据层级", "证据等级"],
            ["来源状态", "检索状态"],
            ["置信度"],
        ],
        errors,
    )


def require_lifecycle_depth(text: str, heading: str, target_terms: list[str], errors: list[str]) -> None:
    """
    检查生命周期判断是否包含阶段, 证据, 反证, 置信度和含义.

    :param text: Markdown 文本.
    :param heading: 生命周期章节标题.
    :param target_terms: 含义对象关键词.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    require_section_min(text, heading, 160, errors)
    require_any_terms(
        text,
        heading,
        [
            ["阶段", "导入期", "成长期", "成熟期", "衰退期", "过渡阶段"],
            ["证据"],
            ["反证", "反向证据", "不支持"],
            ["置信度", "信心"],
            target_terms,
        ],
        errors,
    )


def require_multibusiness_split_columns(text: str, errors: list[str]) -> None:
    """
    检查多业务线中观拆分是否包含必需列.

    :param text: Markdown 文本.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    require_evidence_table_columns(
        text,
        "### 4.0 多业务线中观拆分",
        [
            ["业务线", "行业线"],
            ["行业阶段", "阶段"],
            ["竞争格局", "竞争结构"],
            ["关键指标", "景气信号"],
            ["对目标公司的含义", "目标公司", "含义"],
        ],
        errors,
    )


def require_retrieval_gap_details(text: str, heading: str, errors: list[str]) -> None:
    """
    检查二次检索缺口是否说明缺口, 三轮闭环尝试, 状态, 未补齐原因, 影响, 下一步和来源.

    :param text: Markdown 文本.
    :param heading: 二次检索缺口章节标题.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    require_section_min(text, heading, 120, errors)
    require_any_terms(
        text,
        heading,
        [
            ["缺少", "缺口", "待检索", "待验证", "未取得"],
            ["为什么", "影响", "重要"],
            ["三轮", "闭环", "第1轮", "第一轮"],
            ["第2轮", "第二轮"],
            ["第3轮", "第三轮"],
            ["已尝试", "尝试来源", "检索已尝试"],
            ["当前状态", "缺口闭环状态", "部分补齐", "仍未补齐", "已补齐"],
            ["未补齐原因", "不可访问", "付费库", "需要登录", "公开检索无可靠结果", "无可靠结果", "口径不匹配"],
            ["下一步", "查证", "验证", "核验"],
            ["一手", "近一手", "官方", "公司公告", "财报", "IR", "交易所", "监管", "行业协会", "可信数据库"],
        ],
        errors,
    )
    require_evidence_table_columns(
        text,
        heading,
        [
            ["缺口"],
            ["三轮闭环已尝试", "三轮检索已尝试", "已尝试", "尝试来源"],
            ["当前状态", "状态"],
            ["为什么仍重要", "为什么重要", "影响"],
            ["未补齐原因", "原因"],
            ["下一步来源", "下一步"],
        ],
        errors,
    )


def require_company_compliance_checklist(text: str, errors: list[str]) -> None:
    """
    检查公司报告合规自检表是否覆盖关键概念.

    :param text: Markdown 文本.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    require_section_min(text, "## 17. 报告合规自检表", 240, errors)
    require_any_terms(
        text,
        "## 17. 报告合规自检表",
        [
            ["模板骨架", "skeleton"],
            ["研究简报", "research brief"],
            ["Deep Research"],
            ["分析层级", "层级选择", "layer"],
            ["七个核心模块", "七模块"],
            ["资本市场"],
            ["来源质量", "证据等级", "evidence"],
            ["一手来源", "primary"],
            ["事实/观点/推断", "事实, 观点和推断"],
            ["后续验证"],
        ],
        errors,
    )


def require_company_pressure_test(text: str, errors: list[str]) -> None:
    """
    检查公司报告压力测试章节是否覆盖核心视角.

    :param text: Markdown 文本.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    require_section_min(text, "## 12. 多视角压力测试", 220, errors)
    require_any_terms(
        text,
        "## 12. 多视角压力测试",
        [
            ["行业专家"],
            ["投资研究员"],
            ["政策/监管", "政策研究者", "监管研究者"],
            ["经营者", "创业者"],
        ],
        errors,
    )


def require_company_macro_meso_depth(text: str, errors: list[str]) -> None:
    """
    检查公司报告宏观和中观章节是否过薄.

    :param text: Markdown 文本.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    require_section_min(text, "## 3. 宏观环境分析", 240, errors)
    require_any_terms(
        text,
        "## 3. 宏观环境分析",
        [
            ["政策", "监管"],
            ["经济", "消费", "利率", "汇率", "通胀", "风险偏好"],
            ["技术", "成本", "周期"],
        ],
        errors,
    )
    require_section_min(text, "## 4. 中观行业分析", 420, errors)
    require_any_terms(
        text,
        "## 4. 中观行业分析",
        [
            ["行业定义", "行业一句话定义"],
            ["关键指标", "市场规模", "增速", "渗透率"],
            ["行业地图", "产业链"],
            ["生命周期"],
        ],
        errors,
    )


def require_company_micro_depth(text: str, errors: list[str]) -> None:
    """
    检查公司报告微观章节是否过薄.

    :param text: Markdown 文本.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    require_section_min(text, "## 6. 微观公司/产品分析", 260, errors)
    require_any_terms(
        text,
        "## 6. 微观公司/产品分析",
        [
            ["商业模式"],
            ["产品", "服务"],
            ["客户", "渠道"],
            ["财务", "运营", "收入", "利润", "现金流"],
            ["护城河", "竞争位置", "竞争优势"],
        ],
        errors,
    )


def require_company_risk_and_verification_depth(text: str, errors: list[str]) -> None:
    """
    检查风险机会和后续验证章节是否具备决策价值.

    :param text: Markdown 文本.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    require_section_min(text, "## 13. 风险和机会", 220, errors)
    require_any_terms(
        text,
        "## 13. 风险和机会",
        [
            ["风险"],
            ["机会"],
            ["行业结构", "行业"],
            ["目标公司", "目标产品", "公司", "产品"],
        ],
        errors,
    )
    require_section_min(text, "## 16. 附录: 后续验证清单", 180, errors)
    require_any_terms(
        text,
        "## 16. 附录: 后续验证清单",
        [
            ["待验证", "验证"],
            ["为什么重要", "重要"],
            ["推荐来源", "来源"],
            ["优先级"],
        ],
        errors,
    )


def check_company(text: str, capital: bool) -> list[str]:
    """
    检查公司或资本市场报告.

    :param text: Markdown 文本.
    :param capital: 是否按上市公司资本市场报告检查.
    :return: 错误列表.
    """
    errors: list[str] = []
    require_report_shell(text, "## 0. 研报前置区", errors)
    require_report_min_length(text, 12000 if capital else 10000, errors)
    require_mermaid_block(text, errors)
    require_headings(text, COMPANY_CORE_HEADINGS, errors)
    require_company_exhibit_list(text, errors)
    require_company_report_front_density(text, errors)
    require_company_core_metrics_overview(text, errors)
    require_company_research_trace_density(text, errors)
    require_source_matrix_columns(text, "### 2.2 来源矩阵和证据质量", errors)
    require_retrieval_gap_details(text, "### 2.3 二次检索缺口", errors)
    require_fact_inference_columns(text, "## 10. 事实, 观点和推断分层", errors)
    require_company_compliance_checklist(text, errors)
    require_company_pressure_test(text, errors)
    require_company_macro_meso_depth(text, errors)
    require_company_micro_depth(text, errors)
    require_company_risk_and_verification_depth(text, errors)
    require_lifecycle_depth(text, "### 4.4 生命周期判断", ["目标公司", "目标产品", "目标"], errors)
    require_company_module_verification_blocks(text, errors)
    if capital:
        require_headings(text, CAPITAL_MARKET_HEADINGS, errors)
        require_multibusiness_split_columns(text, errors)
        require_section_min(text, "## 11. 资本市场表现与估值预期变化", 1500, errors)
        require_capital_section_paragraph_density(text, errors)
        require_capital_section_concepts(text, errors)
    for idx in range(1, 8):
        heading = [
            "### 5.1 可行性",
            "### 5.2 规模性",
            "### 5.3 防守性",
            "### 5.4 盈利性",
            "### 5.5 估值",
            "### 5.6 外部因素",
            "### 5.7 景气度",
        ][idx - 1]
        minimum = 450 if capital and idx >= 4 else 250
        require_section_min(text, heading, minimum, errors)
        require_labels(text, heading, ["结论", "依据", "机制", "对目标公司/产品的影响"], errors)
    if capital:
        require_capital_priority_depth_blocks(text, errors)
    return errors


def check_overview(text: str) -> list[str]:
    """
    检查行业全览报告.

    :param text: Markdown 文本.
    :return: 错误列表.
    """
    errors: list[str] = []
    require_report_shell(text, "## 1. 行业一句话定义", errors)
    require_report_min_length(text, 8000, errors)
    require_mermaid_block(text, errors)
    require_headings(text, OVERVIEW_HEADINGS, errors)
    require_source_matrix_columns(text, "### 2.2 来源矩阵和证据质量", errors)
    require_retrieval_gap_details(text, "### 2.3 二次检索缺口", errors)
    require_fact_inference_columns(text, "## 8. 事实, 观点和推断分层", errors)
    require_lifecycle_depth(text, "## 4. 生命周期判断", ["行业含义", "行业"], errors)
    if first_nonempty_line(text) == "## 0. 研报前置区":
        errors.append("wrong opening: industry overview must not use company front matter")
    for heading in [
        "### 5.1 可行性",
        "### 5.2 规模性",
        "### 5.3 防守性",
        "### 5.4 盈利性",
        "### 5.5 估值",
        "### 5.6 外部因素",
        "### 5.7 景气度",
    ]:
        require_section_min(text, heading, 180, errors)
        require_labels(text, heading, ["结论", "证据", "机制", "行业含义"], errors)
    return errors


def check_specific(text: str) -> list[str]:
    """
    检查行业具体问题报告.

    :param text: Markdown 文本.
    :return: 错误列表.
    """
    errors: list[str] = []
    require_report_shell(text, "## 1. 直接回答", errors)
    require_report_min_length(text, 8000, errors)
    require_mermaid_block(text, errors)
    require_headings(text, SPECIFIC_HEADINGS, errors)
    require_source_matrix_columns(text, "### 3.2 来源矩阵和证据质量", errors)
    require_retrieval_gap_details(text, "### 3.3 二次检索缺口", errors)
    require_specific_evidence_chain_columns(text, errors)
    require_lifecycle_depth(text, "## 7. 生命周期判断", ["问题含义", "用户问题", "该问题"], errors)
    require_section_min(text, "## 1. 直接回答", 250, errors)
    for heading in [
        "### 8.1 可行性",
        "### 8.2 规模性",
        "### 8.3 防守性",
        "### 8.4 盈利性",
        "### 8.5 估值",
        "### 8.6 外部因素",
        "### 8.7 景气度",
    ]:
        require_section_min(text, heading, 150, errors)
        require_labels(text, heading, ["结论", "证据", "机制", "对该问题的含义"], errors)
    return errors


def check_prompt_builder(text: str) -> list[str]:
    """
    检查 Prompt Builder 输出.

    :param text: Markdown 文本.
    :return: 错误列表.
    """
    errors: list[str] = []
    required_terms = [
        "报告路由",
        "必须使用",
        "结构要求",
        "必需章节",
        "深度要求",
        "目标字数",
        "证据要求",
        "一手来源优先",
        "合规要求",
        "重写",
    ]
    for term in required_terms:
        if term not in text:
            errors.append(f"missing prompt-builder term: {term}")
    for term in [
        "研究计划摘要",
        "来源矩阵",
        "二次检索缺口",
        "事实/观点/推断",
        "压力测试",
        "报告合规自检表",
    ]:
        if term not in text:
            errors.append(f"missing prompt-builder report contract: {term}")
    if "公司/产品" in text or "公司产品" in text or "company-product-template" in text:
        for term in ["0. 研报前置区", "5.1", "5.7", "微观公司/产品分析"]:
            if term not in text:
                errors.append(f"missing company prompt-builder contract: {term}")
    if "资本市场" in text or "股价" in text or "上市公司" in text:
        for term in ["11.1", "11.2", "11.3", "11.4", "不构成投资建议"]:
            if term not in text:
                errors.append(f"missing capital prompt-builder contract: {term}")
    if "## 0. 研报前置区" in text and "请使用 industry-research skill" not in text:
        errors.append("prompt-builder appears to be writing the report directly")
    return errors


def check_short(text: str) -> list[str]:
    """
    检查显式短答输出.

    :param text: Markdown 文本.
    :return: 错误列表.
    """
    errors: list[str] = []
    length = rough_cjk_length(text)
    if length > 1800:
        errors.append(f"short answer too long: length {length}, expected <= 1800")
    if "## 0. 研报前置区" in text or "## 11. 报告合规自检表" in text:
        errors.append("short answer should not use full standard-report skeleton")
    return errors


def sample_prompt_builder_weak_contract() -> str:
    """
    构造缺少完整研报契约的 Prompt Builder 样例.

    :return: Prompt Builder 样例文本.
    """
    return "\n".join(
        [
            "请使用 industry-research skill 分析小米股价下跌.",
            "报告路由: 公司/产品加资本市场模块.",
            "必须使用: assets/company-product-template.md.",
            "结构要求: 写清楚为什么下跌和后续怎么看.",
            "深度要求: 尽量详细.",
            "证据要求: 使用可靠来源.",
            "合规要求: 不构成投资建议.",
        ]
    )


def run_profile(text: str, profile: str, language: str = "auto") -> list[str]:
    """
    按指定 profile 运行检查.

    :param text: Markdown 文本.
    :param profile: 检查 profile.
    :param language: 报告语言, 可为 `auto`, `zh` 或 `en`.
    :return: 错误列表.
    """
    resolved_language = detect_report_language(text) if language == "auto" else language
    language_errors = require_language_consistency(text, resolved_language)
    normalized_text = normalize_report_contract(text, resolved_language)
    resolved_profile = detect_profile(normalized_text) if profile == "auto" else profile
    if resolved_profile == "unknown":
        return language_errors + ["could not auto-detect report profile"]
    field_errors = validate_canonical_fields(text, resolved_profile, resolved_language)
    if field_errors:
        return language_errors + field_errors
    if resolved_profile == "company-capital":
        errors = check_company(normalized_text, capital=True)
    elif resolved_profile == "company":
        errors = check_company(normalized_text, capital=False)
    elif resolved_profile == "overview":
        errors = check_overview(normalized_text)
    elif resolved_profile == "specific":
        errors = check_specific(normalized_text)
    elif resolved_profile == "prompt-builder":
        errors = check_prompt_builder(normalized_text)
    elif resolved_profile == "short":
        errors = check_short(normalized_text)
    else:
        raise ValueError(f"unknown profile: {resolved_profile}")
    return language_errors + errors


def detect_profile(text: str) -> str:
    """
    自动识别报告 profile.

    :param text: Markdown 文本.
    :return: 识别出的 profile, 无法识别时返回 unknown.
    """
    if all(term in text for term in ["报告路由", "必须使用", "结构要求", "深度要求", "证据要求", "合规要求"]):
        return "prompt-builder"
    if "## 0. 研报前置区" in text:
        if "## 11. 资本市场表现与估值预期变化" in text:
            return "company-capital"
        return "company"
    if "## 1. 直接回答" in text:
        return "specific"
    if "## 1. 行业一句话定义" in text and "## 3. 行业地图" in text:
        return "overview"
    if rough_cjk_length(text) <= 1800 and "## " not in text:
        return "short"
    return "unknown"


def sample_overview_report(body_repeat: int) -> str:
    """
    构造行业全览报告样例.

    :param body_repeat: 普通章节重复次数, 用于控制整篇长度.
    :return: Markdown 样例文本.
    """
    body = "行业研究边界来源证据行业地图生命周期事实观点推断压力测试合规检查" * body_repeat
    source_matrix_body = "\n".join(
        [
            "| 来源类型 | 本报告用途 | 证据层级 | 检索状态 | 限制 |",
            "|---|---|---|---|---|",
            "| 官方统计/监管/行业协会 | 市场, 政策, 供需, 价格 | 一手/近一手 | 已取得/待检索 | 口径或时效限制 |",
            "| 可信数据库/国际组织/行业报告 | 趋势, 预测, 对比指标 | 近一手/二手 | 已尝试未取得 | 预测假设限制 |",
            "| 媒体/访谈/专家观点 | 补充信号和观点 | 二手/弱证据 | 待交叉验证 | 不能替代一手事实 |",
            body,
        ]
    )
    fact_inference_body = "\n".join(
        [
            "| 类型 | 内容 | 来源/依据 | 证据层级 | 来源状态 | 置信度 |",
            "|---|---|---|---|---|---|",
            "| 事实 | 行业事实 | 官方统计 | 一手 | 已取得 | 高 |",
            "| 观点 | 专家观点 | 访谈或报告 | 二手 | 待交叉验证 | 中 |",
            "| 推断 | 趋势推断 | 基于事实和观点 | 混合证据 | 受缺口影响 | 中 |",
            body,
        ]
    )
    lifecycle_body = "\n\n".join(
        [
            "**阶段结论:** " + "行业处于成长期向成熟期过渡阶段, 需求仍增长但竞争结构开始分化." * 8,
            "**证据:** " + "市场规模, 渗透率, 供需关系和竞争格局仍有增长信号, 但价格和利润率压力已经出现." * 8,
            "**反证:** " + "如果监管口径, 替代品扩张或需求放缓数据持续恶化, 生命周期可能更接近成熟期." * 8,
            "**置信度:** " + "中等, 因为关键行业数据仍需要官方统计, 行业协会和可信数据库继续验证." * 8,
            "**行业含义:** " + "七模块应更重视盈利性, 防守性和景气度拐点." * 8,
        ]
    )
    retrieval_gap_body = "\n".join(
        [
            "| 缺口 | 三轮闭环已尝试 | 当前状态 | 为什么仍重要 | 未补齐原因 | 下一步来源 |",
            "|---|---|---|---|---|---|",
            "| 最新市场规模, 渗透率, 价格变化和供需数据 | 第1轮: 官方统计和监管文件. 第2轮: 行业协会和可信数据库. 第3轮: 替代关键词, 本地语言和可信二手交叉验证 | 部分补齐/仍未补齐 | 这些缺口会影响行业生命周期, 七模块权重和风险机会判断 | 部分数据库需要付费库或登录, 公开检索无可靠结果, 口径不匹配 | 官方统计, 行业协会, 监管公告, 可信数据库 |",
            body,
        ]
    )
    mermaid_body = "\n".join(
        [
            "```mermaid",
            "flowchart LR",
            "  A[上游供给] --> B[中游生产]",
            "  B --> C[渠道]",
            "  C --> D[终端需求]",
            "```",
            body,
        ]
    )
    module_body = "\n\n".join(
        [
            "**结论:** " + "结论内容" * 25,
            "**证据:** " + "证据内容" * 25,
            "**机制:** " + "机制内容" * 25,
            "**行业含义:** " + "行业含义" * 25,
        ]
    )
    pressure_test_body = "\n".join(
        [
            "| 视角 | 质疑 | 影响 | 需要验证 |",
            "|---|---|---|---|",
            "| 行业专家 | 行业判断可能过于乐观 | 影响行业结论 | 验证行业数据 |",
            body,
        ]
    )
    compliance_body = "\n".join(
        [
            "| 检查项 | 是否通过 | 说明 |",
            "|---|---|---|",
            "| 行业全览模板完整 | 通过 | 结构完整 |",
            body,
        ]
    )
    parts: list[str] = [
        "# 示例行业研究报告",
        "## 1. 行业一句话定义",
        body,
        "## 2. 研究边界",
        body,
        "### 2.1 研究计划摘要",
        body,
        "### 2.2 来源矩阵和证据质量",
        source_matrix_body,
        "### 2.3 二次检索缺口",
        retrieval_gap_body,
        "## 3. 行业地图",
        mermaid_body,
        "## 4. 生命周期判断",
        lifecycle_body,
        "## 5. 七个核心模块",
    ]
    for heading in [
        "### 5.1 可行性",
        "### 5.2 规模性",
        "### 5.3 防守性",
        "### 5.4 盈利性",
        "### 5.5 估值",
        "### 5.6 外部因素",
        "### 5.7 景气度",
    ]:
        parts.extend([heading, module_body])
    parts.extend(
        [
        "## 8. 事实, 观点和推断分层",
        fact_inference_body,
            "## 9. 多视角压力测试",
            pressure_test_body,
            "## 11. 报告合规自检表",
            compliance_body,
            "本报告仅供研究和信息参考, 不构成投资建议, 也不构成任何收益承诺.",
        ]
    )
    return "\n\n".join(parts)


def sample_specific_report(body_repeat: int) -> str:
    """
    构造行业具体问题报告样例.

    :param body_repeat: 普通章节重复次数, 用于控制整篇长度.
    :return: Markdown 样例文本.
    """
    body = "直接回答结论摘要研究边界来源证据行业地图议题树证据链生命周期压力测试合规" * body_repeat
    direct_answer = "直接回答证据机制行业问题含义来源缺口后续验证" * max(body_repeat, 12)
    source_matrix_body = "\n".join(
        [
            "| 来源类型 | 本报告用途 | 证据层级 | 检索状态 | 限制 |",
            "|---|---|---|---|---|",
            "| 官方统计/监管/行业协会 | 市场, 政策, 供需, 价格 | 一手/近一手 | 已取得/待检索 | 口径或时效限制 |",
            "| 可信数据库/国际组织/行业报告 | 趋势, 预测, 对比指标 | 近一手/二手 | 已尝试未取得 | 预测假设限制 |",
            "| 媒体/访谈/专家观点 | 补充信号和观点 | 二手/弱证据 | 待交叉验证 | 不能替代一手事实 |",
            body,
        ]
    )
    evidence_chain_body = "\n".join(
        [
            "| 子问题 | 结论 | 事实 | 观点 | 推断 | 证据层级 | 来源状态 | 置信度 |",
            "|---|---|---|---|---|---|---|---|",
            "| 子问题 | 结论 | 事实 | 观点 | 推断 | 一手/近一手/二手 | 已取得/待检索 | 中 |",
            body,
        ]
    )
    lifecycle_body = "\n\n".join(
        [
            "**阶段结论:** " + "与用户问题相关的行业环节处于成长期向成熟期过渡阶段, 增长仍在但竞争和利润压力上升." * 8,
            "**证据:** " + "需求指标, 供给扩张, 价格变化和政策信号共同说明行业仍有增量, 但边际变化正在变复杂." * 8,
            "**反证:** " + "如果后续数据证明需求已经放缓, 库存上升或政策收紧, 当前阶段判断需要下修为成熟期压力." * 8,
            "**置信度:** " + "中等, 因为仍需验证官方统计, 行业协会和企业经营数据." * 8,
            "**对该问题的含义:** " + "解释原因时不能只看短期事件, 还要看生命周期切换." * 8,
        ]
    )
    retrieval_gap_body = "\n".join(
        [
            "| 缺口 | 三轮闭环已尝试 | 当前状态 | 为什么仍重要 | 未补齐原因 | 下一步来源 |",
            "|---|---|---|---|---|---|",
            "| 与用户问题直接相关的最新行业指标, 政策口径和供需变化数据 | 第1轮: 官方统计和监管文件. 第2轮: 行业协会, 公司公告和可信数据库. 第3轮: 替代关键词, 本地语言和可信二手交叉验证 | 部分补齐/仍未补齐 | 这些缺口会影响直接回答, 议题树排序和证据链置信度 | 部分来源需要登录或付费库, 公开检索无可靠结果, 口径不匹配 | 官方统计, 监管公告, 行业协会数据, 公司公告和可信数据库 |",
            body,
        ]
    )
    mermaid_body = "\n".join(
        [
            "```mermaid",
            "flowchart LR",
            "  P[问题驱动因素] --> I[行业结构]",
            "  I --> E[证据链]",
            "  E --> J[结论]",
            "```",
            body,
        ]
    )
    module_body = "\n\n".join(
        [
            "**结论:** " + "结论内容" * 20,
            "**证据:** " + "证据内容" * 20,
            "**机制:** " + "机制内容" * 20,
            "**对该问题的含义:** " + "问题含义" * 20,
        ]
    )
    pressure_test_body = "\n".join(
        [
            "| 视角 | 质疑 | 影响 | 需要验证 |",
            "|---|---|---|---|",
            "| 行业专家 | 问题判断可能过于乐观 | 影响直接回答 | 验证行业数据 |",
            body,
        ]
    )
    compliance_body = "\n".join(
        [
            "| 检查项 | 是否通过 | 说明 |",
            "|---|---|---|",
            "| 行业具体问题模板完整 | 通过 | 结构完整 |",
            body,
        ]
    )
    parts: list[str] = [
        "# 示例行业问题研究报告",
        "## 1. 直接回答",
        direct_answer,
        "## 2. 结论摘要",
        body,
        "## 3. 研究边界",
        body,
        "### 3.1 研究计划摘要",
        body,
        "### 3.2 来源矩阵和证据质量",
        source_matrix_body,
        "### 3.3 二次检索缺口",
        retrieval_gap_body,
        "## 4. 行业地图",
        mermaid_body,
        "## 5. 问题拆解和议题树",
        body,
        "## 6. 证据链分析",
        evidence_chain_body,
        "## 7. 生命周期判断",
        lifecycle_body,
        "## 8. 七个核心模块分析",
    ]
    for heading in [
        "### 8.1 可行性",
        "### 8.2 规模性",
        "### 8.3 防守性",
        "### 8.4 盈利性",
        "### 8.5 估值",
        "### 8.6 外部因素",
        "### 8.7 景气度",
    ]:
        parts.extend([heading, module_body])
    parts.extend(
        [
            "## 9. 多视角压力测试",
            pressure_test_body,
            "## 12. 报告合规自检表",
            compliance_body,
            "本报告仅供研究和信息参考, 不构成投资建议, 也不构成任何收益承诺.",
        ]
    )
    return "\n\n".join(parts)


def sample_company_capital_without_priority_block() -> str:
    """
    构造缺少资本市场优先模块第五块的样例.

    :return: Markdown 样例文本.
    """
    module_body = "\n\n".join(
        [
            "**结论:** " + "结论内容" * 60,
            "**依据:** " + "依据内容" * 60,
            "**机制:** " + "机制内容" * 60,
            "**对目标公司/产品的影响:** " + "影响内容" * 60,
        ]
    )
    long_body = "分析内容" * 260
    source_matrix_body = "\n".join(
        [
            "| 来源类型 | 本报告用途 | 证据等级 | 一手来源状态 | 缺口处理 |",
            "|---|---|---|---|---|",
            "| 公司公告/财报/IR/交易所文件 | 公司和财务事实 | 高 | 已取得/待检索 | 标记缺口和下一步来源 |",
            "| 交易所/可信市场数据库 | 股价, 估值, 市值, 交易表现 | 高/中 | 已尝试未取得 | 说明行情口径限制 |",
            "| 可信数据库/行业报告 | 趋势, 预测, 对比指标 | 中高 | 待检索 | 标记预测假设 |",
            "| 媒体/访谈/专家观点 | 补充信号和观点 | 中/低 | 二手来源 | 必须交叉验证 |",
            long_body,
        ]
    )
    fact_inference_body = "\n".join(
        [
            "| 类型 | 内容 | 来源/依据 | 证据层级 | 一手来源状态 | 置信度 |",
            "|---|---|---|---|---|---|",
            "| 事实 | 公司财务和运营事实 | 公司公告或财报 | 一手/近一手 | 已取得/待检索 | 高 |",
            "| 待核验事实 | 二手行情或媒体转述数据 | 市场数据库或媒体 | 二手/弱证据 | 待核验 | 中 |",
            "| 观点 | 分析师或媒体观点 | 来源立场 | 二手 | 待交叉验证 | 中 |",
            "| 推断 | 估值和预期差判断 | 基于事实和观点 | 混合证据 | 受缺口影响 | 中 |",
            long_body,
        ]
    )
    retrieval_gap_body = "\n".join(
        [
            "| 缺口 | 三轮闭环已尝试 | 当前状态 | 为什么仍重要 | 未补齐原因 | 下一步来源 |",
            "|---|---|---|---|---|---|",
            "| 目标公司分业务线收入, 毛利率, 现金流, 订单交付, 股价区间和估值倍数的最新一手口径 | 第1轮: 公司公告, 财报和 IR 材料. 第2轮: 交易所文件, 交易所行情和可信市场数据库. 第3轮: 替代关键词, 本地语言和可信二手交叉验证 | 部分补齐/仍未补齐 | 这些缺口会影响基本面变化, 估值锚, 市场预期差和资本市场情景判断 | 部分行情和一致预期需要付费库或登录, 公开检索无可靠结果 | 公司公告, 财报, IR, 交易所, 监管公告, 官方行业数据和可信数据库 |",
            long_body,
        ]
    )
    exhibit_list_body = "\n".join(
        [
            "| 图表 | 类型 | 用途 |",
            "|---|---|---|",
            "| 图表 1: 行业地图和目标位置 | Mermaid | 展示产业链, 横向竞争和目标位置 |",
            "| 图表 2: 核心指标总览 | 表格 | 展示行业和目标公司的关键读数 |",
            "| 图表 3: 七模块判断矩阵 | 表格 | 展示七模块结论和证据等级 |",
            "| 图表 4: 竞争对手对比 | 表格 | 展示目标公司与主要玩家差异 |",
        ]
    )
    exhibit_list_body = "\n".join(
        [
            "| 图表 | 类型 | 用途 |",
            "|---|---|---|",
            "| 图表 1: 行业地图和目标位置 | Mermaid | 展示产业链, 横向竞争和目标位置 |",
            "| 图表 2: 核心指标总览 | 表格 | 展示行业和目标公司的关键读数 |",
            "| 图表 3: 七模块判断矩阵 | 表格 | 展示七模块结论和证据等级 |",
            "| 图表 4: 竞争对手对比 | 表格 | 展示目标公司与主要玩家差异 |",
        ]
    )
    macro_body = "\n\n".join(
        [
            "政策和监管变量会影响行业准入, 合规成本和资本市场风险偏好." * 25,
            "经济, 消费, 利率, 汇率和通胀变量会影响需求弹性, 资金成本和估值折现." * 25,
            "技术周期和成本周期会影响产品迭代, 供应链压力和利润率弹性." * 25,
        ]
    )
    meso_body = "\n\n".join(
        [
            "行业定义需要明确本报告口径, 并解释目标公司所在细分行业和相邻替代品." * 25,
            "关键指标包括市场规模, 增速, 渗透率, 供需关系, 价格成本和政策监管变量." * 25,
            "行业地图和产业链用于定位上游, 中游, 渠道, 客户和目标公司位置." * 25,
            "生命周期判断需要说明行业阶段, 证据, 反证和对目标公司的含义." * 25,
        ]
    )
    mermaid_map_body = "\n".join(
        [
            "```mermaid",
            "flowchart LR",
            "  U[上游供应链] --> M[中游制造和服务]",
            "  M --> C[渠道和客户]",
            "  C --> T[目标公司/产品]",
            "  T --> E[生态和资本市场预期]",
            "```",
            "行业地图和目标位置需要结合产业链, 横向竞争, 目标公司位置和关键流向解释." * 30,
        ]
    )
    lifecycle_body = "\n\n".join(
        [
            "**阶段结论:** " + "目标公司所在关键业务线处于成长期向成熟期过渡阶段, 新业务仍有增长弹性, 传统业务更接近成熟竞争." * 8,
            "**证据:** " + "行业规模, 渗透率, 订单或交付, 价格竞争, 毛利率和监管信号共同支持这一阶段判断." * 8,
            "**反证:** " + "如果后续需求转弱, 价格战加剧, 监管约束升级或目标公司交付质量下降, 阶段判断可能更接近成熟期压力." * 8,
            "**置信度:** " + "中等, 因为仍需用公司公告, 官方行业数据和交易所信息验证." * 8,
            "**对目标公司/产品的影响:** " + "估值和盈利性需要按不同业务线加权, 不能只交易单一成长叙事." * 8,
        ]
    )
    mermaid_map_body = "\n".join(
        [
            "```mermaid",
            "flowchart LR",
            "  U[上游供应链] --> M[中游制造和服务]",
            "  M --> C[渠道和客户]",
            "  C --> T[目标公司/产品]",
            "  T --> E[生态和资本市场预期]",
            "```",
            "行业地图和目标位置需要结合产业链, 横向竞争, 目标公司位置和关键流向解释." * 30,
        ]
    )
    lifecycle_body = "\n\n".join(
        [
            "**阶段结论:** " + "目标公司所在关键业务线处于成长期向成熟期过渡阶段, 新业务仍有增长弹性, 传统业务更接近成熟竞争." * 8,
            "**证据:** " + "行业规模, 渗透率, 订单或交付, 价格竞争, 毛利率和监管信号共同支持这一阶段判断." * 8,
            "**反证:** " + "如果后续需求转弱, 价格战加剧, 监管约束升级或目标公司交付质量下降, 阶段判断可能更接近成熟期压力." * 8,
            "**置信度:** " + "中等, 因为仍需用公司公告, 官方行业数据和交易所信息验证." * 8,
            "**对目标公司/产品的影响:** " + "估值和盈利性需要按不同业务线加权, 不能只交易单一成长叙事." * 8,
        ]
    )
    multibusiness_body = "\n".join(
        [
            "| 业务线/行业线 | 行业阶段 | 竞争格局 | 关键指标/景气信号 | 对目标公司的含义 |",
            "|---|---|---|---|---|",
            "| 智能手机 | 成熟竞争阶段 | 头部集中但价格竞争强 | 出货量, ASP, 毛利率, 渠道库存 | 对目标公司的现金流和品牌基本盘有稳定意义 |",
            "| AIoT/消费电子生态 | 成熟增长阶段 | 品类分散, 生态协同重要 | 连接设备数, 用户活跃, 品类毛利 | 对目标公司的生态粘性和交叉销售有影响 |",
            "| 互联网服务 | 成熟变现阶段 | 依赖硬件用户基础和广告环境 | ARPU, MAU, 广告收入, 游戏收入 | 对目标公司的利润率和估值稳定性有影响 |",
            "| 智能 EV | 导入到成长期 | 竞争激烈且监管安全要求高 | 订单, 交付, 毛利率, 召回投诉 | 对目标公司的成长叙事和资本市场预期影响最大 |",
        ]
    )
    micro_body = "\n\n".join(
        [
            "商业模式分析说明目标公司如何创造收入, 承担成本, 形成用户粘性和复购." * 25,
            "产品和服务分析说明核心产品线, 差异化卖点, 技术路线和用户价值." * 25,
            "客户和渠道分析说明目标客群, 渠道结构, 线上线下触点和获客效率." * 25,
            "财务和运营指标分析说明收入, 利润, 现金流, 交付, 库存和费用率变化." * 25,
            "护城河和竞争位置分析说明品牌, 供应链, 数据, 软件生态和替代风险." * 25,
        ]
    )
    parts: list[str] = [
        "# 示例公司基本面和资本市场研究报告",
        "## 0. 研报前置区",
        "### 0.1 报告摘要",
        long_body,
        "### 0.2 关键结论",
        long_body,
        "### 0.3 核心指标总览",
        long_body,
        "### 0.4 图表清单或图表占位",
        exhibit_list_body,
        "## 1. 直接结论",
        long_body,
        "## 2. 研究边界",
        long_body,
        "### 2.1 研究计划摘要",
        long_body,
        "### 2.2 来源矩阵和证据质量",
        source_matrix_body,
        "### 2.3 二次检索缺口",
        retrieval_gap_body,
        "## 3. 宏观环境分析",
        macro_body,
        "## 4. 中观行业分析",
        meso_body,
        "### 4.0 多业务线中观拆分",
        multibusiness_body,
        "### 4.3 行业地图和目标位置",
        mermaid_map_body,
        "### 4.4 生命周期判断",
        lifecycle_body,
        "## 5. 七个核心模块加权分析",
    ]
    for heading in [
        "### 5.1 可行性",
        "### 5.2 规模性",
        "### 5.3 防守性",
        "### 5.4 盈利性",
        "### 5.5 估值",
        "### 5.6 外部因素",
        "### 5.7 景气度",
    ]:
        parts.extend([heading, module_body])
    parts.extend(
        [
            "## 6. 微观公司/产品分析",
            long_body,
            "## 10. 事实, 观点和推断分层",
            long_body,
            "## 11. 资本市场表现与估值预期变化",
            "### 11.1 股价表现拆解",
            long_body,
            "### 11.2 基本面变化",
            long_body,
            "### 11.3 估值逻辑和市场预期差",
            long_body,
            "### 11.4 上涨触发器, 下跌风险和情景分析",
            long_body,
            "## 12. 多视角压力测试",
            long_body,
            "## 13. 风险和机会",
            long_body,
            "## 15. 方法论和数据来源说明",
            long_body,
            "## 16. 附录: 后续验证清单",
            long_body,
            "## 17. 报告合规自检表",
            long_body,
        ]
    )
    return "\n\n".join(parts)


def sample_company_capital_single_paragraph_section_11() -> str:
    """
    构造第 11 章长度足够但段落密度不足的样例.

    :return: Markdown 样例文本.
    """
    module_body = "\n\n".join(
        [
            "**结论:** " + "结论内容" * 60,
            "**依据:** " + "依据内容" * 60,
            "**机制:** " + "机制内容" * 60,
            "**对目标公司/产品的影响:** " + "影响内容" * 60,
            "**关键指标和后续验证:** " + "指标验证" * 60,
        ]
    )
    long_body = "分析内容" * 260
    source_matrix_body = "\n".join(
        [
            "| 来源类型 | 本报告用途 | 证据等级 | 一手来源状态 | 缺口处理 |",
            "|---|---|---|---|---|",
            "| 公司公告/财报/IR/交易所文件 | 公司和财务事实 | 高 | 已取得/待检索 | 标记缺口和下一步来源 |",
            "| 交易所/可信市场数据库 | 股价, 估值, 市值, 交易表现 | 高/中 | 已尝试未取得 | 说明行情口径限制 |",
            "| 可信数据库/行业报告 | 趋势, 预测, 对比指标 | 中高 | 待检索 | 标记预测假设 |",
            "| 媒体/访谈/专家观点 | 补充信号和观点 | 中/低 | 二手来源 | 必须交叉验证 |",
            long_body,
        ]
    )
    fact_inference_body = "\n".join(
        [
            "| 类型 | 内容 | 来源/依据 | 证据层级 | 一手来源状态 | 置信度 |",
            "|---|---|---|---|---|---|",
            "| 事实 | 公司财务和运营事实 | 公司公告或财报 | 一手/近一手 | 已取得/待检索 | 高 |",
            "| 待核验事实 | 二手行情或媒体转述数据 | 市场数据库或媒体 | 二手/弱证据 | 待核验 | 中 |",
            "| 观点 | 分析师或媒体观点 | 来源立场 | 二手 | 待交叉验证 | 中 |",
            "| 推断 | 估值和预期差判断 | 基于事实和观点 | 混合证据 | 受缺口影响 | 中 |",
            long_body,
        ]
    )
    exhibit_list_body = "\n".join(
        [
            "| 图表 | 类型 | 用途 |",
            "|---|---|---|",
            "| 图表 1: 行业地图和目标位置 | Mermaid | 展示产业链和目标位置 |",
            "| 图表 2: 核心指标总览 | 表格 | 展示关键指标 |",
            "| 图表 3: 七模块判断矩阵 | 表格 | 展示七模块结论 |",
            "| 图表 4: 竞争对手对比 | 表格 | 展示竞争差异 |",
        ]
    )
    mermaid_map_body = "\n".join(
        [
            "```mermaid",
            "flowchart LR",
            "  A[上游] --> B[中游]",
            "  B --> C[目标公司/产品]",
            "```",
            "行业地图和目标位置说明." * 80,
        ]
    )
    lifecycle_body = "\n\n".join(
        [
            "阶段结论: 目标公司所在关键业务线处于成长期向成熟期过渡阶段." * 8,
            "证据: 行业规模, 渗透率, 价格竞争和监管信号支持阶段判断." * 8,
            "反证: 如果需求转弱或目标公司经营指标恶化, 阶段判断可能更接近成熟期压力." * 8,
            "置信度: 中等, 对目标公司的含义是估值和盈利性需要按生命周期阶段重新加权." * 8,
        ]
    )
    single_paragraph = "资本市场分析内容" * 180
    parts: list[str] = [
        "# 示例公司基本面和资本市场研究报告",
        "## 0. 研报前置区",
        "### 0.1 报告摘要",
        long_body,
        "### 0.2 关键结论",
        long_body,
        "### 0.3 核心指标总览",
        long_body,
        "### 0.4 图表清单或图表占位",
        exhibit_list_body,
        "## 1. 直接结论",
        long_body,
        "## 2. 研究边界",
        long_body,
        "### 2.1 研究计划摘要",
        long_body,
        "### 2.2 来源矩阵和证据质量",
        source_matrix_body,
        "### 2.3 二次检索缺口",
        long_body,
        "## 3. 宏观环境分析",
        long_body,
        "## 4. 中观行业分析",
        long_body,
        "### 4.0 多业务线中观拆分",
        long_body,
        "### 4.3 行业地图和目标位置",
        mermaid_map_body,
        "### 4.4 生命周期判断",
        lifecycle_body,
        "## 5. 七个核心模块加权分析",
    ]
    for heading in [
        "### 5.1 可行性",
        "### 5.2 规模性",
        "### 5.3 防守性",
        "### 5.4 盈利性",
        "### 5.5 估值",
        "### 5.6 外部因素",
        "### 5.7 景气度",
    ]:
        parts.extend([heading, module_body])
    parts.extend(
        [
            "## 6. 微观公司/产品分析",
            long_body,
            "## 10. 事实, 观点和推断分层",
            long_body,
            "## 11. 资本市场表现与估值预期变化",
            "### 11.1 股价表现拆解",
            single_paragraph,
            "### 11.2 基本面变化",
            single_paragraph,
            "### 11.3 估值逻辑和市场预期差",
            single_paragraph,
            "### 11.4 上涨触发器, 下跌风险和情景分析",
            single_paragraph,
            "## 12. 多视角压力测试",
            long_body,
            "## 13. 风险和机会",
            long_body,
            "## 15. 方法论和数据来源说明",
            long_body,
            "## 16. 附录: 后续验证清单",
            long_body,
            "## 17. 报告合规自检表",
            long_body,
        ]
    )
    return "\n\n".join(parts)


def sample_company_capital_pass() -> str:
    """
    构造可通过资本市场报告结构检查的样例.

    :return: Markdown 样例文本.
    """
    base_module_body = "\n\n".join(
        [
            "**结论:** " + "结论内容" * 60,
            "**依据:** " + "依据内容" * 60,
            "**机制:** " + "机制内容" * 60,
            "**对目标公司/产品的影响:** " + "影响内容" * 60,
            "**关键指标和后续验证:** " + "指标验证" * 60,
        ]
    )
    priority_module_body = "\n\n".join(
        [
            base_module_body,
            "**关键指标和后续验证:** " + "指标验证" * 60,
        ]
    )
    long_body = "分析内容" * 260
    source_matrix_body = "\n".join(
        [
            "| 来源类型 | 本报告用途 | 证据等级 | 一手来源状态 | 缺口处理 |",
            "|---|---|---|---|---|",
            "| 公司公告/财报/IR/交易所文件 | 公司和财务事实 | 高 | 已取得/待检索 | 标记缺口和下一步来源 |",
            "| 交易所/可信市场数据库 | 股价, 估值, 市值, 交易表现 | 高/中 | 已尝试未取得 | 说明行情口径限制 |",
            "| 可信数据库/行业报告 | 趋势, 预测, 对比指标 | 中高 | 待检索 | 标记预测假设 |",
            "| 媒体/访谈/专家观点 | 补充信号和观点 | 中/低 | 二手来源 | 必须交叉验证 |",
            long_body,
        ]
    )
    fact_inference_body = "\n".join(
        [
            "| 类型 | 内容 | 来源/依据 | 证据层级 | 一手来源状态 | 置信度 |",
            "|---|---|---|---|---|---|",
            "| 事实 | 公司财务和运营事实 | 公司公告或财报 | 一手/近一手 | 已取得/待检索 | 高 |",
            "| 待核验事实 | 二手行情或媒体转述数据 | 市场数据库或媒体 | 二手/弱证据 | 待核验 | 中 |",
            "| 观点 | 分析师或媒体观点 | 来源立场 | 二手 | 待交叉验证 | 中 |",
            "| 推断 | 估值和预期差判断 | 基于事实和观点 | 混合证据 | 受缺口影响 | 中 |",
            long_body,
        ]
    )
    exhibit_list_body = "\n".join(
        [
            "| 图表 | 类型 | 用途 |",
            "|---|---|---|",
            "| 图表 1: 行业地图和目标位置 | Mermaid | 展示产业链, 横向竞争和目标位置 |",
            "| 图表 2: 核心指标总览 | 表格 | 展示行业和目标公司的关键读数 |",
            "| 图表 3: 七模块判断矩阵 | 表格 | 展示七模块结论和证据等级 |",
            "| 图表 4: 竞争对手对比 | 表格 | 展示目标公司与主要玩家差异 |",
        ]
    )
    core_metrics_body = "\n".join(
        [
            "| 指标 | 行业读数 | 目标公司/产品读数 | 判断 | 证据/来源 |",
            "|---|---|---|---|---|",
            "| 市场规模 | 行业规模仍有增量空间, 但不同细分行业增长弹性不同 | 目标公司覆盖多个业务线, 需要按手机, IoT, 互联网服务和智能 EV 分别估算 | 空间存在但不能只用单一业务线外推 | 官方统计/行业协会/可信数据库 |",
            "| 增速/渗透率 | 行业增速和渗透率决定生命周期阶段 | 目标公司新业务增速高, 成熟业务增速较低 | 增长结构分化, 需要拆分判断 | 官方统计/行业协会/公司公告 |",
            "| 竞争强度 | 主要赛道竞争格局激烈, 价格和产品迭代压力较高 | 目标公司需要同时面对传统硬件玩家和新进入者 | 竞争强度会压缩估值溢价 | 行业数据库/同业公告/监管资料 |",
            "| 盈利水平 | 行业毛利率和利润率受价格战, 成本周期和规模效应影响 | 目标公司分部盈利能力不同, 新业务仍需验证稳定性 | 盈利水平是估值锚能否修复的核心变量 | 公司财报/同业财报/IR 材料 |",
            "| 景气度 | 订单, 交付, 库存, 价格和政策信号共同决定景气度 | 目标公司景气信号需要结合交付, 渠道库存和用户需求验证 | 景气度改善可支持预期修复, 反之会放大回撤 | 订单/交付/价格/库存指标 |",
            "| 关键风险 | 行业风险来自监管, 安全, 价格战, 技术路线和需求波动 | 目标公司风险集中在质量, 交付, 毛利率, 现金流和舆情 | 风险事件会提高折现率并影响资本市场预期 | 监管公告/召回平台/投诉数据 |",
        ]
    )
    section_11_1_body = "\n\n".join(
        [
            "股价和价格表现需要先界定时间窗口和时间区间, 对比指数, 板块和基准收益, 再拆分已知催化事件." * 25,
            "证据缺口和待核验事项包括交易所行情, 可信市场数据库, 板块指数口径和事件日期, 需要区分事实和推断." * 25,
        ]
    )
    section_11_2_body = "\n\n".join(
        [
            "基本面变化需要拆解收入, 营收, 利润, 毛利率, 利润率, 现金流, 交付, 订单和运营指标." * 25,
            "同时需要比较公司指引, 业务结构, 业务组合和市场预期变化, 区分基本面真实变化和预期变化." * 25,
        ]
    )
    section_11_3_body = "\n\n".join(
        [
            "估值逻辑需要说明估值锚, 市场预期差和之前定价的增长假设, 包括市场此前 priced in 的业务叙事." * 25,
            "重估, 杀估值, rerating 或 derating 机制来自增长假设, 利润率, 风险折现和资金风险偏好的变化." * 25,
            "后续需要重新证明的验证指标包括收入增速, 毛利率, 现金流, 订单交付, 质量风险和同业估值." * 25,
        ]
    )
    section_11_4_body = "\n\n".join(
        [
            "上涨触发器包括交付超预期, 利润率稳定, 风险事件缓和和估值锚修复. 下跌风险包括需求放缓, 价格战, 监管或质量事件." * 22,
            "情景分析需要列出乐观, 中性和悲观条件以及跟踪指标. 本节不是投资建议, 不构成投资建议, 也不承诺收益." * 22,
        ]
    )
    macro_body = "\n\n".join(
        [
            "政策和监管变量会影响行业准入, 合规成本和资本市场风险偏好." * 25,
            "经济, 消费, 利率, 汇率和通胀变量会影响需求弹性, 资金成本和估值折现." * 25,
            "技术周期和成本周期会影响产品迭代, 供应链压力和利润率弹性." * 25,
        ]
    )
    meso_body = "\n\n".join(
        [
            "行业定义需要明确本报告口径, 并解释目标公司所在细分行业和相邻替代品." * 25,
            "关键指标包括市场规模, 增速, 渗透率, 供需关系, 价格成本和政策监管变量." * 25,
            "行业地图和产业链用于定位上游, 中游, 渠道, 客户和目标公司位置." * 25,
            "生命周期判断需要说明行业阶段, 证据, 反证和对目标公司的含义." * 25,
        ]
    )
    mermaid_map_body = "\n".join(
        [
            "```mermaid",
            "flowchart LR",
            "  U[上游供应链] --> M[中游制造和服务]",
            "  M --> C[渠道和客户]",
            "  C --> T[目标公司/产品]",
            "  T --> E[生态和资本市场预期]",
            "```",
            "行业地图和目标位置需要结合产业链, 横向竞争, 目标公司位置和关键流向解释." * 30,
        ]
    )
    lifecycle_body = "\n\n".join(
        [
            "**阶段结论:** " + "目标公司所在关键业务线处于成长期向成熟期过渡阶段, 新业务仍有增长弹性, 传统业务更接近成熟竞争." * 8,
            "**证据:** " + "行业规模, 渗透率, 订单或交付, 价格竞争, 毛利率和监管信号共同支持这一阶段判断." * 8,
            "**反证:** " + "如果后续需求转弱, 价格战加剧, 监管约束升级或目标公司交付质量下降, 阶段判断可能更接近成熟期压力." * 8,
            "**置信度:** " + "中等, 因为仍需用公司公告, 官方行业数据和交易所信息验证." * 8,
            "**对目标公司/产品的影响:** " + "估值和盈利性需要按不同业务线加权, 不能只交易单一成长叙事." * 8,
        ]
    )
    multibusiness_body = "\n".join(
        [
            "| 业务线/行业线 | 行业阶段 | 竞争格局 | 关键指标/景气信号 | 对目标公司的含义 |",
            "|---|---|---|---|---|",
            "| 智能手机 | 成熟竞争阶段 | 头部集中但价格竞争强 | 出货量, ASP, 毛利率, 渠道库存 | 对目标公司的现金流和品牌基本盘有稳定意义 |",
            "| AIoT/消费电子生态 | 成熟增长阶段 | 品类分散, 生态协同重要 | 连接设备数, 用户活跃, 品类毛利 | 对目标公司的生态粘性和交叉销售有影响 |",
            "| 互联网服务 | 成熟变现阶段 | 依赖硬件用户基础和广告环境 | ARPU, MAU, 广告收入, 游戏收入 | 对目标公司的利润率和估值稳定性有影响 |",
            "| 智能 EV | 导入到成长期 | 竞争激烈且监管安全要求高 | 订单, 交付, 毛利率, 召回投诉 | 对目标公司的成长叙事和资本市场预期影响最大 |",
        ]
    )
    micro_body = "\n\n".join(
        [
            "商业模式分析说明目标公司如何创造收入, 承担成本, 形成用户粘性和复购." * 25,
            "产品和服务分析说明核心产品线, 差异化卖点, 技术路线和用户价值." * 25,
            "客户和渠道分析说明目标客群, 渠道结构, 线上线下触点和获客效率." * 25,
            "财务和运营指标分析说明收入, 利润, 现金流, 交付, 库存和费用率变化." * 25,
            "护城河和竞争位置分析说明品牌, 供应链, 数据, 软件生态和替代风险." * 25,
        ]
    )
    pressure_test_body = "\n".join(
        [
            "| 视角 | 质疑 | 为什么重要 | 需要验证 |",
            "|---|---|---|---|",
            "| 行业专家 | 价值链和生命周期判断可能过于乐观, 行业利润池未必向目标环节转移 | 影响中观行业结论和七模块盈利性判断可靠性 | 验证行业规模, 竞争结构, 产能利用率和利润池分布数据 |",
            "| 投资研究员 | 估值修复可能依赖过高盈利假设, 市场可能把短期订单当成长期利润 | 影响资本市场预期差和估值锚判断 | 验证毛利率, 自由现金流, 分部利润和同业估值 |",
            "| 政策/监管研究者 | 监管约束可能改变业务增长节奏, 安全合规事件可能提高风险折现 | 影响风险折现, 外部因素和情景分析 | 查证监管文件, 处罚案例, 召回公告和政策口径 |",
            "| 经营者/创业者 | 执行难度可能高于战略叙事, 交付和售后能力可能成为瓶颈 | 影响交付节奏, 成本结构和组织能力判断 | 验证渠道质量, 供应链稳定性, 售后投入和用户投诉数据 |",
        ]
    )
    risk_body = "\n\n".join(
        [
            "风险需要拆成行业结构风险和目标公司自身风险. 行业结构风险来自竞争强度, 价格战, 监管变化, 技术路线切换和上游成本周期, 这些因素会压缩行业利润池并提高估值折现率." * 12,
            "目标公司或目标产品风险来自产品质量, 交付能力, 渠道效率, 现金流承压, 品牌舆情和管理执行, 这些变量会影响七模块里的盈利性, 防守性和景气度判断." * 12,
            "机会也需要拆成行业机会和目标自身机会. 行业机会来自渗透率提升, 政策支持, 供给出清和技术成本下降, 目标公司机会来自品牌, 渠道, 生态协同, 产品组合和运营效率改善." * 12,
        ]
    )
    verification_body = "\n".join(
        [
            "| 待验证问题 | 为什么重要 | 推荐来源 | 优先级 |",
            "|---|---|---|---|",
            "| 验证行业规模, 增速和渗透率是否仍支持增长假设 | 这些指标决定行业空间和生命周期判断是否成立 | 官方统计, 行业协会, 监管文件, 可信数据库 | 高 |",
            "| 验证目标公司收入, 利润, 现金流和运营指标是否支持估值逻辑 | 这些指标决定基本面变化和市场预期差是否真实 | 公司公告, 财报, 交易所文件, IR 材料 | 高 |",
            "| 验证目标产品质量, 交付, 投诉, 召回或合规风险 | 这些指标决定风险折现和品牌韧性 | 监管公告, 召回平台, 售后数据, 用户投诉数据库 | 高 |",
            "| 验证竞争对手价格, 产能, 渠道和新品节奏 | 这些信息决定行业结构风险和机会是否变化 | 同业公告, 行业数据库, 渠道调研, 媒体访谈 | 中 |",
        ]
    )
    retrieval_gap_body = "\n".join(
        [
            "| 缺口 | 三轮闭环已尝试 | 当前状态 | 为什么仍重要 | 未补齐原因 | 下一步来源 |",
            "|---|---|---|---|---|---|",
            "| 目标公司分业务线收入, 毛利率, 现金流, 订单交付, 股价区间和估值倍数的最新一手口径 | 第1轮: 公司公告, 财报和 IR 材料. 第2轮: 交易所文件, 交易所行情和可信市场数据库. 第3轮: 替代关键词, 本地语言和可信二手交叉验证 | 部分补齐/仍未补齐 | 这些缺口会影响基本面变化, 估值锚, 市场预期差和资本市场情景判断 | 部分行情和一致预期需要付费库或登录, 公开检索无可靠结果 | 公司公告, 财报, IR, 交易所, 监管公告, 官方行业数据和可信数据库 |",
            long_body,
        ]
    )
    parts: list[str] = [
        "# 示例公司基本面和资本市场研究报告",
        "## 0. 研报前置区",
        "### 0.1 报告摘要",
        long_body,
        "### 0.2 关键结论",
        long_body,
        "### 0.3 核心指标总览",
        core_metrics_body,
        "### 0.4 图表清单或图表占位",
        exhibit_list_body,
        "## 1. 直接结论",
        long_body,
        "## 2. 研究边界",
        long_body,
        "### 2.1 研究计划摘要",
        long_body,
        "### 2.2 来源矩阵和证据质量",
        source_matrix_body,
        "### 2.3 二次检索缺口",
        retrieval_gap_body,
        "## 3. 宏观环境分析",
        macro_body,
        "## 4. 中观行业分析",
        meso_body,
        "### 4.0 多业务线中观拆分",
        multibusiness_body,
        "### 4.3 行业地图和目标位置",
        mermaid_map_body,
        "### 4.4 生命周期判断",
        lifecycle_body,
        "## 5. 七个核心模块加权分析",
    ]
    for heading in [
        "### 5.1 可行性",
        "### 5.2 规模性",
        "### 5.3 防守性",
    ]:
        parts.extend([heading, base_module_body])
    for heading in [
        "### 5.4 盈利性",
        "### 5.5 估值",
        "### 5.6 外部因素",
            "### 5.7 景气度",
    ]:
        parts.extend([heading, priority_module_body])
    parts.extend(
        [
            "## 6. 微观公司/产品分析",
            micro_body,
            "## 10. 事实, 观点和推断分层",
            fact_inference_body,
            "## 11. 资本市场表现与估值预期变化",
            "### 11.1 股价表现拆解",
            section_11_1_body,
            "### 11.2 基本面变化",
            section_11_2_body,
            "### 11.3 估值逻辑和市场预期差",
            section_11_3_body,
            "### 11.4 上涨触发器, 下跌风险和情景分析",
            section_11_4_body,
            "| 情景 | 条件 | 需要跟踪的指标 |",
            "|---|---|---|",
            "| 乐观 | 条件 | 指标 |",
            "| 中性 | 条件 | 指标 |",
            "| 悲观 | 条件 | 指标 |",
            "## 12. 多视角压力测试",
            pressure_test_body,
            "## 13. 风险和机会",
            risk_body,
            "## 15. 方法论和数据来源说明",
            long_body,
            "## 16. 附录: 后续验证清单",
            verification_body,
            "## 17. 报告合规自检表",
            "\n".join(
                [
                    "| 检查项 | 是否通过 | 说明 |",
                    "|---|---|---|",
                    "| 模板骨架完整 | 通过 | 已保留 0-17 主骨架和公司/产品报告必需章节 |",
                    "| 研究简报转译已完成 | 通过 | 已按 research brief 锁定路由, 来源计划和深度契约 |",
                    "| Deep Research 可见痕迹完整 | 通过 | 已展示研究计划, 来源矩阵和二次检索缺口 |",
                    "| 分析层级选择正确 | 通过 | 宏观, 中观, 微观和资本市场层级齐全 |",
                    "| 七个核心模块全部出现 | 通过 | 七模块均独立展开且重点模块更厚 |",
                    "| 资本市场章节适用时已出现 | 通过 | 已包含 11.1-11.4 和情景分析 |",
                    "| 来源质量和证据等级清楚 | 通过 | 已区分来源质量, 证据等级和弱证据 |",
                    "| 一手来源检索状态和缺口清楚 | 通过 | 已说明一手来源状态和下一步验证缺口 |",
                    "| 事实/观点/推断已分层且证据层级清楚 | 通过 | 已区分事实/观点/推断和对应证据层级 |",
                    "| 后续验证清单具体 | 通过 | 已列出后续验证问题, 推荐来源和优先级 |",
                ]
            ),
            "本报告仅供研究和信息参考, 不构成投资建议, 也不构成任何收益承诺.",
        ]
    )
    return "\n\n".join(parts)


def sample_company_capital_thin_compliance_checklist() -> str:
    """
    构造合规自检表过薄的资本市场报告样例.

    :return: Markdown 样例文本.
    """
    text = sample_company_capital_pass()
    return re.sub(
        r"(?ms)(^## 17\. 报告合规自检表\s*\n\n).*",
        r"\1通过.",
        text,
    )


def sample_company_capital_thin_pressure_test() -> str:
    """
    构造压力测试章节过薄的资本市场报告样例.

    :return: Markdown 样例文本.
    """
    text = sample_company_capital_pass()
    return re.sub(
        r"(?ms)(^## 12\. 多视角压力测试\s*\n\n).*?(?=\n\n## 13\. 风险和机会)",
        r"\1太薄",
        text,
    )


def sample_company_capital_thin_report_front() -> str:
    """
    构造研报前置区过薄的资本市场报告样例.

    :return: Markdown 样例文本.
    """
    text = sample_company_capital_pass()
    return re.sub(
        r"(?ms)(^### 0\.2 关键结论\s*\n\n).*?(?=\n\n### 0\.3 核心指标总览)",
        r"\1太薄",
        text,
    )


def sample_company_capital_thin_macro() -> str:
    """
    构造宏观章节过薄的资本市场报告样例.

    :return: Markdown 样例文本.
    """
    text = sample_company_capital_pass()
    return re.sub(
        r"(?ms)(^## 3\. 宏观环境分析\s*\n\n).*?(?=\n\n## 4\. 中观行业分析)",
        r"\1太薄",
        text,
    )


def sample_company_capital_thin_micro() -> str:
    """
    构造微观章节过薄的资本市场报告样例.

    :return: Markdown 样例文本.
    """
    text = sample_company_capital_pass()
    return re.sub(
        r"(?ms)(^## 6\. 微观公司/产品分析\s*\n\n).*?(?=\n\n## 10\. 事实, 观点和推断分层)",
        r"\1太薄",
        text,
    )


def sample_company_capital_thin_risk_verification() -> str:
    """
    构造风险机会和后续验证章节过薄的资本市场报告样例.

    :return: Markdown 样例文本.
    """
    text = sample_company_capital_pass()
    text = re.sub(
        r"(?ms)(^## 13\. 风险和机会\s*\n\n).*?(?=\n\n## 15\. 方法论和数据来源说明)",
        r"\1太薄",
        text,
    )
    return re.sub(
        r"(?ms)(^## 16\. 附录: 后续验证清单\s*\n\n).*?(?=\n\n## 17\. 报告合规自检表)",
        r"\1太薄",
        text,
    )


def sample_company_capital_without_mermaid() -> str:
    """
    构造缺少 Mermaid 行业地图的资本市场报告样例.

    :return: Markdown 样例文本.
    """
    text = sample_company_capital_pass()
    return re.sub(
        r"(?ms)```mermaid.*?```",
        "行业地图文字描述.",
        text,
        count=1,
    )


def sample_company_capital_thin_exhibit_list() -> str:
    """
    构造图表清单过薄的资本市场报告样例.

    :return: Markdown 样例文本.
    """
    text = sample_company_capital_pass()
    return re.sub(
        r"(?ms)(^### 0\.4 图表清单或图表占位\s*\n\n).*?(?=\n\n## 1\. 直接结论)",
        r"\1| 图表 | 类型 | 用途 |\n|---|---|---|\n| 图表 1: 行业地图 | Mermaid | 展示产业链 |",
        text,
    )


def sample_overview_without_mermaid() -> str:
    """
    构造缺少 Mermaid 行业地图的行业全览报告样例.

    :return: Markdown 样例文本.
    """
    text = sample_overview_report(20)
    return re.sub(r"(?ms)```mermaid.*?```", "行业地图文字描述.", text, count=1)


def sample_specific_without_mermaid() -> str:
    """
    构造缺少 Mermaid 行业地图的行业具体问题报告样例.

    :return: Markdown 样例文本.
    """
    text = sample_specific_report(20)
    return re.sub(r"(?ms)```mermaid.*?```", "行业地图文字描述.", text, count=1)


def sample_company_capital_total_length_fail() -> str:
    """
    构造局部章节达标但整篇篇幅不足的资本市场报告样例.

    :return: Markdown 样例文本.
    """
    brief_body = "研究计划来源证据缺口事实观点推断方法论一手来源后续验证" * 7
    front_body = "报告摘要关键结论核心指标图表占位资本市场公司产品行业" * 5
    exhibit_list_body = "\n".join(
        [
            "| 图表 | 类型 | 用途 |",
            "|---|---|---|",
            "| 图表 1: 行业地图和目标位置 | Mermaid | 展示产业链和目标位置 |",
            "| 图表 2: 核心指标总览 | 表格 | 展示行业和目标关键读数 |",
            "| 图表 3: 七模块判断矩阵 | 表格 | 展示七模块结论 |",
            "| 图表 4: 竞争对手对比 | 表格 | 展示主要玩家差异 |",
        ]
    )
    macro_body = "政策监管经济消费利率汇率通胀风险偏好技术成本周期影响行业和目标公司" * 8
    meso_body = "行业定义关键指标市场规模增速渗透率行业地图产业链生命周期目标公司位置" * 8
    mermaid_map_body = "\n".join(
        [
            "```mermaid",
            "flowchart LR",
            "  A[上游] --> B[中游]",
            "  B --> C[渠道]",
            "  C --> D[目标公司/产品]",
            "```",
            "行业地图产业链目标公司位置竞争结构关键流向" * 5,
        ]
    )
    micro_body = "商业模式产品服务客户渠道财务运营收入利润现金流护城河竞争位置竞争优势" * 8
    module_body = "\n\n".join(
        [
            "**结论:** " + "结论内容" * 28,
            "**依据:** " + "依据内容" * 28,
            "**机制:** " + "机制内容" * 28,
            "**对目标公司/产品的影响:** " + "影响内容" * 28,
        ]
    )
    priority_module_body = "\n\n".join(
        [
            "**结论:** " + "结论内容" * 46,
            "**依据:** " + "依据内容" * 46,
            "**机制:** " + "机制内容" * 46,
            "**对目标公司/产品的影响:** " + "影响内容" * 46,
            "**关键指标和后续验证:** " + "指标验证" * 46,
        ]
    )
    capital_two_paragraphs = "\n\n".join(
        [
            "价格表现时间区间催化因素基本面变化市场预期估值锚" * 8,
            "事实推断证据缺口后续验证指数板块对比风险偏好" * 8,
        ]
    )
    capital_one_paragraph = "上涨触发器下跌风险情景分析跟踪指标不构成投资建议" * 16
    pressure_test_body = "\n".join(
        [
            "| 视角 | 质疑 | 为什么重要 | 需要验证 |",
            "|---|---|---|---|",
            "| 行业专家 | 行业结构和生命周期判断可能偏乐观 | 影响行业结论 | 验证市场规模和利润池 |",
            "| 投资研究员 | 估值和现金流假设可能偏乐观 | 影响估值判断 | 验证利润和现金流 |",
            "| 政策/监管研究者 | 政策监管约束可能遗漏 | 影响风险边界 | 查证监管文件 |",
            "| 经营者/创业者 | 执行路径可能不现实 | 影响落地判断 | 验证渠道和供应链 |",
            "| 反方审稿人 | 核心结论可能被薄弱证据支撑 | 重要因为会影响报告结论可靠性 | 验证事实观点推断和证据等级 |",
            "| 方法论审稿人 | 样本和口径可能不一致 | 重要因为会影响可比性 | 验证统计口径和样本范围 |",
        ]
    )
    risk_body = "风险机会行业结构目标公司目标产品竞争监管成本品牌渠道现金流质量交付机会验证" * 8
    verification_body = "\n".join(
        [
            "| 待验证问题 | 为什么重要 | 推荐来源 | 优先级 |",
            "|---|---|---|---|",
            "| 验证收入利润现金流 | 为什么重要是影响基本面 | 推荐来源公司公告财报IR交易所文件 | 高 |",
            "| 验证行业规模增速渗透率 | 为什么重要是影响行业空间 | 推荐来源官方统计行业协会监管公告 | 高 |",
            "| 验证质量投诉召回 | 为什么重要是影响风险折现 | 推荐来源监管公告召回平台投诉数据 | 中 |",
            "| 验证竞争对手价格产能渠道 | 为什么重要是影响行业结构和机会 | 推荐来源同业公告行业数据库渠道调研 | 中 |",
            "| 验证估值和交易数据 | 为什么重要是影响资本市场判断 | 推荐来源交易所行情和数据库 | 中 |",
        ]
    )
    compliance_body = "\n".join(
        [
            "| 检查项 | 是否通过 | 说明 |",
            "|---|---|---|",
            "| 模板骨架完整 | 通过 | 模板骨架完整 |",
            "| 研究简报转译已完成 | 通过 | 研究简报已转译 |",
            "| Deep Research 可见痕迹完整 | 通过 | Deep Research 计划和来源矩阵已呈现 |",
            "| 分析层级选择正确 | 通过 | 分析层级包含宏观中观微观资本市场 |",
            "| 七模块完整 | 通过 | 七模块独立展开 |",
            "| 资本市场章节适用时已出现 | 通过 | 资本市场 11.1-11.4 已出现 |",
            "| 来源质量和证据等级清楚 | 通过 | 来源质量证据等级和一手来源状态已说明 |",
            "| 事实/观点/推断已分层 | 通过 | 事实观点推断已分层 |",
            "| 后续验证清单具体 | 通过 | 后续验证清单含推荐来源和优先级 |",
            "| Markdown 标题格式正确 | 通过 | 标题格式正确且报告深度 rubric 已检查 |",
            "| 总篇幅门槛已检查 | 通过 | 总篇幅门槛已作为维护检查项 |",
        ]
    )
    parts: list[str] = [
        "## 0. 研报前置区",
        "### 0.1 报告摘要",
        front_body,
        "### 0.2 关键结论",
        front_body,
        "### 0.3 核心指标总览",
        front_body,
        "### 0.4 图表清单或图表占位",
        exhibit_list_body,
        "## 1. 直接结论",
        brief_body,
        "## 2. 研究边界",
        brief_body,
        "### 2.1 研究计划摘要",
        brief_body,
        "### 2.2 来源矩阵和证据质量",
        brief_body,
        "### 2.3 二次检索缺口",
        brief_body,
        "## 3. 宏观环境分析",
        macro_body,
        "## 4. 中观行业分析",
        meso_body,
        "### 4.0 多业务线中观拆分",
        brief_body,
        "### 4.3 行业地图和目标位置",
        mermaid_map_body,
        "### 4.4 生命周期判断",
        brief_body,
        "## 5. 七个核心模块加权分析",
    ]
    for heading in ["### 5.1 可行性", "### 5.2 规模性", "### 5.3 防守性"]:
        parts.extend([heading, module_body])
    for heading in ["### 5.4 盈利性", "### 5.5 估值", "### 5.6 外部因素", "### 5.7 景气度"]:
        parts.extend([heading, priority_module_body])
    parts.extend(
        [
            "## 6. 微观公司/产品分析",
            micro_body,
            "## 10. 事实, 观点和推断分层",
            brief_body,
            "## 11. 资本市场表现与估值预期变化",
            "### 11.1 股价表现拆解",
            capital_two_paragraphs,
            "### 11.2 基本面变化",
            capital_two_paragraphs,
            "### 11.3 估值逻辑和市场预期差",
            capital_two_paragraphs,
            "### 11.4 上涨触发器, 下跌风险和情景分析",
            capital_one_paragraph,
            "## 12. 多视角压力测试",
            pressure_test_body,
            "## 13. 风险和机会",
            risk_body,
            "## 15. 方法论和数据来源说明",
            brief_body,
            "## 16. 附录: 后续验证清单",
            verification_body,
            "## 17. 报告合规自检表",
            compliance_body,
        ]
    )
    return "\n\n".join(parts)


def sample_company_capital_thin_source_matrix() -> str:
    """
    构造来源矩阵过薄的资本市场报告样例.

    :return: Markdown 样例文本.
    """
    text = sample_company_capital_pass()
    return re.sub(
        r"(?ms)(^### 2\.2 来源矩阵和证据质量\s*\n\n).*?(?=\n\n### 2\.3 二次检索缺口)",
        r"\1太薄",
        text,
    )


def sample_company_capital_weak_source_columns() -> str:
    """
    构造来源矩阵列缺失的资本市场报告样例.

    :return: Markdown 样例文本.
    """
    text = sample_company_capital_pass()
    weak_body = "\n".join(
        [
            "| 来源 | 内容 |",
            "|---|---|",
            "| 媒体和公告 | 来源说明 |",
            "来源矩阵证据质量说明" * 40,
        ]
    )
    return re.sub(
        r"(?ms)(^### 2\.2 来源矩阵和证据质量\s*\n\n).*?(?=\n\n### 2\.3 二次检索缺口)",
        r"\1" + weak_body,
        text,
    )


def sample_company_capital_weak_fact_columns() -> str:
    """
    构造事实观点推断分层列缺失的资本市场报告样例.

    :return: Markdown 样例文本.
    """
    text = sample_company_capital_pass()
    weak_body = "\n".join(
        [
            "| 类型 | 内容 |",
            "|---|---|",
            "| 事实 | 内容 |",
            "| 观点 | 内容 |",
            "| 推断 | 内容 |",
            "事实观点推断分层证据说明" * 40,
        ]
    )
    return re.sub(
        r"(?ms)(^## 10\. 事实, 观点和推断分层\s*\n\n).*?(?=\n\n## 11\. 资本市场表现与估值预期变化)",
        r"\1" + weak_body,
        text,
    )


def sample_overview_weak_evidence_columns() -> str:
    """
    构造行业全览证据分层列缺失样例.

    :return: Markdown 样例文本.
    """
    text = sample_overview_report(20)
    return re.sub(
        r"(?ms)(^## 8\. 事实, 观点和推断分层\s*\n\n).*?(?=\n\n## 9\. 多视角压力测试)",
        r"\1| 类型 | 内容 |\n|---|---|\n| 事实 | 内容 |\n| 观点 | 内容 |\n| 推断 | 内容 |",
        text,
    )


def sample_specific_weak_evidence_chain_columns() -> str:
    """
    构造行业具体问题证据链列缺失样例.

    :return: Markdown 样例文本.
    """
    text = sample_specific_report(20)
    return re.sub(
        r"(?ms)(^## 6\. 证据链分析\s*\n\n).*?(?=\n\n## 7\. 生命周期判断)",
        r"\1| 子问题 | 结论 |\n|---|---|\n| 子问题 | 结论 |",
        text,
    )


def sample_company_capital_thin_lifecycle() -> str:
    """
    构造生命周期判断过薄的资本市场报告样例.

    :return: Markdown 样例文本.
    """
    text = sample_company_capital_pass()
    return re.sub(
        r"(?ms)(^### 4\.4 生命周期判断\s*\n\n).*?(?=\n\n## 5\. 七个核心模块加权分析)",
        r"\1成长期.",
        text,
    )


def sample_company_capital_weak_capital_concepts() -> str:
    """
    构造资本市场第 11 章概念缺失的报告样例.

    :return: Markdown 样例文本.
    """
    text = sample_company_capital_pass()
    generic_two_paragraphs = "\n\n".join(
        [
            "资本市场分析内容围绕外部环境和市场变化展开, 需要结合多种信息综合判断." * 45,
            "资本市场分析内容还需要考虑风险因素和未来变化, 但这里故意不写具体概念." * 45,
        ]
    )
    replacements = [
        ("### 11.1 股价表现拆解", "### 11.2 基本面变化"),
        ("### 11.2 基本面变化", "### 11.3 估值逻辑和市场预期差"),
        ("### 11.3 估值逻辑和市场预期差", "### 11.4 上涨触发器, 下跌风险和情景分析"),
        ("### 11.4 上涨触发器, 下跌风险和情景分析", "## 12. 多视角压力测试"),
    ]
    for start, end in replacements:
        text = re.sub(
            rf"(?ms)(^{re.escape(start)}\s*\n\n).*?(?=\n\n{re.escape(end)})",
            r"\1" + generic_two_paragraphs,
            text,
        )
    return text


def sample_company_capital_weak_multibusiness_split() -> str:
    """
    构造多业务线中观拆分列缺失的资本市场报告样例.

    :return: Markdown 样例文本.
    """
    text = sample_company_capital_pass()
    weak_body = "\n".join(
        [
            "| 业务 | 内容 |",
            "|---|---|",
            "| 多业务 | 泛泛说明公司有多个业务 |",
            "多业务线中观拆分需要展开但这里故意缺少行业阶段, 竞争格局, 关键指标和对目标公司的含义." * 20,
        ]
    )
    return re.sub(
        r"(?ms)(^### 4\.0 多业务线中观拆分\s*\n\n).*?(?=\n\n### 4\.3 行业地图和目标位置)",
        r"\1" + weak_body,
        text,
    )


def sample_company_capital_weak_retrieval_gap() -> str:
    """
    构造二次检索缺口缺少可执行验证信息的资本市场报告样例.

    :return: Markdown 样例文本.
    """
    text = sample_company_capital_pass()
    return re.sub(
        r"(?ms)(^### 2\.3 二次检索缺口\s*\n\n).*?(?=\n\n## 3\. 宏观环境分析)",
        r"\1后续继续关注相关信息." + "说明内容" * 80,
        text,
    )


def sample_company_capital_weak_core_metrics() -> str:
    """
    构造核心指标总览缺少指标表契约的资本市场报告样例.

    :return: Markdown 样例文本.
    """
    text = sample_company_capital_pass()
    weak_body = "\n".join(
        [
            "| 项目 | 内容 |",
            "|---|---|",
            "| 指标 | 这里用泛泛摘要代替核心指标表 |",
            "本节虽然写了较长内容, 但故意缺少行业读数, 目标公司/产品读数, 判断, 证据/来源, 也没有覆盖市场规模, 增速/渗透率, 竞争强度, 盈利水平, 景气度和关键风险." * 12,
        ]
    )
    return re.sub(
        r"(?ms)(^### 0\.3 核心指标总览\s*\n\n).*?(?=\n\n### 0\.4 图表清单或图表占位)",
        r"\1" + weak_body,
        text,
    )


def sample_company_capital_missing_module_verification() -> str:
    """
    构造七模块缺少关键指标和后续验证块的资本市场报告样例.

    :return: Markdown 样例文本.
    """
    text = sample_company_capital_pass()
    weak_body = "\n\n".join(
        [
            "**结论:** " + "结论内容" * 70,
            "**依据:** " + "依据内容" * 70,
            "**机制:** " + "机制内容" * 70,
            "**对目标公司/产品的影响:** " + "影响内容" * 70,
        ]
    )
    return re.sub(
        r"(?ms)(^### 5\.1 可行性\s*\n\n).*?(?=\n\n### 5\.2 规模性)",
        r"\1" + weak_body,
        text,
    )


def sample_overview_weak_retrieval_gap() -> str:
    """
    构造二次检索缺口缺少可执行验证信息的行业全览报告样例.

    :return: Markdown 样例文本.
    """
    text = sample_overview_report(20)
    return re.sub(
        r"(?ms)(^### 2\.3 二次检索缺口\s*\n\n).*?(?=\n\n## 3\. 行业地图)",
        r"\1后续继续关注相关信息." + "说明内容" * 80,
        text,
    )


def sample_specific_weak_retrieval_gap() -> str:
    """
    构造二次检索缺口缺少可执行验证信息的行业具体问题报告样例.

    :return: Markdown 样例文本.
    """
    text = sample_specific_report(20)
    return re.sub(
        r"(?ms)(^### 3\.3 二次检索缺口\s*\n\n).*?(?=\n\n## 4\. 行业地图)",
        r"\1后续继续关注相关信息." + "说明内容" * 80,
        text,
    )


def sample_overview_thin_lifecycle() -> str:
    """
    构造生命周期判断过薄的行业全览报告样例.

    :return: Markdown 样例文本.
    """
    text = sample_overview_report(20)
    return re.sub(
        r"(?ms)(^## 4\. 生命周期判断\s*\n\n).*?(?=\n\n## 5\. 七个核心模块)",
        r"\1成长期.",
        text,
    )


def sample_specific_thin_lifecycle() -> str:
    """
    构造生命周期判断过薄的行业具体问题报告样例.

    :return: Markdown 样例文本.
    """
    text = sample_specific_report(20)
    return re.sub(
        r"(?ms)(^## 7\. 生命周期判断\s*\n\n).*?(?=\n\n## 8\. 七个核心模块分析)",
        r"\1成长期.",
        text,
    )


def sample_english_specific_report() -> str:
    """
    构造完整英文行业具体问题报告样例.

    :return: 英文 Markdown 样例文本.
    """
    analysis = (
        "Conclusion: the available Evidence supports a conditional industry judgment. "
        "The Mechanism connects demand, supply, competition, cost, and policy to measurable outcomes. "
        "Implication for the Question: decision makers should track the stated indicators and verify gaps "
        "against a Primary Source before changing the conclusion."
    )
    module_body = "\n\n".join(
        [
            "**Conclusion:** " + analysis,
            "**Evidence:** " + analysis,
            "**Mechanism:** " + analysis,
            "**Implication for the Question:** " + " ".join([analysis] * 13),
        ]
    )
    direct_answer = "\n\n".join([analysis] * 4)
    return "\n\n".join(
        [
            "# Example Industry Question Research Report",
            "## 1. Direct Answer\n\n" + direct_answer,
            "## 2. Conclusion Summary\n\n" + analysis,
            "## 3. Research Scope\n\nGlobal market, 2024-2026, with explicit inclusions, exclusions, and assumptions.",
            "### 3.1 Research Plan Summary\n\n" + analysis,
            "### 3.2 Source Matrix and Evidence Quality\n\n"
            "| Source Type | Use in This Report | Evidence Tier | Retrieval Status | Limitations |\n"
            "|---|---|---|---|---|\n"
            "| Official Source | Market Size and Policy | primary | obtained | Verification |",
            "### 3.3 Follow-up Retrieval Gaps\n\n"
            "Missing Evidence remains important because it may change the conclusion. Three-Round Closure Attempts "
            "included Round 1 with a Primary Source, Round 2 with a Near-Primary Source, and Round 3 with an "
            "Industry Association and Credible Database. Attempted Sources are recorded. Current Status is "
            "Partially Closed. Unresolved Reason is Paid Database and Definition Mismatch. Next Source is an "
            "Official Source for Verification.\n\n"
            "| Gap | Three-Round Closure Attempts | Current Status | Why It Still Matters | Unresolved Reason | Next Source |\n"
            "|---|---|---|---|---|---|\n"
            "| Missing Evidence | Round 1, Round 2, Round 3 | Partially Closed | Evidence may change the result | Paid Database | Primary Source |",
            "## 4. Industry Map\n\n```mermaid\nflowchart LR\nA[Supply] --> B[Market]\nB --> C[Demand]\n```",
            "## 5. Problem Decomposition and Issue Tree\n\n" + analysis,
            "## 6. Evidence Chain Analysis\n\n"
            "| Sub-question | Conclusion | Fact | Opinion | Inference | Evidence Tier | Source Status | Confidence |\n"
            "|---|---|---|---|---|---|---|---|\n"
            "| Demand | Conditional growth | Fact | Opinion | Inference | primary | obtained | high |",
            "## 7. Lifecycle Assessment\n\n"
            "**Lifecycle Phase:** Growth Phase. " + analysis + "\n\n"
            "**Evidence:** Evidence supports expansion. " + analysis + "\n\n"
            "**Counterevidence:** Uneven adoption challenges the base case. " + analysis + "\n\n"
            "**Confidence:** Medium. " + analysis + "\n\n"
            "**Implication for the Question:** Timing, segment selection, and verification matter. " + analysis,
            "## 8. Seven Core Modules Analysis",
            "### 8.1 Feasibility\n\n" + module_body,
            "### 8.2 Scalability\n\n" + module_body,
            "### 8.3 Defensibility\n\n" + module_body,
            "### 8.4 Profitability\n\n" + module_body,
            "### 8.5 Valuation\n\n" + module_body,
            "### 8.6 External Factors\n\n" + module_body,
            "### 8.7 Prosperity\n\n" + module_body,
            "## 9. Multi-Perspective Pressure Test\n\n"
            "| Perspective | Challenge | Impact | Verification Needed |\n"
            "|---|---|---|---|\n"
            "| Industry Expert | Industry structure may differ | Changes the conclusion | Verify industry data |\n"
            "| Investment Researcher | Profitability may be weaker | Changes valuation logic | Verify financial data |\n"
            "| Policy/Regulatory | Policy may tighten | Changes the risk boundary | Verify official policy |\n"
            "| Operator/Entrepreneur | Execution may be harder | Changes feasibility | Verify operating data |",
            "## 12. Report Compliance Checklist\n\n"
            "| Check | Passed | Explanation |\n"
            "|---|---|---|\n"
            "| Report structure | Yes | The report preserves the required structure, Evidence rules, and Verification gaps. |",
            "This report is for research and informational purposes only. It does not constitute investment advice or any guarantee of returns.",
        ]
    )


def englishize_contract_fixture(text: str) -> str:
    """
    将中文自测样例的契约标题和关键词转换为英文.

    本函数只用于复用既有深度样例验证英文适配层.

    :param text: 中文 Markdown 自测样例.
    :return: 使用英文契约标题和关键词的样例.
    """
    reverse_headings = {target: source for source, target in ENGLISH_HEADING_ALIASES.items()}
    translated_lines = [reverse_headings.get(line.strip(), line) for line in text.splitlines()]
    translated = "\n".join(translated_lines)
    reverse_terms: dict[str, str] = {}
    for source, target in ENGLISH_TERM_ALIASES.items():
        reverse_terms.setdefault(target, source)
    reverse_terms.update(
        {
            "证据层级": "Evidence Tier",
            "为什么重要": "Why It Matters",
            "阶段结论": "Lifecycle Phase",
            "依据": "Basis",
            "检索状态": "Retrieval Status",
            "限制": "Limitations",
            "一手来源检索状态": "Primary-Source Status",
        }
    )
    for source, target in sorted(reverse_terms.items(), key=lambda item: len(item[0]), reverse=True):
        translated = translated.replace(source, target)
    translated = translated.replace(
        "# 示例行业研究报告",
        "# Example Industry Research Report",
    )
    translated = translated.replace(
        "# 示例公司基本面和资本市场研究报告",
        "# Example Company Fundamentals and Capital-Market Research Report",
    )
    translated = translated.replace(
        "本报告仅供研究和信息参考, 不构成投资建议, 也不构成任何收益承诺.",
        "This report is for research and informational purposes only. It does not constitute investment advice or any guarantee of returns.",
    )
    return translated


def run_self_test(json_output: bool = False) -> int:
    """
    运行脚本内置自检.

    :param json_output: 是否输出 JSON.
    :return: 退出码, 0 表示通过, 1 表示失败.
    """
    cases = [
        (
            "short_pass",
            "short",
            "价格战通常来自供给扩张快于需求, 龙头希望用价格换份额, 中小玩家被迫跟进. 具体强度还需要结合销量, 库存和盈利数据验证.",
            False,
        ),
        (
            "prompt_builder_pass",
            "prompt-builder",
            "\n".join(
                [
                    "请使用 industry-research skill 生成一份标准报告.",
                    "报告路由: 公司/产品加资本市场模块.",
                    "必须使用: assets/company-product-template.md.",
                    "结构要求: 包含 0. 研报前置区, 2.1 研究计划摘要, 2.2 来源矩阵和证据质量, 2.3 二次检索缺口, 5.1-5.7, 6. 微观公司/产品分析, 11.1, 11.2, 11.3, 11.4, 12. 多视角压力测试, 17. 报告合规自检表.",
                    "必需章节: 0. 研报前置区, 研究计划摘要, 来源矩阵, 二次检索缺口, 事实/观点/推断, 压力测试, 报告合规自检表.",
                    "深度要求: 目标字数 12000-18000 中文字符, 七模块 5.1 到 5.7 独立展开, 不压缩成表格.",
                    "证据要求: 一手来源优先, 重要数字标注来源或进入二次检索缺口.",
                    "合规要求: 不构成投资建议.",
                    "输出前重写触发器: 缺少模板, 11.1-11.4, 来源矩阵, 二次检索缺口或报告合规自检表时必须重写.",
                ]
            ),
            False,
        ),
        (
            "auto_prompt_builder_pass",
            "auto",
            "\n".join(
                [
                    "请使用 industry-research skill 生成一份标准报告.",
                    "报告路由: 公司/产品加资本市场模块.",
                    "必须使用: assets/company-product-template.md.",
                    "结构要求: 包含 0. 研报前置区, 2.1 研究计划摘要, 2.2 来源矩阵和证据质量, 2.3 二次检索缺口, 5.1-5.7, 6. 微观公司/产品分析, 11.1, 11.2, 11.3, 11.4, 12. 多视角压力测试, 17. 报告合规自检表.",
                    "必需章节: 0. 研报前置区, 研究计划摘要, 来源矩阵, 二次检索缺口, 事实/观点/推断, 压力测试, 报告合规自检表.",
                    "深度要求: 目标字数 12000-18000 中文字符, 七模块 5.1 到 5.7 独立展开, 不压缩成表格.",
                    "证据要求: 一手来源优先, 重要数字标注来源或进入二次检索缺口.",
                    "合规要求: 不构成投资建议.",
                    "输出前重写触发器: 缺少模板, 11.1-11.4, 来源矩阵, 二次检索缺口或报告合规自检表时必须重写.",
                ]
            ),
            False,
        ),
        (
            "english_prompt_builder_pass",
            "prompt-builder",
            "\n".join(
                [
                    "Please use the industry-research skill to generate a standard report.",
                    "Report Route: Company/Product plus Capital Market module.",
                    "Must Use: assets/company-product-template.md.",
                    "Structure Requirements: include 0. Research Front Matter, 2.1 Research Plan Summary, 2.2 Source Matrix, 2.3 Follow-up Retrieval Gaps, 5.1-5.7, 6. Micro Company/Product Analysis, 11.1, 11.2, 11.3, 11.4, 12. Multi-Perspective Pressure Test, and 17. Report Compliance Checklist.",
                    "Required Sections: Research Plan Summary, Source Matrix, Follow-up Retrieval Gaps, Fact/Opinion/Inference, Pressure Test, and Report Compliance Checklist.",
                    "Depth Requirements: Target Length is the standard range and seven modules remain independent.",
                    "Evidence Requirements: Primary-Source-First and place unsupported figures in Follow-up Retrieval Gaps.",
                    "Compliance Requirements: Not Investment Advice.",
                    "Rewrite before output when the template, 11.1-11.4, Source Matrix, Follow-up Retrieval Gaps, or Report Compliance Checklist is missing.",
                ]
            ),
            False,
        ),
        (
            "prompt_builder_weak_contract_fail",
            "prompt-builder",
            sample_prompt_builder_weak_contract(),
            True,
        ),
        (
            "company_capital_pass",
            "company-capital",
            sample_company_capital_pass(),
            False,
        ),
        (
            "overview_pass",
            "overview",
            sample_overview_report(20),
            False,
        ),
        (
            "specific_pass",
            "specific",
            sample_specific_report(20),
            False,
        ),
        (
            "english_specific_pass",
            "specific",
            sample_english_specific_report(),
            False,
        ),
        (
            "english_overview_contract_pass",
            "overview",
            englishize_contract_fixture(sample_overview_report(20)),
            False,
        ),
        (
            "english_company_capital_contract_pass",
            "company-capital",
            englishize_contract_fixture(sample_company_capital_pass()),
            False,
        ),
        (
            "overview_missing_h1_fail",
            "overview",
            sample_overview_report(20).replace("# 示例行业研究报告\n\n", "", 1),
            True,
        ),
        (
            "specific_duplicate_h1_fail",
            "specific",
            sample_specific_report(20).replace(
                "# 示例行业问题研究报告",
                "# 示例行业问题研究报告\n\n# 重复标题",
                1,
            ),
            True,
        ),
        (
            "overview_noncanonical_disclaimer_fail",
            "overview",
            sample_overview_report(20).replace(
                "本报告仅供研究和信息参考, 不构成投资建议, 也不构成任何收益承诺.",
                "本报告不构成投资建议.",
                1,
            ),
            True,
        ),
        (
            "auto_english_specific_pass",
            "auto",
            sample_english_specific_report(),
            False,
        ),
        (
            "english_mixed_heading_fail",
            "specific",
            sample_english_specific_report().replace(
                "### 8.7 Prosperity",
                "### 8.7 景气度",
            ),
            True,
        ),
        (
            "english_lowercase_contract_field_fail",
            "specific",
            sample_english_specific_report().replace(
                "| Source Type |",
                "| source type |",
            ),
            True,
        ),
        (
            "english_mixed_contract_field_fail",
            "specific",
            sample_english_specific_report().replace(
                "| Source Type |",
                "| 来源类型 |",
            ),
            True,
        ),
        (
            "chinese_legacy_contract_field_fail",
            "company-capital",
            sample_company_capital_pass().replace(
                "| 指标 | 行业读数 | 目标公司/产品读数 | 判断 | 证据/来源 |",
                "| 指标 | 行业读数 | 目标公司读数 | 判断 | 证据/来源 |",
            ),
            True,
        ),
        (
            "english_dynamic_target_field_fail",
            "company-capital",
            englishize_contract_fixture(sample_company_capital_pass()).replace(
                "Target Company/Product Reading",
                "BYD Reading",
            ),
            True,
        ),
        (
            "english_assessment_field_fail",
            "company-capital",
            englishize_contract_fixture(sample_company_capital_pass()).replace(
                "Judgment",
                "Assessment",
            ),
            True,
        ),
        (
            "english_subquestion_field_fail",
            "specific",
            sample_english_specific_report().replace(
                "Sub-question",
                "Subquestion",
            ),
            True,
        ),
        (
            "english_counterevidence_label_fail",
            "specific",
            sample_english_specific_report().replace(
                "**Counterevidence:**",
                "**Counter-evidence:**",
            ),
            True,
        ),
        (
            "english_round_abbreviation_fail",
            "specific",
            sample_english_specific_report().replace("Round 1", "R1"),
            True,
        ),
        (
            "company_capital_fail",
            "company-capital",
            "## 1. 直接结论\n\n这是一个不完整报告.",
            True,
        ),
        (
            "capital_priority_depth_block_fail",
            "company-capital",
            sample_company_capital_without_priority_block(),
            True,
        ),
        (
            "capital_section_11_paragraph_density_fail",
            "company-capital",
            sample_company_capital_single_paragraph_section_11(),
            True,
        ),
        (
            "capital_weak_core_metrics_fail",
            "company-capital",
            sample_company_capital_weak_core_metrics(),
            True,
        ),
        (
            "capital_missing_module_verification_fail",
            "company-capital",
            sample_company_capital_missing_module_verification(),
            True,
        ),
        (
            "capital_thin_source_matrix_fail",
            "company-capital",
            sample_company_capital_thin_source_matrix(),
            True,
        ),
        (
            "capital_weak_source_columns_fail",
            "company-capital",
            sample_company_capital_weak_source_columns(),
            True,
        ),
        (
            "capital_weak_fact_columns_fail",
            "company-capital",
            sample_company_capital_weak_fact_columns(),
            True,
        ),
        (
            "capital_thin_lifecycle_fail",
            "company-capital",
            sample_company_capital_thin_lifecycle(),
            True,
        ),
        (
            "capital_weak_capital_concepts_fail",
            "company-capital",
            sample_company_capital_weak_capital_concepts(),
            True,
        ),
        (
            "capital_weak_multibusiness_split_fail",
            "company-capital",
            sample_company_capital_weak_multibusiness_split(),
            True,
        ),
        (
            "capital_weak_retrieval_gap_fail",
            "company-capital",
            sample_company_capital_weak_retrieval_gap(),
            True,
        ),
        (
            "capital_thin_compliance_checklist_fail",
            "company-capital",
            sample_company_capital_thin_compliance_checklist(),
            True,
        ),
        (
            "capital_thin_pressure_test_fail",
            "company-capital",
            sample_company_capital_thin_pressure_test(),
            True,
        ),
        (
            "capital_thin_report_front_fail",
            "company-capital",
            sample_company_capital_thin_report_front(),
            True,
        ),
        (
            "capital_thin_macro_fail",
            "company-capital",
            sample_company_capital_thin_macro(),
            True,
        ),
        (
            "capital_thin_micro_fail",
            "company-capital",
            sample_company_capital_thin_micro(),
            True,
        ),
        (
            "capital_thin_risk_verification_fail",
            "company-capital",
            sample_company_capital_thin_risk_verification(),
            True,
        ),
        (
            "capital_missing_mermaid_fail",
            "company-capital",
            sample_company_capital_without_mermaid(),
            True,
        ),
        (
            "capital_thin_exhibit_list_fail",
            "company-capital",
            sample_company_capital_thin_exhibit_list(),
            True,
        ),
        (
            "capital_total_length_fail",
            "company-capital",
            sample_company_capital_total_length_fail(),
            True,
        ),
        (
            "overview_total_length_fail",
            "overview",
            sample_overview_report(10),
            True,
        ),
        (
            "specific_total_length_fail",
            "specific",
            sample_specific_report(9),
            True,
        ),
        (
            "overview_missing_mermaid_fail",
            "overview",
            sample_overview_without_mermaid(),
            True,
        ),
        (
            "specific_missing_mermaid_fail",
            "specific",
            sample_specific_without_mermaid(),
            True,
        ),
        (
            "overview_weak_evidence_columns_fail",
            "overview",
            sample_overview_weak_evidence_columns(),
            True,
        ),
        (
            "overview_thin_lifecycle_fail",
            "overview",
            sample_overview_thin_lifecycle(),
            True,
        ),
        (
            "overview_weak_retrieval_gap_fail",
            "overview",
            sample_overview_weak_retrieval_gap(),
            True,
        ),
        (
            "specific_weak_evidence_chain_columns_fail",
            "specific",
            sample_specific_weak_evidence_chain_columns(),
            True,
        ),
        (
            "specific_thin_lifecycle_fail",
            "specific",
            sample_specific_thin_lifecycle(),
            True,
        ),
        (
            "specific_weak_retrieval_gap_fail",
            "specific",
            sample_specific_weak_retrieval_gap(),
            True,
        ),
        (
            "short_fail",
            "short",
            "长内容" * 1000,
            True,
        ),
    ]

    failures: list[str] = []
    for name, profile, text, should_fail in cases:
        errors = run_profile(text, profile)
        failed = bool(errors)
        if failed != should_fail:
            state = "failed" if failed else "passed"
            expected = "fail" if should_fail else "pass"
            failures.append(f"{name}: expected {expected}, got {state}")

    english_report = sample_english_specific_report()
    if detect_report_language(english_report) != "en":
        failures.append("english_language_detection: expected en")
    if run_profile(english_report, "specific", language="en"):
        failures.append("explicit_english_language: expected pass")
    if not run_profile(english_report, "specific", language="zh"):
        failures.append("explicit_chinese_language_mismatch: expected fail")

    semantic_alias_cases = {
        "Research brief": "研究简报",
        "Seven core modules": "七个核心模块",
        "market expectations": "市场预期",
        "moat": "护城河",
        "share-price performance": "股价",
        "time period": "时间区间",
        "two-year": "时间区间",
        "fundamental catalysts": "催化",
        "catalysts": "催化",
        "data gap": "证据缺口",
        "verification gap": "待核验",
        "deliveries and orders": "交付和订单",
        "business mix": "业务组合",
        "mix": "业务组合",
        "fundamentals": "基本面",
        "re-rating": "重估",
        "proof required": "需要证明",
        "proof": "需要证明",
        "upside catalyst": "上涨触发器",
        "downside risks": "下跌风险",
        "scenario": "情景",
        "metrics to track": "跟踪指标",
        "follow-up verification checklist": "后续验证清单",
        "consumption": "消费",
        "volume": "运营指标",
        "industry-structure": "行业结构",
        "company filings": "公司公告",
        "peer-reviewed research": "近一手来源",
        "Capital-Market": "资本市场",
        "Industry Risk and Company Opportunity": "行业风险 and 目标公司机会",
        "price pattern over one-year": "价格表现 over 时间区间",
        "shipments show a fundamental change": "交付 show a 基本面变化",
        "expectation gap": "预期差",
        "Primary company disclosure and near-primary evidence": "一手来源 and 近一手 证据",
        "Primary-source retrieval status": "一手来源检索状态",
        "peer-reviewed evidence": "近一手 证据",
    }
    for source, expected in semantic_alias_cases.items():
        normalized = normalize_report_contract(source, "en")
        if expected not in normalized:
            failures.append(f"english_semantic_alias: {source!r} did not normalize to {expected!r}")

    if failures:
        if json_output:
            print(json.dumps({"status": "fail", "failures": failures}, ensure_ascii=False, indent=2))
            return 1
        print("SELF TEST FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    if json_output:
        print(json.dumps({"status": "pass", "failures": []}, ensure_ascii=False, indent=2))
        return 0
    print("SELF TEST PASS")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """
    构建命令行解析器.

    :return: argparse 解析器.
    """
    parser = argparse.ArgumentParser(description="Check industry research report contract.")
    parser.add_argument("report", type=Path, nargs="?", help="Markdown report path.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-test.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument(
        "--profile",
        choices=["company-capital", "company", "overview", "specific", "prompt-builder", "short", "auto"],
        help="Expected report profile.",
    )
    parser.add_argument(
        "--language",
        choices=["auto", "zh", "en"],
        default="auto",
        help="Expected report language. Default: auto.",
    )
    return parser


def main() -> int:
    """
    执行命令行入口.

    :return: 退出码, 0 表示通过, 1 表示失败.
    """
    parser = build_parser()
    args = parser.parse_args()
    if args.self_test:
        return run_self_test(json_output=args.json)
    if not args.report or not args.profile:
        parser.error("report and --profile are required unless --self-test is used")
    text = read_text(args.report)
    errors = run_profile(text, args.profile, language=args.language)
    if args.json:
        status = "fail" if errors else "pass"
        print(
            json.dumps(
                {
                    "status": status,
                    "profile": args.profile,
                    "language": args.language,
                    "report": str(args.report),
                    "errors": errors,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1 if errors else 0
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
