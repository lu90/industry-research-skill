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
import tempfile
from pathlib import Path


COMMON_SECTION_TITLES = {
    "research_scope": ("研究边界", "Research Scope"),
    "research_plan": ("研究计划摘要", "Research Plan Summary"),
    "source_matrix": ("来源矩阵和证据质量", "Source Matrix and Evidence Quality"),
    "retrieval_gap_closure": ("检索缺口闭环结果", "Retrieval Gap Closure Results"),
    "industry_definition": ("行业一句话定义", "One-Sentence Industry Definition"),
    "industry_map": ("行业地图", "Industry Map"),
    "lifecycle": ("生命周期判断", "Lifecycle Assessment"),
    "seven_modules": ("七个核心模块分析", "Seven Core Modules Analysis"),
    "evidence_classification": ("事实, 观点和推断分层", "Fact, Opinion, and Inference Layers"),
    "pressure_test": ("多视角压力测试", "Multi-Perspective Pressure Test"),
    "risk_uncertainty": ("风险, 机会和不确定性", "Risks, Opportunities, and Uncertainties"),
    "verification_checklist": ("后续验证清单", "Follow-up Verification Checklist"),
    "compliance_checklist": ("报告合规自检表", "Report Compliance Checklist"),
}


COMPANY_ROUTE_HEADINGS = [
    "## 0. 研报前置区",
    "### 0.1 报告摘要",
    "### 0.2 关键结论",
    "### 0.3 核心指标总览",
    "### 0.4 图表清单或图表占位",
    "## 1. 目标公司/产品综合判断",
    "## 2. 研究边界",
    "### 2.1 研究计划摘要",
    "### 2.2 来源矩阵和证据质量",
    "### 2.3 检索缺口闭环结果",
    "## 3. 宏观环境分析",
    "## 4. 中观行业分析",
    "### 4.1 行业一句话定义",
    "### 4.2 行业关键指标",
    "### 4.3 行业地图",
    "### 4.4 生命周期判断",
    "## 5. 七个核心模块分析",
    "### 5.1 可行性",
    "### 5.2 规模性",
    "### 5.3 防守性",
    "### 5.4 盈利性",
    "### 5.5 估值",
    "### 5.6 外部因素",
    "### 5.7 景气度",
    "## 6. 微观公司/产品分析",
    "## 7. SWOT",
    "## 9. 竞争对手对比",
    "## 10. 事实, 观点和推断分层",
    "## 12. 多视角压力测试",
    "## 13. 风险, 机会和不确定性",
    "## 14. 后续行动建议",
    "## 15. 方法论和数据来源说明",
    "## 16. 后续验证清单",
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
    "### 2.3 检索缺口闭环结果",
    "## 3. 行业地图",
    "## 4. 生命周期判断",
    "## 5. 七个核心模块分析",
    "### 5.1 可行性",
    "### 5.2 规模性",
    "### 5.3 防守性",
    "### 5.4 盈利性",
    "### 5.5 估值",
    "### 5.6 外部因素",
    "### 5.7 景气度",
    "## 7. 事实, 观点和推断分层",
    "## 8. 多视角压力测试",
    "## 9. 风险, 机会和不确定性",
    "## 10. 后续验证清单",
    "## 11. 报告合规自检表",
]

SPECIFIC_HEADINGS = [
    "## 1. 直接回答",
    "## 2. 结论摘要",
    "## 3. 研究边界",
    "### 3.1 研究计划摘要",
    "### 3.2 来源矩阵和证据质量",
    "### 3.3 检索缺口闭环结果",
    "## 4. 行业一句话定义",
    "## 5. 行业地图",
    "## 6. 问题拆解和议题树",
    "## 7. 证据链分析",
    "## 8. 生命周期判断",
    "## 9. 七个核心模块分析",
    "### 9.1 可行性",
    "### 9.2 规模性",
    "### 9.3 防守性",
    "### 9.4 盈利性",
    "### 9.5 估值",
    "### 9.6 外部因素",
    "### 9.7 景气度",
    "## 10. 多视角压力测试",
    "## 11. 风险, 机会和不确定性",
    "## 12. 后续验证清单",
    "## 13. 报告合规自检表",
]


ENGLISH_HEADING_ALIASES = {
    "## 0. Research Front Matter": "## 0. 研报前置区",
    "### 0.1 Executive Summary": "### 0.1 报告摘要",
    "### 0.2 Key Conclusions": "### 0.2 关键结论",
    "### 0.3 Core Metrics Overview": "### 0.3 核心指标总览",
    "### 0.4 Exhibit List or Placeholders": "### 0.4 图表清单或图表占位",
    "## 1. Target Company/Product Overall Assessment": "## 1. 目标公司/产品综合判断",
    "## 1. Direct Answer": "## 1. 直接回答",
    "## 1. One-Sentence Industry Definition": "## 1. 行业一句话定义",
    "## 2. Conclusion Summary": "## 2. 结论摘要",
    "## 2. Research Scope": "## 2. 研究边界",
    "### 2.1 Research Plan Summary": "### 2.1 研究计划摘要",
    "### 2.2 Source Matrix and Evidence Quality": "### 2.2 来源矩阵和证据质量",
    "### 2.3 Retrieval Gap Closure Results": "### 2.3 检索缺口闭环结果",
    "## 3. Research Scope": "## 3. 研究边界",
    "### 3.1 Research Plan Summary": "### 3.1 研究计划摘要",
    "### 3.2 Source Matrix and Evidence Quality": "### 3.2 来源矩阵和证据质量",
    "### 3.3 Retrieval Gap Closure Results": "### 3.3 检索缺口闭环结果",
    "## 3. Macro Environment Analysis": "## 3. 宏观环境分析",
    "## 3. Industry Map": "## 3. 行业地图",
    "## 4. One-Sentence Industry Definition": "## 4. 行业一句话定义",
    "## 5. Industry Map": "## 5. 行业地图",
    "## 4. Meso Industry Analysis": "## 4. 中观行业分析",
    "### 4.0 Multi-Business Meso Breakdown": "### 4.0 多业务线中观拆分",
    "### 4.1 One-Sentence Industry Definition": "### 4.1 行业一句话定义",
    "### 4.2 Key Industry Metrics": "### 4.2 行业关键指标",
    "### 4.3 Industry Map": "### 4.3 行业地图",
    "### 4.4 Lifecycle Assessment": "### 4.4 生命周期判断",
    "## 4. Lifecycle Assessment": "## 4. 生命周期判断",
    "## 6. Problem Decomposition and Issue Tree": "## 6. 问题拆解和议题树",
    "## 5. Seven Core Modules Analysis": "## 5. 七个核心模块分析",
    "### 5.1 Feasibility": "### 5.1 可行性",
    "### 5.2 Scalability": "### 5.2 规模性",
    "### 5.3 Defensibility": "### 5.3 防守性",
    "### 5.4 Profitability": "### 5.4 盈利性",
    "### 5.5 Valuation": "### 5.5 估值",
    "### 5.6 External Factors": "### 5.6 外部因素",
    "### 5.7 Prosperity": "### 5.7 景气度",
    "## 7. Evidence Chain Analysis": "## 7. 证据链分析",
    "## 6. Micro Company/Product Analysis": "## 6. 微观公司/产品分析",
    "## 6. Trend Outlook": "## 6. 趋势推演",
    "## 8. Lifecycle Assessment": "## 8. 生命周期判断",
    "## 9. Risks, Opportunities, and Uncertainties": "## 9. 风险, 机会和不确定性",
    "## 7. SWOT": "## 7. SWOT",
    "## 8. Business/Product Portfolio Analysis": "## 8. 业务/产品组合分析",
    "## 7. Fact, Opinion, and Inference Layers": "## 7. 事实, 观点和推断分层",
    "## 8. Multi-Perspective Pressure Test": "## 8. 多视角压力测试",
    "## 9. Seven Core Modules Analysis": "## 9. 七个核心模块分析",
    "### 9.1 Feasibility": "### 9.1 可行性",
    "### 9.2 Scalability": "### 9.2 规模性",
    "### 9.3 Defensibility": "### 9.3 防守性",
    "### 9.4 Profitability": "### 9.4 盈利性",
    "### 9.5 Valuation": "### 9.5 估值",
    "### 9.6 External Factors": "### 9.6 外部因素",
    "### 9.7 Prosperity": "### 9.7 景气度",
    "## 10. Multi-Perspective Pressure Test": "## 10. 多视角压力测试",
    "## 9. Competitor Comparison": "## 9. 竞争对手对比",
    "## 10. Fact, Opinion, and Inference Layers": "## 10. 事实, 观点和推断分层",
    "## 10. Follow-up Verification Checklist": "## 10. 后续验证清单",
    "## 11. Risks, Opportunities, and Uncertainties": "## 11. 风险, 机会和不确定性",
    "## 11. Capital-Market Performance and Valuation Expectation Changes": "## 11. 资本市场表现与估值预期变化",
    "### 11.1 Share-Price Performance Breakdown": "### 11.1 股价表现拆解",
    "### 11.2 Fundamental Changes": "### 11.2 基本面变化",
    "### 11.3 Valuation Logic and Market Expectation Gap": "### 11.3 估值逻辑和市场预期差",
    "### 11.4 Upside Catalysts, Downside Risks, and Scenario Analysis": "### 11.4 上涨触发器, 下跌风险和情景分析",
    "## 11. Report Compliance Checklist": "## 11. 报告合规自检表",
    "## 12. Follow-up Verification Checklist": "## 12. 后续验证清单",
    "## 12. Multi-Perspective Pressure Test": "## 12. 多视角压力测试",
    "## 13. Report Compliance Checklist": "## 13. 报告合规自检表",
    "## 13. Risks, Opportunities, and Uncertainties": "## 13. 风险, 机会和不确定性",
    "## 14. Recommended Next Actions": "## 14. 后续行动建议",
    "## 15. Methodology and Data Sources": "## 15. 方法论和数据来源说明",
    "## 16. Follow-up Verification Checklist": "## 16. 后续验证清单",
    "## 17. Report Compliance Checklist": "## 17. 报告合规自检表",
}


ENGLISH_TERM_ALIASES = {
    "This report is for research and informational purposes only. It does not constitute investment advice or any guarantee of returns.": "本报告仅供研究和信息参考, 不构成投资建议, 也不构成任何收益承诺.",
    "Multi-Perspective Pressure Test": "多视角压力测试",
    "Fact, Opinion, and Inference": "事实/观点/推断",
    "Research Front Matter": "研报前置区",
    "Key Metrics and Follow-up Verification": "关键指标和后续验证",
    "Follow-up Verification Checklist": "后续验证清单",
    "Research Implication": "研究含义",
    "Attempted Rounds and Sources": "已尝试轮次和来源",
    "Why It Still Matters": "为什么仍重要",
    "Why It Matters": "为什么重要",
    "Unresolved Reason": "未补齐原因",
    "Next Source": "下一步来源",
    "Current Status": "当前状态",
    "Research Plan Summary": "研究计划摘要",
    "Research Brief": "研究简报",
    "Seven Core Modules": "七个核心模块",
    "Source Matrix": "来源矩阵",
    "Retrieval Gap Closure Results": "检索缺口闭环结果",
    "Key Claim": "关键 Claim",
    "Evidence Quality": "证据质量",
    "Independent Verification Status": "独立验证状态",
    "Limitations and Gap Handling": "限制和缺口处理",
    "Current Evidence Status": "当前证据状态",
    "Fact Risk": "事实风险",
    "Assumption Risk": "假设风险",
    "Data Gap": "数据缺口",
    "Upside Opportunity": "上行机会",
    "Trigger Condition": "触发条件",
    "Fact/Opinion/Inference": "事实/观点/推断",
    "Pressure Test": "压力测试",
    "Report Compliance Checklist": "报告合规自检表",
    "Report Route": "报告路由",
    "Conditional Modules": "条件模块",
    "Item": "项目",
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
    "Evidence Tier": "证据层级",
    "Retrieval Status": "检索状态",
    "Limitations": "限制",
    "Primary-Source Status": "来源状态",
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
    "Challenge ID": "质疑 ID",
    "Target Claim/Section": "目标 Claim/章节",
    "Materiality": "重要性",
    "Core Challenge": "核心质疑",
    "Resolution": "裁决",
    "Evidence/Gap": "证据/Gap",
    "Report Change": "报告改动",
    "Reviewer Status": "复核状态",
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
    "### 9.1 可行性",
    "### 9.2 规模性",
    "### 9.3 防守性",
    "### 9.4 盈利性",
    "### 9.5 估值",
    "### 9.6 外部因素",
    "### 9.7 景气度",
]

COMPANY_MODULE_HEADINGS = OVERVIEW_MODULE_HEADINGS

CANONICAL_FIELD_CONTRACTS = {
    "overview": {
        "zh": {
            "tables": [
                ("### 2.2 来源矩阵和证据质量", ["关键 Claim", "来源类型", "本报告用途", "证据层级", "证据质量", "来源状态", "独立验证状态", "限制和缺口处理"]),
                ("### 2.3 检索缺口闭环结果", ["缺口", "已尝试轮次和来源", "当前状态", "为什么仍重要", "未补齐原因", "下一步来源"]),
                ("## 7. 事实, 观点和推断分层", ["类型", "内容", "来源/依据", "证据层级", "证据质量", "来源状态", "置信度"]),
                ("## 8. 多视角压力测试", ["质疑 ID", "视角", "目标 Claim/章节", "重要性", "核心质疑", "裁决", "证据/Gap", "报告改动", "复核状态"]),
                ("## 10. 后续验证清单", ["待验证问题", "当前证据状态", "为什么重要", "推荐来源", "优先级"]),
                ("## 11. 报告合规自检表", ["检查项", "是否通过", "说明"]),
            ],
            "labels": [
                ("## 4. 生命周期判断", ["阶段结论", "证据", "反证", "置信度", "研究含义"]),
                *[(heading, ["结论", "证据", "机制", "研究含义", "关键指标和后续验证"]) for heading in OVERVIEW_MODULE_HEADINGS],
            ],
            "rows": [],
        },
        "en": {
            "tables": [
                ("### 2.2 Source Matrix and Evidence Quality", ["Key Claim", "Source Type", "Use in This Report", "Evidence Tier", "Evidence Quality", "Source Status", "Independent Verification Status", "Limitations and Gap Handling"]),
                ("### 2.3 Retrieval Gap Closure Results", ["Gap", "Attempted Rounds and Sources", "Current Status", "Why It Still Matters", "Unresolved Reason", "Next Source"]),
                ("## 7. Fact, Opinion, and Inference Layers", ["Type", "Content", "Source/Basis", "Evidence Tier", "Evidence Quality", "Source Status", "Confidence"]),
                ("## 8. Multi-Perspective Pressure Test", ["Challenge ID", "Perspective", "Target Claim/Section", "Materiality", "Core Challenge", "Resolution", "Evidence/Gap", "Report Change", "Reviewer Status"]),
                ("## 10. Follow-up Verification Checklist", ["Verification Item", "Current Evidence Status", "Why It Matters", "Recommended Source", "Priority"]),
                ("## 11. Report Compliance Checklist", ["Check", "Passed", "Explanation"]),
            ],
            "labels": [
                ("## 4. Lifecycle Assessment", ["Lifecycle Phase", "Evidence", "Counterevidence", "Confidence", "Research Implication"]),
                *[(heading, ["Conclusion", "Evidence", "Mechanism", "Research Implication", "Key Metrics and Follow-up Verification"]) for heading in ENGLISH_HEADING_ALIASES if heading.startswith("### 5.")],
            ],
            "rows": [],
        },
    },
    "specific": {
        "zh": {
            "tables": [
                ("### 3.2 来源矩阵和证据质量", ["关键 Claim", "来源类型", "本报告用途", "证据层级", "证据质量", "来源状态", "独立验证状态", "限制和缺口处理"]),
                ("### 3.3 检索缺口闭环结果", ["缺口", "已尝试轮次和来源", "当前状态", "为什么仍重要", "未补齐原因", "下一步来源"]),
                ("## 7. 证据链分析", ["子问题", "结论", "事实", "观点", "推断", "来源/依据", "证据层级", "证据质量", "来源状态", "置信度"]),
                ("## 10. 多视角压力测试", ["质疑 ID", "视角", "目标 Claim/章节", "重要性", "核心质疑", "裁决", "证据/Gap", "报告改动", "复核状态"]),
                ("## 12. 后续验证清单", ["待验证问题", "当前证据状态", "为什么重要", "推荐来源", "优先级"]),
                ("## 13. 报告合规自检表", ["检查项", "是否通过", "说明"]),
            ],
            "labels": [
                ("## 8. 生命周期判断", ["阶段结论", "证据", "反证", "置信度", "研究含义"]),
                *[(heading, ["结论", "证据", "机制", "研究含义", "关键指标和后续验证"]) for heading in SPECIFIC_MODULE_HEADINGS],
            ],
            "rows": [],
        },
        "en": {
            "tables": [
                ("### 3.2 Source Matrix and Evidence Quality", ["Key Claim", "Source Type", "Use in This Report", "Evidence Tier", "Evidence Quality", "Source Status", "Independent Verification Status", "Limitations and Gap Handling"]),
                ("### 3.3 Retrieval Gap Closure Results", ["Gap", "Attempted Rounds and Sources", "Current Status", "Why It Still Matters", "Unresolved Reason", "Next Source"]),
                ("## 7. Evidence Chain Analysis", ["Sub-question", "Conclusion", "Fact", "Opinion", "Inference", "Source/Basis", "Evidence Tier", "Evidence Quality", "Source Status", "Confidence"]),
                ("## 10. Multi-Perspective Pressure Test", ["Challenge ID", "Perspective", "Target Claim/Section", "Materiality", "Core Challenge", "Resolution", "Evidence/Gap", "Report Change", "Reviewer Status"]),
                ("## 12. Follow-up Verification Checklist", ["Verification Item", "Current Evidence Status", "Why It Matters", "Recommended Source", "Priority"]),
                ("## 13. Report Compliance Checklist", ["Check", "Passed", "Explanation"]),
            ],
            "labels": [
                ("## 8. Lifecycle Assessment", ["Lifecycle Phase", "Evidence", "Counterevidence", "Confidence", "Research Implication"]),
                *[(heading, ["Conclusion", "Evidence", "Mechanism", "Research Implication", "Key Metrics and Follow-up Verification"]) for heading in ENGLISH_HEADING_ALIASES if heading.startswith("### 9.")],
            ],
            "rows": [],
        },
    },
}

COMPANY_FIELD_CONTRACT = {
    "zh": {
        "tables": [
            ("### 0.3 核心指标总览", ["指标", "行业读数", "目标公司/产品读数", "判断", "证据/来源"]),
            ("### 2.2 来源矩阵和证据质量", ["关键 Claim", "来源类型", "本报告用途", "证据层级", "证据质量", "来源状态", "独立验证状态", "限制和缺口处理"]),
            ("### 2.3 检索缺口闭环结果", ["缺口", "已尝试轮次和来源", "当前状态", "为什么仍重要", "未补齐原因", "下一步来源"]),
            ("## 10. 事实, 观点和推断分层", ["类型", "内容", "来源/依据", "证据层级", "证据质量", "来源状态", "置信度"]),
            ("## 12. 多视角压力测试", ["质疑 ID", "视角", "目标 Claim/章节", "重要性", "核心质疑", "裁决", "证据/Gap", "报告改动", "复核状态"]),
            ("## 16. 后续验证清单", ["待验证问题", "当前证据状态", "为什么重要", "推荐来源", "优先级"]),
            ("## 17. 报告合规自检表", ["检查项", "是否通过", "说明"]),
        ],
        "labels": [
            ("### 4.4 生命周期判断", ["阶段结论", "证据", "反证", "置信度", "研究含义"]),
            *[(heading, ["结论", "证据", "机制", "研究含义", "关键指标和后续验证"]) for heading in COMPANY_MODULE_HEADINGS],
        ],
        "rows": [
            ("### 0.3 核心指标总览", ["市场规模", "增速/渗透率", "竞争强度", "盈利水平", "景气度", "关键风险"]),
        ],
    },
    "en": {
        "tables": [
            ("### 0.3 Core Metrics Overview", ["Metric", "Industry Reading", "Target Company/Product Reading", "Judgment", "Evidence/Source"]),
            ("### 2.2 Source Matrix and Evidence Quality", ["Key Claim", "Source Type", "Use in This Report", "Evidence Tier", "Evidence Quality", "Source Status", "Independent Verification Status", "Limitations and Gap Handling"]),
            ("### 2.3 Retrieval Gap Closure Results", ["Gap", "Attempted Rounds and Sources", "Current Status", "Why It Still Matters", "Unresolved Reason", "Next Source"]),
            ("## 10. Fact, Opinion, and Inference Layers", ["Type", "Content", "Source/Basis", "Evidence Tier", "Evidence Quality", "Source Status", "Confidence"]),
            ("## 12. Multi-Perspective Pressure Test", ["Challenge ID", "Perspective", "Target Claim/Section", "Materiality", "Core Challenge", "Resolution", "Evidence/Gap", "Report Change", "Reviewer Status"]),
            ("## 16. Follow-up Verification Checklist", ["Verification Item", "Current Evidence Status", "Why It Matters", "Recommended Source", "Priority"]),
            ("## 17. Report Compliance Checklist", ["Check", "Passed", "Explanation"]),
        ],
        "labels": [
            ("### 4.4 Lifecycle Assessment", ["Lifecycle Phase", "Evidence", "Counterevidence", "Confidence", "Research Implication"]),
            *[(heading, ["Conclusion", "Evidence", "Mechanism", "Research Implication", "Key Metrics and Follow-up Verification"]) for heading in ENGLISH_HEADING_ALIASES if heading.startswith("### 5.")],
        ],
        "rows": [
            ("### 0.3 Core Metrics Overview", ["Market Size", "Growth Rate/Penetration Rate", "Competitive Intensity", "Profitability Level", "Prosperity", "Key Risk"]),
        ],
    },
}

COMPANY_CAPITAL_FIELD_CONTRACT = {
    language: {
        **contract,
        "tables": [
            *contract["tables"][:3],
            (
                "### 4.0 多业务线中观拆分" if language == "zh" else "### 4.0 Multi-Business Meso Breakdown",
                ["业务线/行业线", "行业阶段", "竞争格局", "关键指标/景气信号", "对目标公司的含义"]
                if language == "zh"
                else ["Business Line/Industry Line", "Industry Stage", "Competitive Landscape", "Key Metrics/Prosperity Signal", "Implication for the Target Company"],
            ),
            *contract["tables"][3:],
        ],
    }
    for language, contract in COMPANY_FIELD_CONTRACT.items()
}

CANONICAL_FIELD_CONTRACTS["company"] = COMPANY_FIELD_CONTRACT
CANONICAL_FIELD_CONTRACTS["company-capital"] = COMPANY_CAPITAL_FIELD_CONTRACT

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


def markdown_table_rows(text: str, heading: str) -> tuple[list[str], list[list[str]]]:
    """
    提取指定章节第一张表格的表头和数据行.

    :param text: 报告文本.
    :param heading: 目标章节标题.
    :return: 表头和数据行.
    """
    lines = section_body(text, heading).splitlines()
    for index in range(len(lines) - 1):
        header = parse_markdown_table_cells(lines[index])
        separator = parse_markdown_table_cells(lines[index + 1])
        if not header or not is_markdown_separator_row(separator) or len(header) != len(separator):
            continue
        rows: list[list[str]] = []
        for line in lines[index + 2 :]:
            cells = parse_markdown_table_cells(line)
            if not cells:
                if rows:
                    break
                continue
            if len(cells) == len(header) and not is_markdown_separator_row(cells):
                rows.append(cells)
        return header, rows
    return [], []


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
    for heading, required_rounds in contract.get("rounds", []):
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
    validate_canonical_table_values(text, contract, errors)
    return errors


ACCESS_STATUSES = {
    "obtained",
    "public-but-technical-failure",
    "login-required",
    "paid-database",
    "API-key-required",
    "blocked",
    "not-found",
    "definition-mismatch",
}

EVIDENCE_TIERS = {"primary", "near-primary", "secondary", "weak"}
EVIDENCE_QUALITIES = {"high", "medium", "low"}
INDEPENDENCE_STATUSES = {
    "independently_verified",
    "same-origin-cross-check",
    "single-source-primary",
    "secondary-only",
    "unresolved-conflict",
}


def validate_canonical_table_values(
    text: str,
    contract: dict[str, list[tuple[str, list[str]]]],
    errors: list[str],
) -> None:
    """
    检查共同证据字段的枚举值.

    :param text: 原始 Markdown 报告文本.
    :param contract: 当前路由和语言的字段合同.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    label_options = [
        (("证据层级", "Evidence Tier"), EVIDENCE_TIERS, "evidence tier"),
        (("证据质量", "Evidence Quality"), EVIDENCE_QUALITIES, "evidence quality"),
        (("来源状态", "Source Status"), ACCESS_STATUSES, "source status"),
        (
            ("独立验证状态", "Independent Verification Status"),
            INDEPENDENCE_STATUSES,
            "independence status",
        ),
    ]
    for heading, expected_header in contract.get("tables", []):
        if heading not in text:
            continue
        lines = section_body(text, heading).splitlines()
        for index in range(len(lines) - 1):
            candidate_header = parse_markdown_table_cells(lines[index])
            separator = parse_markdown_table_cells(lines[index + 1])
            if candidate_header != expected_header or not is_markdown_separator_row(separator):
                continue
            for table_row, line in enumerate(lines[index + 2 :], start=1):
                cells = parse_markdown_table_cells(line)
                if not cells:
                    break
                if len(cells) != len(expected_header):
                    errors.append(
                        f"noncanonical table row width under {heading} row {table_row}: "
                        f"expected {len(expected_header)}, got {len(cells)}"
                    )
            break
        header, rows = markdown_table_rows(text, heading)
        if header != expected_header:
            continue
        for labels, allowed, field_name in label_options:
            label = next((candidate for candidate in labels if candidate in header), None)
            if label is None:
                continue
            column_index = header.index(label)
            for row_number, row in enumerate(rows, start=1):
                value = row[column_index]
                if value not in allowed:
                    errors.append(
                        f"noncanonical {field_name} under {heading} row {row_number}: {value!r}"
                    )


def read_jsonl(path: Path) -> list[dict[str, object]]:
    """
    读取逐行对象列表.

    :param path: 逐行对象文件路径.
    :return: 对象列表.
    """
    records: list[dict[str, object]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSONL at {path}:{line_number}: {exc}") from exc
        if not isinstance(record, dict):
            raise ValueError(f"invalid JSONL object at {path}:{line_number}")
        records.append(record)
    return records


def extract_trace_id(value: str, prefix: str) -> str:
    """
    从读者可见单元格提取唯一追踪 ID.

    :param value: Markdown 表格单元格文本.
    :param prefix: ID 前缀, 可为 `claim` 或 `gap`.
    :return: 唯一追踪 ID, 缺失或不唯一时返回空字符串.
    """
    identifiers = re.findall(rf"\b{re.escape(prefix)}-[a-z0-9]+(?:-[a-z0-9]+)*\b", value)
    return identifiers[0] if len(set(identifiers)) == 1 else ""


def normalize_trace_value(value: object) -> str:
    """
    规范化读者视图和运行工件中的可比较文本.

    :param value: 待规范化值.
    :return: 去除 Markdown 标记, 空白和末尾英文标点后的文本.
    """
    normalized = re.sub(r"[`*_\s]+", "", str(value)).strip()
    return normalized.rstrip(".,;:")


def pressure_test_heading(profile: str, language: str) -> str:
    """
    返回正式 route 对应的 Pressure Test 标题.

    :param profile: 正式报告 profile.
    :param language: 报告语言.
    :return: Pressure Test 章节标题.
    """
    number = "12" if profile in {"company", "company-capital"} else "10" if profile == "specific" else "8"
    title = "多视角压力测试" if language == "zh" else "Multi-Perspective Pressure Test"
    return f"## {number}. {title}"


def challenge_requires_reader_row(challenge: dict[str, object]) -> bool:
    """
    判断 Challenge 是否必须进入读者可见摘要.

    :param challenge: Challenge Ledger record.
    :return: 是否必须展示.
    """
    if challenge.get("materiality") == "high":
        return True
    if challenge.get("resolution") in {"confirmed", "partially_valid", "unresolved"}:
        return True
    change = normalize_trace_value(challenge.get("report_change", "")).casefold()
    no_change_values = {"", "none", "nochange", "noreportchange", "无改动", "无报告改动", "无需改动", "不改动", "未改动"}
    no_change_prefixes = tuple(f"{marker}{separator}" for marker in no_change_values - {""} for separator in (",", ":", ";"))
    return change not in no_change_values and not change.startswith(no_change_prefixes)


def validate_pressure_test_summary(
    text: str,
    profile: str,
    language: str,
    challenges_payload: dict[str, object] | None = None,
) -> list[str]:
    """
    校验九列 Pressure Test 摘要及其 Challenge Ledger 绑定.

    :param text: 原始报告文本.
    :param profile: 正式报告 profile.
    :param language: 报告语言.
    :param challenges_payload: 可选的 Challenge Ledger.
    :return: 错误列表.
    """
    errors: list[str] = []
    heading = pressure_test_heading(profile, language)
    header, rows = markdown_table_rows(text, heading)
    expected = (
        ["质疑 ID", "视角", "目标 Claim/章节", "重要性", "核心质疑", "裁决", "证据/Gap", "报告改动", "复核状态"]
        if language == "zh"
        else ["Challenge ID", "Perspective", "Target Claim/Section", "Materiality", "Core Challenge", "Resolution", "Evidence/Gap", "Report Change", "Reviewer Status"]
    )
    if header != expected:
        return [f"pressure-test: noncanonical nine-column summary under {heading}"]
    if not rows:
        return [f"pressure-test: summary under {heading} requires non-placeholder rows"]
    identifiers: set[str] = set()
    perspectives: set[str] = set()
    for row_number, row in enumerate(rows, start=1):
        challenge_id = extract_trace_id(row[0], "challenge")
        if not challenge_id:
            errors.append(f"pressure-test row {row_number}: missing unique challenge_id")
        elif challenge_id in identifiers:
            errors.append(f"pressure-test row {row_number}: duplicate challenge_id")
        identifiers.add(challenge_id)
        perspectives.add(normalize_trace_value(row[1]))
        if row[3] not in {"high", "medium", "low"}:
            errors.append(f"pressure-test row {row_number}: invalid materiality")
        if row[5] not in {"confirmed", "partially_valid", "refuted", "unresolved", "out_of_scope"}:
            errors.append(f"pressure-test row {row_number}: pending or invalid resolution")
        if row[8] != "closed":
            errors.append(f"pressure-test row {row_number}: open or disputed reviewer status")
        if any(not normalize_trace_value(cell) for cell in row):
            errors.append(f"pressure-test row {row_number}: empty or placeholder field")
    section = section_body(text, heading)
    core_perspectives = [
        {"industry-expert", "IndustryExpert", "行业专家"},
        {"investment-researcher", "InvestmentResearcher", "投资研究员"},
        {"policy-regulatory", "Policy/Regulatory", "政策/监管", "政策或监管研究者"},
        {"operator-entrepreneur", "Operator/Entrepreneur", "经营者/创业者", "经营者或创业者"},
    ]
    if any(not perspective_names.intersection(perspectives) for perspective_names in core_perspectives):
        errors.append("pressure-test: four core reviewer perspectives are required")
    if rough_cjk_length(section) < 220:
        errors.append(f"pressure-test: section under {heading} is too thin")
    if "multi-agent" not in section and "single-agent-simulated" not in section:
        errors.append("pressure-test: review_mode disclosure is required")
    if challenges_payload is None:
        return errors
    ledger = {
        str(item.get("challenge_id", "")): item
        for item in challenges_payload.get("challenges", [])
        if isinstance(item, dict)
    }
    role_labels = {
        "industry-expert": {"industry-expert", "IndustryExpert", "行业专家"},
        "investment-researcher": {"investment-researcher", "InvestmentResearcher", "投资研究员"},
        "policy-regulatory": {"policy-regulatory", "Policy/Regulatory", "政策/监管", "政策或监管研究者"},
        "operator-entrepreneur": {"operator-entrepreneur", "Operator/Entrepreneur", "经营者/创业者", "经营者或创业者"},
        "intern": {"intern", "实习生"},
        "devils-advocate": {"devils-advocate", "魔鬼代言人"},
    }
    for row_number, row in enumerate(rows, start=1):
        challenge_id = extract_trace_id(row[0], "challenge")
        challenge = ledger.get(challenge_id)
        if challenge is None:
            errors.append(f"pressure-test row {row_number}: challenge_id {challenge_id!r} not found in challenges.json")
            continue
        role = str(challenge.get("reviewer_role", ""))
        if normalize_trace_value(row[1]) not in role_labels.get(role, {role}):
            errors.append(f"pressure-test row {row_number}: perspective does not match {challenge_id}")
        target = normalize_trace_value(row[2])
        if str(challenge.get("target_claim_id", "")) not in row[2] or normalize_trace_value(challenge.get("target_section", "")) not in target:
            errors.append(f"pressure-test row {row_number}: target does not match {challenge_id}")
        comparisons = ((3, "materiality"), (4, "challenge"), (5, "resolution"), (7, "report_change"), (8, "reviewer_status"))
        for column, field in comparisons:
            if normalize_trace_value(row[column]) != normalize_trace_value(challenge.get(field, "")):
                errors.append(f"pressure-test row {row_number}: {field} does not match {challenge_id}")
        gap_id = challenge.get("gap_id")
        if gap_id and str(gap_id) not in row[6]:
            errors.append(f"pressure-test row {row_number}: Evidence/Gap does not match {challenge_id}")
        if not gap_id:
            source_ids = {
                str(reference.get("source_id", ""))
                for reference in challenge.get("evidence_refs", [])
                if isinstance(reference, dict)
            }
            visible_source_ids = set(re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)+", row[6]))
            if source_ids and not source_ids.issubset(visible_source_ids):
                errors.append(f"pressure-test row {row_number}: Evidence/Gap does not match {challenge_id}")
            if not source_ids and str(challenge.get("verification_method", "")) not in row[6]:
                errors.append(f"pressure-test row {row_number}: Evidence/Gap does not match {challenge_id}")
    required = {
        challenge_id
        for challenge_id, challenge in ledger.items()
        if challenge_requires_reader_row(challenge)
    }
    missing = sorted(required - identifiers)
    if missing:
        errors.append(f"pressure-test: required Challenge rows missing: {', '.join(missing)}")
    return errors


def validate_reader_view_consistency(
    report_path: Path,
    text: str,
    profile: str,
    language: str,
    run_dir: Path,
    repo_root: Path,
) -> list[str]:
    """
    检查报告读者视图与最终研究运行工件的一致性.

    :param report_path: 报告路径.
    :param text: 原始报告文本.
    :param profile: 已解析的正式报告 profile.
    :param language: 已解析的报告语言.
    :param run_dir: 研究运行目录.
    :param repo_root: 仓库根目录.
    :return: 一致性错误列表.
    """
    errors: list[str] = []
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    plan = json.loads((run_dir / "plan.json").read_text(encoding="utf-8"))
    evidence = read_jsonl(run_dir / "evidence.jsonl")
    gaps_payload = json.loads((run_dir / "gaps.json").read_text(encoding="utf-8"))
    challenge_path = run_dir / "challenges.json"
    if not challenge_path.is_file():
        return ["reader-view binding: challenges.json is required"]
    challenges_payload = json.loads(challenge_path.read_text(encoding="utf-8"))
    run_id = manifest.get("run_id")
    if manifest.get("status") != "completed" or manifest.get("engine_report_permission") is not True:
        errors.append("reader-view binding: formal report requires completed Run and Engine permission")
    if manifest.get("report_status") != "generated":
        errors.append("reader-view binding: formal report requires report_status generated")
    try:
        relative_report = report_path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        relative_report = report_path.as_posix()
    if manifest.get("report_path") != relative_report:
        errors.append(
            f"reader-view binding: manifest report_path mismatch, expected {relative_report!r}"
        )
    if report_path.stem != run_id or run_dir.name != run_id:
        errors.append("reader-view binding: report stem, run directory, and run_id must match")

    contract = CANONICAL_FIELD_CONTRACTS.get(profile, {}).get(language, {})
    source_heading = next(
        (heading for heading, fields in contract.get("tables", []) if "来源状态" in fields or "Source Status" in fields),
        "",
    )
    source_header, source_rows = markdown_table_rows(text, source_heading)
    status_label = "来源状态" if language == "zh" else "Source Status"
    independence_label = "独立验证状态" if language == "zh" else "Independent Verification Status"
    claim_label = "关键 Claim" if language == "zh" else "Key Claim"
    tier_label = "证据层级" if language == "zh" else "Evidence Tier"
    plan_claims = {
        str(claim.get("claim_id", "")): claim
        for claim in plan.get("claims", [])
        if isinstance(claim, dict)
    }
    evidence_by_claim: dict[str, list[dict[str, object]]] = {}
    for record in evidence:
        evidence_by_claim.setdefault(str(record.get("claim_id", "")), []).append(record)
    if source_header and status_label in source_header and independence_label in source_header:
        status_index = source_header.index(status_label)
        independence_index = source_header.index(independence_label)
        claim_index = source_header.index(claim_label)
        tier_index = source_header.index(tier_label)
        for row_number, row in enumerate(source_rows, start=1):
            claim_id = extract_trace_id(row[claim_index], "claim")
            status = row[status_index]
            independence = row[independence_index]
            tier = row[tier_index]
            if not claim_id:
                errors.append(f"reader-view source row {row_number}: missing unique claim_id")
                continue
            if claim_id not in plan_claims:
                errors.append(
                    f"reader-view source row {row_number}: claim_id {claim_id!r} not found in plan.json"
                )
                continue
            claim_records = evidence_by_claim.get(claim_id, [])
            if not claim_records:
                errors.append(
                    f"reader-view source row {row_number}: claim_id {claim_id!r} has no Evidence Ledger record"
                )
                continue
            claim_access = {str(record.get("access_status", "")) for record in claim_records}
            claim_independence = {
                str(record.get("independence_status", "")) for record in claim_records
            }
            claim_tiers = {str(record.get("evidence_tier", "")) for record in claim_records}
            if status not in ACCESS_STATUSES:
                errors.append(f"reader-view source row {row_number}: invalid access status {status!r}")
            elif status not in claim_access:
                errors.append(
                    f"reader-view source row {row_number}: access status {status!r} not supported for {claim_id}"
                )
            if independence not in claim_independence:
                errors.append(
                    f"reader-view source row {row_number}: independence status {independence!r} not supported for {claim_id}"
                )
            if tier not in claim_tiers:
                errors.append(
                    f"reader-view source row {row_number}: evidence tier {tier!r} not supported for {claim_id}"
                )

    gap_heading = next(
        (heading for heading, fields in contract.get("tables", []) if "当前状态" in fields or "Current Status" in fields),
        "",
    )
    gap_header, gap_rows = markdown_table_rows(text, gap_heading)
    gap_status_label = "当前状态" if language == "zh" else "Current Status"
    gap_id_label = "缺口" if language == "zh" else "Gap"
    unresolved_label = "未补齐原因" if language == "zh" else "Unresolved Reason"
    next_source_label = "下一步来源" if language == "zh" else "Next Source"
    final_gaps = {
        str(gap.get("gap_id", "")): gap
        for gap in gaps_payload.get("gaps", [])
        if isinstance(gap, dict)
    }
    closed_markers = {"已补齐", "closed", "no remaining gap", "无剩余缺口"}
    if gap_header and gap_status_label in gap_header:
        status_index = gap_header.index(gap_status_label)
        gap_id_index = gap_header.index(gap_id_label)
        unresolved_index = gap_header.index(unresolved_label)
        next_source_index = gap_header.index(next_source_label)
        for row_number, row in enumerate(gap_rows, start=1):
            status = row[status_index]
            gap_id = extract_trace_id(row[gap_id_index], "gap")
            if not final_gaps and status in closed_markers:
                continue
            if not gap_id:
                errors.append(f"reader-view gap row {row_number}: missing unique gap_id")
                continue
            gap = final_gaps.get(gap_id)
            if gap is None:
                errors.append(
                    f"reader-view gap row {row_number}: gap_id {gap_id!r} not found in gaps.json"
                )
                continue
            if status != str(gap.get("status", "")):
                errors.append(
                    f"reader-view gap row {row_number}: status {status!r} does not match {gap_id}"
                )
            if normalize_trace_value(row[unresolved_index]) != normalize_trace_value(
                gap.get("unresolved_reason", "")
            ):
                errors.append(
                    f"reader-view gap row {row_number}: unresolved reason does not match {gap_id}"
                )
            if normalize_trace_value(row[next_source_index]) != normalize_trace_value(
                gap.get("next_source_route", "")
            ):
                errors.append(
                    f"reader-view gap row {row_number}: next source does not match {gap_id}"
                )
    if challenges_payload.get("run_id") != run_id:
        errors.append("reader-view binding: challenges run_id mismatch")
    review_mode = str(challenges_payload.get("review_mode", ""))
    if review_mode not in section_body(text, pressure_test_heading(profile, language)):
        errors.append("reader-view binding: review_mode disclosure does not match challenges.json")
    errors.extend(validate_pressure_test_summary(text, profile, language, challenges_payload))
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
    trace_ids: list[str] = []

    def preserve_trace_id(match: re.Match[str]) -> str:
        """
        在英文术语归一化期间暂存 Claim 和 Gap ID.

        :param match: 追踪 ID 正则匹配对象.
        :return: 不会被术语映射改写的占位符.
        """
        trace_ids.append(match.group(0))
        return f"__TRACE_ID_{len(trace_ids) - 1}__"

    protected = re.sub(
        r"\b(?:claim|gap)-[a-z0-9]+(?:-[a-z0-9]+)*\b",
        preserve_trace_id,
        text,
    )
    normalized_lines = [ENGLISH_HEADING_ALIASES.get(line.strip(), line) for line in protected.splitlines()]
    normalized = "\n".join(normalized_lines)
    for source, target in sorted(ENGLISH_TERM_ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        pattern = rf"(?<![A-Za-z_]){re.escape(source)}(?![A-Za-z_])"
        normalized = re.sub(pattern, target, normalized, flags=re.IGNORECASE)
    for index, trace_id in enumerate(trace_ids):
        normalized = normalized.replace(f"__TRACE_ID_{index}__", trace_id)
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
        ("### 2.3 检索缺口闭环结果", 120),
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
            ["关键 Claim"],
            ["来源类型"],
            ["本报告用途"],
            ["证据层级"],
            ["证据质量"],
            ["来源状态"],
            ["独立验证状态"],
            ["限制和缺口处理"],
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
            ["证据层级"],
            ["证据质量"],
            ["来源状态"],
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
        "## 7. 证据链分析",
        [
            ["子问题"],
            ["结论"],
            ["事实"],
            ["观点"],
            ["推断"],
            ["来源/依据"],
            ["证据层级"],
            ["证据质量"],
            ["来源状态"],
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
    检查检索缺口闭环结果是否说明缺口, 三轮闭环尝试, 状态, 未补齐原因, 影响, 下一步和来源.

    :param text: Markdown 文本.
    :param heading: 检索缺口闭环结果章节标题.
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
            ["轮", "闭环", "第1轮", "第一轮"],
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
            ["已尝试轮次和来源", "三轮检索已尝试", "已尝试", "尝试来源"],
            ["当前状态", "状态"],
            ["为什么仍重要", "为什么重要", "影响"],
            ["未补齐原因", "原因"],
            ["下一步来源", "下一步"],
        ],
        errors,
    )


def require_company_compliance_checklist(text: str, capital: bool, errors: list[str]) -> None:
    """
    检查公司报告合规自检表是否覆盖关键概念.

    :param text: Markdown 文本.
    :param capital: 是否启用资本市场模块.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    require_section_min(text, "## 17. 报告合规自检表", 240, errors)
    concepts = [
        ["模板骨架", "skeleton"],
        ["研究简报", "research brief"],
        ["Deep Research"],
        ["分析层级", "层级选择", "layer"],
        ["七个核心模块", "七模块"],
        ["来源质量", "证据质量", "evidence"],
        ["一手来源", "primary"],
        ["事实/观点/推断", "事实, 观点和推断"],
        ["后续验证"],
    ]
    if capital:
        concepts.append(["资本市场"])
    require_any_terms(text, "## 17. 报告合规自检表", concepts, errors)

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
    require_section_min(text, "## 13. 风险, 机会和不确定性", 220, errors)
    require_any_terms(
        text,
        "## 13. 风险, 机会和不确定性",
        [
            ["风险"],
            ["机会"],
            ["行业结构", "行业"],
            ["目标公司", "目标产品", "公司", "产品"],
        ],
        errors,
    )
    require_section_min(text, "## 16. 后续验证清单", 180, errors)
    require_any_terms(
        text,
        "## 16. 后续验证清单",
        [
            ["待验证", "验证"],
            ["为什么重要", "重要"],
            ["推荐来源", "来源"],
            ["优先级"],
        ],
        errors,
    )


SHARED_RENDERINGS = {
    "overview": {
        "source": "### 2.2 来源矩阵和证据质量",
        "gaps": "### 2.3 检索缺口闭环结果",
        "map": "## 3. 行业地图",
        "lifecycle": "## 4. 生命周期判断",
        "modules": OVERVIEW_MODULE_HEADINGS,
        "evidence": "## 7. 事实, 观点和推断分层",
        "pressure": "## 8. 多视角压力测试",
        "risk": "## 9. 风险, 机会和不确定性",
        "verification": "## 10. 后续验证清单",
        "compliance": "## 11. 报告合规自检表",
    },
    "specific": {
        "source": "### 3.2 来源矩阵和证据质量",
        "gaps": "### 3.3 检索缺口闭环结果",
        "map": "## 5. 行业地图",
        "lifecycle": "## 8. 生命周期判断",
        "modules": SPECIFIC_MODULE_HEADINGS,
        "evidence": "## 7. 证据链分析",
        "pressure": "## 10. 多视角压力测试",
        "risk": "## 11. 风险, 机会和不确定性",
        "verification": "## 12. 后续验证清单",
        "compliance": "## 13. 报告合规自检表",
    },
    "company": {
        "source": "### 2.2 来源矩阵和证据质量",
        "gaps": "### 2.3 检索缺口闭环结果",
        "map": "### 4.3 行业地图",
        "lifecycle": "### 4.4 生命周期判断",
        "modules": COMPANY_MODULE_HEADINGS,
        "evidence": "## 10. 事实, 观点和推断分层",
        "pressure": "## 12. 多视角压力测试",
        "risk": "## 13. 风险, 机会和不确定性",
        "verification": "## 16. 后续验证清单",
        "compliance": "## 17. 报告合规自检表",
    },
}


LEGACY_HEADINGS = [
    "### 2.3 二次检索缺口",
    "### 3.3 二次检索缺口",
    "## 5. 七个核心模块加权分析",
    "## 5. 七个核心模块\n",
    "### 4.3 行业地图和目标位置",
    "## 1. 直接结论",
    "## 7. 风险和机会",
    "## 10. 风险和不确定性",
    "## 13. 风险和机会",
    "## 10. 后续研究建议",
    "## 16. 附录: 后续验证清单",
    "### 2.3 Follow-up Retrieval Gaps",
    "### 3.3 Follow-up Retrieval Gaps",
    "## 5. Weighted Analysis of Seven Core Modules",
    "### 4.3 Industry Map and Target Position",
    "## 1. Direct Conclusion",
    "## 7. Risks and Opportunities",
    "## 10. Risks and Uncertainties",
    "## 13. Risks and Opportunities",
    "## 10. Follow-up Research Recommendations",
    "## 16. Appendix: Follow-up Verification Checklist",
]


def require_heading_order(text: str, headings: list[str], errors: list[str]) -> None:
    """
    检查章节相对顺序.

    :param text: Markdown 文本.
    :param headings: 按契约顺序排列的标题.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    positions = [text.find(heading) for heading in headings]
    if any(position < 0 for position in positions):
        return
    if positions != sorted(positions):
        errors.append(f"wrong shared section order: {' -> '.join(headings)}")


def validate_shared_sections(text: str, profile: str, errors: list[str]) -> None:
    """
    检查所有正式报告共用的章节, 字段和收口顺序.

    :param text: 已归一化的 Markdown 文本.
    :param profile: 正式报告路由.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    route = "company" if profile in {"company", "company-capital"} else profile
    rendering = SHARED_RENDERINGS[route]
    for legacy_heading in LEGACY_HEADINGS:
        if legacy_heading in text:
            errors.append(f"legacy report structure is not accepted: {legacy_heading}")
    require_source_matrix_columns(text, rendering["source"], errors)
    require_retrieval_gap_details(text, rendering["gaps"], errors)
    validate_report_trace_ids(text, rendering["source"], rendering["gaps"], errors)
    require_lifecycle_depth(text, rendering["lifecycle"], ["研究含义", "研究对象"], errors)
    if route == "specific":
        require_specific_evidence_chain_columns(text, errors)
    else:
        require_fact_inference_columns(text, rendering["evidence"], errors)
    for heading in rendering["modules"]:
        require_labels(
            text,
            heading,
            ["结论", "证据", "机制", "研究含义", "关键指标和后续验证"],
            errors,
        )
    require_any_terms(
        text,
        rendering["risk"],
        [["事实风险"], ["假设风险"], ["数据缺口"], ["上行机会"], ["触发条件"]],
        errors,
    )
    require_heading_order(
        text,
        [rendering["pressure"], rendering["risk"], rendering["verification"], rendering["compliance"]],
        errors,
    )


def validate_report_trace_ids(
    text: str,
    source_heading: str,
    gap_heading: str,
    errors: list[str],
) -> None:
    """
    检查正式报告来源矩阵和缺口表中的追踪 ID.

    :param text: 已归一化的 Markdown 文本.
    :param source_heading: 来源矩阵章节标题.
    :param gap_heading: 检索缺口章节标题.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    source_header, source_rows = markdown_table_rows(text, source_heading)
    if source_header and source_header[0] == "关键 Claim":
        for row_number, row in enumerate(source_rows, start=1):
            if not extract_trace_id(row[0], "claim"):
                errors.append(f"source matrix row {row_number}: missing unique claim_id")

    gap_header, gap_rows = markdown_table_rows(text, gap_heading)
    if gap_header and gap_header[0] == "缺口" and "当前状态" in gap_header:
        status_index = gap_header.index("当前状态")
        closed_markers = {"已补齐", "closed", "no remaining gap", "无剩余缺口"}
        for row_number, row in enumerate(gap_rows, start=1):
            if row[status_index].strip().lower() in closed_markers:
                continue
            if not extract_trace_id(row[0], "gap"):
                errors.append(f"retrieval gap row {row_number}: missing unique gap_id")


def validate_conditional_modules(text: str, capital: bool, errors: list[str]) -> None:
    """
    检查公司报告条件模块的启用和禁用状态.

    :param text: 已归一化的 Markdown 文本.
    :param capital: 是否启用资本市场模块.
    :param errors: 错误列表, 会被原地追加.
    :return: None.
    """
    plan_header, plan_rows = markdown_table_rows(text, "### 2.1 研究计划摘要")
    declarations: dict[str, bool] = {}
    if plan_header == ["项目", "内容"]:
        declaration_text = next(
            (row[1] for row in plan_rows if row[0] == "条件模块"),
            "",
        )
        matches = re.findall(
            r"\b(multi_business_split|portfolio_analysis|capital_market)=(enabled|disabled)\b",
            declaration_text,
        )
        declarations = {name: state == "enabled" for name, state in matches}
    expected_keys = {"multi_business_split", "portfolio_analysis", "capital_market"}
    if set(declarations) != expected_keys:
        errors.append(
            "missing or invalid conditional module declaration under ### 2.1 研究计划摘要"
        )
        return

    capital_heading = "## 11. 资本市场表现与估值预期变化"
    multi_heading = "### 4.0 多业务线中观拆分"
    portfolio_heading = "## 8. 业务/产品组合分析"
    if declarations["capital_market"] != capital:
        errors.append("conditional module declaration conflicts with report profile: capital_market")
    if declarations["multi_business_split"] != (multi_heading in text):
        errors.append(
            "conditional module declaration conflicts with rendered section: multi_business_split"
        )
    if declarations["portfolio_analysis"] != (portfolio_heading in text):
        errors.append(
            "conditional module declaration conflicts with rendered section: portfolio_analysis"
        )
    if capital:
        require_headings(text, CAPITAL_MARKET_HEADINGS, errors)
        require_multibusiness_split_columns(text, errors)
    elif capital_heading in text:
        errors.append("unexpected conditional module: capital market section is forbidden for company profile")
    if multi_heading in text and not capital:
        require_multibusiness_split_columns(text, errors)
    if portfolio_heading in text:
        require_section_min(text, portfolio_heading, 180, errors)
        require_any_terms(
            text,
            portfolio_heading,
            [["业务", "产品"], ["资源配置", "组合"], ["证据", "验证"]],
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
    require_headings(text, COMPANY_ROUTE_HEADINGS, errors)
    validate_shared_sections(text, "company-capital" if capital else "company", errors)
    validate_conditional_modules(text, capital, errors)
    require_company_exhibit_list(text, errors)
    require_company_report_front_density(text, errors)
    require_company_core_metrics_overview(text, errors)
    require_company_research_trace_density(text, errors)
    require_company_compliance_checklist(text, capital, errors)
    require_company_pressure_test(text, errors)
    require_company_macro_meso_depth(text, errors)
    require_any_terms(
        text,
        "### 4.3 行业地图",
        [["目标位置", "目标公司", "目标产品", "研究对象位置"]],
        errors,
    )
    require_company_micro_depth(text, errors)
    require_company_risk_and_verification_depth(text, errors)
    require_company_module_verification_blocks(text, errors)
    if capital:
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
        require_labels(text, heading, ["结论", "证据", "机制", "研究含义", "关键指标和后续验证"], errors)
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
    validate_shared_sections(text, "overview", errors)
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
        require_labels(text, heading, ["结论", "证据", "机制", "研究含义", "关键指标和后续验证"], errors)
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
    validate_shared_sections(text, "specific", errors)
    require_section_min(text, "## 1. 直接回答", 250, errors)
    for heading in [
        "### 9.1 可行性",
        "### 9.2 规模性",
        "### 9.3 防守性",
        "### 9.4 盈利性",
        "### 9.5 估值",
        "### 9.6 外部因素",
        "### 9.7 景气度",
    ]:
        require_section_min(text, heading, 150, errors)
        require_labels(text, heading, ["结论", "证据", "机制", "研究含义", "关键指标和后续验证"], errors)
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
        "检索缺口闭环结果",
        "事实/观点/推断",
        "压力测试",
        "报告合规自检表",
    ]:
        if term not in text:
            errors.append(f"missing prompt-builder report contract: {term}")
    for path in [
        "<skill-root>/scripts/report_contract_check.py",
        "<skill-root>/scripts/deep_search_contract_check.py",
    ]:
        if path not in text:
            errors.append(f"missing prompt-builder maintenance path: {path}")
    if "公司/产品" in text or "公司产品" in text or "company-product-template" in text:
        for term in ["0. 研报前置区", "5.1", "5.7", "微观公司/产品分析"]:
            if term not in text:
                errors.append(f"missing company prompt-builder contract: {term}")
    if "资本市场" in text or "股价" in text or "上市公司" in text:
        for term in ["11.1", "11.2", "11.3", "11.4", "不构成投资建议"]:
            if term not in text:
                errors.append(f"missing capital prompt-builder contract: {term}")
        if "--profile company-capital" not in text:
            errors.append("capital prompt-builder must use --profile company-capital")
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
    if length > 1500:
        errors.append(f"short answer too long: length {length}, expected <= 1500")
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
    if resolved_profile in {"company-capital", "company", "overview", "specific"}:
        errors.extend(validate_pressure_test_summary(text, resolved_profile, resolved_language))
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
    if "## " not in text:
        return "short"
    return "unknown"


def sample_company_research_plan(capital: bool) -> str:
    """
    构造公司样例的研究计划摘要.

    :param capital: 是否启用资本市场条件模块.
    :return: Markdown 研究计划表格.
    """
    capital_state = "enabled" if capital else "disabled"
    return "\n".join(
        [
            "| 项目 | 内容 |",
            "|---|---|",
            "| 母问题 | 示例公司或产品的竞争力, 增长质量, 风险和价值如何 |",
            "| 子问题 | 行业位置, 多业务差异, 盈利能力, 估值逻辑, 竞争优势和主要风险 |",
            "| 选择的分析层级 | 使用宏观, 中观和微观层, 并在资本市场问题中增加预期差分析 |",
            "| 必须验证的事项 | 行业规模和阶段, 公司经营与财务表现, 竞争位置, 证据缺口和风险触发条件 |",
            "| 条件模块 | multi_business_split=enabled; portfolio_analysis=disabled; "
            f"capital_market={capital_state} |",
        ]
    )


def sample_overview_report(body_repeat: int) -> str:
    """
    构造行业全览报告样例.

    :param body_repeat: 普通章节重复次数, 用于控制整篇长度.
    :return: Markdown 样例文本.
    """
    body = "行业研究边界来源证据行业地图生命周期事实观点推断压力测试合规检查" * body_repeat
    source_matrix_body = "\n".join(
        [
            "| 关键 Claim | 来源类型 | 本报告用途 | 证据层级 | 证据质量 | 来源状态 | 独立验证状态 | 限制和缺口处理 |",
            "|---|---|---|---|---|---|---|---|",
            "| 市场规模与供需 | 官方统计/监管/行业协会 | 核实市场, 政策, 供需和价格 | primary | high | obtained | independently_verified | 口径和时效限制已说明 |",
            "| 趋势与预测 | 可信数据库/国际组织/行业报告 | 对比趋势和预测指标 | near-primary | medium | paid-database | single-source-primary | 预测假设仍需验证 |",
            "| 补充市场信号 | 媒体/访谈/专家观点 | 补充观点 | secondary | low | obtained | secondary-only | 不能替代一手事实 |",
            body,
        ]
    )
    fact_inference_body = "\n".join(
        [
            "| 类型 | 内容 | 来源/依据 | 证据层级 | 证据质量 | 来源状态 | 置信度 |",
            "|---|---|---|---|---|---|---|",
            "| 事实 | 行业事实 | 官方统计 | primary | high | obtained | 高 |",
            "| 观点 | 专家观点 | 访谈或报告 | secondary | medium | obtained | 中 |",
            "| 推断 | 趋势推断 | 基于事实和观点 | near-primary | medium | obtained | 中 |",
            body,
        ]
    )
    lifecycle_body = "\n\n".join(
        [
            "**阶段结论:** " + "行业处于成长期向成熟期过渡阶段, 需求仍增长但竞争结构开始分化." * 8,
            "**证据:** " + "市场规模, 渗透率, 供需关系和竞争格局仍有增长信号, 但价格和利润率压力已经出现." * 8,
            "**反证:** " + "如果监管口径, 替代品扩张或需求放缓数据持续恶化, 生命周期可能更接近成熟期." * 8,
            "**置信度:** " + "中等, 因为关键行业数据仍需要官方统计, 行业协会和可信数据库继续验证." * 8,
            "**研究含义:** " + "七模块应更重视盈利性, 防守性和景气度拐点." * 8,
        ]
    )
    retrieval_gap_body = "\n".join(
        [
            "| 缺口 | 已尝试轮次和来源 | 当前状态 | 为什么仍重要 | 未补齐原因 | 下一步来源 |",
            "|---|---|---|---|---|---|",
            "| 最新市场规模, 渗透率, 价格变化和供需数据 | 第1轮: 官方统计和监管文件. 第2轮: 行业协会和可信数据库. 第3轮: 替代关键词, 本地语言和可信二手交叉验证 | 仍未补齐 | 这些缺口会影响行业生命周期, 七模块权重和风险机会判断 | 部分数据库需要付费库或登录, 公开检索无可靠结果, 口径不匹配 | 官方统计, 行业协会, 监管公告, 可信数据库 |",
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
            "**研究含义:** " + "研究含义" * 25,
            "**关键指标和后续验证:** " + "跟踪指标和一手来源验证" * 25,
        ]
    )
    pressure_test_body = "\n".join(
        [
            "review_mode: single-agent-simulated. 以下角色视角由同一 Agent 分别执行, 不代表独立 Agent 审查.",
            "| 质疑 ID | 视角 | 目标 Claim/章节 | 重要性 | 核心质疑 | 裁决 | 证据/Gap | 报告改动 | 复核状态 |",
            "|---|---|---|---|---|---|---|---|---|",
            "| challenge-industry | 行业专家 | claim-market-size / 4. 生命周期判断 | high | 行业判断可能过于乐观 | confirmed | gap-market-definition | 收窄生命周期结论并披露定义限制 | closed |",
            "| challenge-investment | 投资研究员 | claim-market-size / 5.4 盈利性 | medium | 盈利假设可能高估 | refuted | source-example | 保留原结论并补充复核依据 | closed |",
            "| challenge-policy | 政策/监管 | claim-market-size / 5.6 外部因素 | medium | 监管边界可能遗漏 | out_of_scope | source-policy | 在研究边界中明确排除项 | closed |",
            "| challenge-operator | 经营者/创业者 | claim-market-size / 5.1 可行性 | medium | 执行难度可能被低估 | partially_valid | source-operator | 下调执行置信度并增加条件 | closed |",
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
    risk_body = "事实风险, 假设风险, 数据缺口, 上行机会和触发条件需要分别评估." * 40
    verification_body = "\n".join(
        [
            "| 待验证问题 | 当前证据状态 | 为什么重要 | 推荐来源 | 优先级 |",
            "|---|---|---|---|---|",
            "| 行业需求与利润池 | 部分补齐 | 影响阶段和盈利判断 | 官方统计和行业协会 | 高 |",
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
        "### 2.3 检索缺口闭环结果",
        retrieval_gap_body,
        "## 3. 行业地图",
        mermaid_body,
        "## 4. 生命周期判断",
        lifecycle_body,
        "## 5. 七个核心模块分析",
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
            "## 6. 趋势推演",
            body,
            "## 7. 事实, 观点和推断分层",
            fact_inference_body,
            "## 8. 多视角压力测试",
            pressure_test_body,
            "## 9. 风险, 机会和不确定性",
            risk_body,
            "## 10. 后续验证清单",
            verification_body,
            "## 11. 报告合规自检表",
            compliance_body,
            "本报告仅供研究和信息参考, 不构成投资建议, 也不构成任何收益承诺.",
        ]
    )
    return add_sample_trace_ids("\n\n".join(parts))


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
            "| 关键 Claim | 来源类型 | 本报告用途 | 证据层级 | 证据质量 | 来源状态 | 独立验证状态 | 限制和缺口处理 |",
            "|---|---|---|---|---|---|---|---|",
            "| 价格战供需证据 | 官方统计/监管/行业协会 | 核实市场, 政策, 供需和价格 | primary | high | obtained | independently_verified | 口径和时效限制已说明 |",
            "| 趋势与预测 | 可信数据库/国际组织/行业报告 | 对比趋势和预测指标 | near-primary | medium | paid-database | single-source-primary | 预测假设仍需验证 |",
            "| 补充市场信号 | 媒体/访谈/专家观点 | 补充观点 | secondary | low | obtained | secondary-only | 不能替代一手事实 |",
            body,
        ]
    )
    evidence_chain_body = "\n".join(
        [
            "| 子问题 | 结论 | 事实 | 观点 | 推断 | 来源/依据 | 证据层级 | 证据质量 | 来源状态 | 置信度 |",
            "|---|---|---|---|---|---|---|---|---|---|",
            "| 子问题 | 结论 | 事实 | 观点 | 推断 | 官方统计 | primary | high | obtained | 中 |",
            body,
        ]
    )
    lifecycle_body = "\n\n".join(
        [
            "**阶段结论:** " + "与用户问题相关的行业环节处于成长期向成熟期过渡阶段, 增长仍在但竞争和利润压力上升." * 8,
            "**证据:** " + "需求指标, 供给扩张, 价格变化和政策信号共同说明行业仍有增量, 但边际变化正在变复杂." * 8,
            "**反证:** " + "如果后续数据证明需求已经放缓, 库存上升或政策收紧, 当前阶段判断需要下修为成熟期压力." * 8,
            "**置信度:** " + "中等, 因为仍需验证官方统计, 行业协会和企业经营数据." * 8,
            "**研究含义:** " + "解释原因时不能只看短期事件, 还要看生命周期切换." * 8,
        ]
    )
    retrieval_gap_body = "\n".join(
        [
            "| 缺口 | 已尝试轮次和来源 | 当前状态 | 为什么仍重要 | 未补齐原因 | 下一步来源 |",
            "|---|---|---|---|---|---|",
            "| 与用户问题直接相关的最新行业指标, 政策口径和供需变化数据 | 第1轮: 官方统计和监管文件. 第2轮: 行业协会, 公司公告和可信数据库. 第3轮: 替代关键词, 本地语言和可信二手交叉验证 | 仍未补齐 | 这些缺口会影响直接回答, 议题树排序和证据链置信度 | 部分来源需要登录或付费库, 公开检索无可靠结果, 口径不匹配 | 官方统计, 监管公告, 行业协会数据, 公司公告和可信数据库 |",
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
            "**研究含义:** " + "问题含义" * 20,
            "**关键指标和后续验证:** " + "跟踪指标和一手来源验证" * 20,
        ]
    )
    pressure_test_body = "\n".join(
        [
            "review_mode: single-agent-simulated. 以下角色视角由同一 Agent 分别执行, 不代表独立 Agent 审查.",
            "| 质疑 ID | 视角 | 目标 Claim/章节 | 重要性 | 核心质疑 | 裁决 | 证据/Gap | 报告改动 | 复核状态 |",
            "|---|---|---|---|---|---|---|---|---|",
            "| challenge-industry | 行业专家 | claim-market-size / 8. 生命周期判断 | high | 问题判断可能过于乐观 | confirmed | gap-market-definition | 收窄直接回答并披露限制 | closed |",
            "| challenge-investment | 投资研究员 | claim-market-size / 9.4 盈利性 | medium | 盈利影响可能高估 | refuted | source-example | 保留原结论并补充复核依据 | closed |",
            "| challenge-policy | 政策/监管 | claim-market-size / 9.6 外部因素 | medium | 政策影响可能遗漏 | out_of_scope | source-policy | 在研究边界中明确排除项 | closed |",
            "| challenge-operator | 经营者/创业者 | claim-market-size / 9.1 可行性 | medium | 执行影响可能低估 | partially_valid | source-operator | 下调置信度并增加适用条件 | closed |",
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
    risk_body = "事实风险, 假设风险, 数据缺口, 上行机会和触发条件需要分别检验." * 40
    verification_body = "\n".join(
        [
            "| 待验证问题 | 当前证据状态 | 为什么重要 | 推荐来源 | 优先级 |",
            "|---|---|---|---|---|",
            "| 价格战驱动因素 | 部分补齐 | 影响直接回答 | 官方统计和行业协会 | 高 |",
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
        "### 3.3 检索缺口闭环结果",
        retrieval_gap_body,
        "## 4. 行业一句话定义",
        body,
        "## 5. 行业地图",
        mermaid_body,
        "## 6. 问题拆解和议题树",
        body,
        "## 7. 证据链分析",
        evidence_chain_body,
        "## 8. 生命周期判断",
        lifecycle_body,
        "## 9. 七个核心模块分析",
    ]
    for heading in [
        "### 9.1 可行性",
        "### 9.2 规模性",
        "### 9.3 防守性",
        "### 9.4 盈利性",
        "### 9.5 估值",
        "### 9.6 外部因素",
        "### 9.7 景气度",
    ]:
        parts.extend([heading, module_body])
    parts.extend(
        [
            "## 10. 多视角压力测试",
            pressure_test_body,
            "## 11. 风险, 机会和不确定性",
            risk_body,
            "## 12. 后续验证清单",
            verification_body,
            "## 13. 报告合规自检表",
            compliance_body,
            "本报告仅供研究和信息参考, 不构成投资建议, 也不构成任何收益承诺.",
        ]
    )
    return add_sample_trace_ids("\n\n".join(parts))


def sample_company_capital_without_priority_block() -> str:
    """
    构造缺少资本市场优先模块第五块的样例.

    :return: Markdown 样例文本.
    """
    module_body = "\n\n".join(
        [
            "**结论:** " + "结论内容" * 60,
            "**证据:** " + "证据内容" * 60,
            "**机制:** " + "机制内容" * 60,
            "**研究含义:** " + "影响内容" * 60,
        ]
    )
    long_body = "分析内容" * 260
    source_matrix_body = "\n".join(
        [
            "| 关键 Claim | 来源类型 | 本报告用途 | 证据层级 | 证据质量 | 来源状态 | 独立验证状态 | 限制和缺口处理 |",
            "|---|---|---|---|---|---|---|---|",
            "| 公司财务与经营 | 公司公告/财报/IR/交易所文件 | 核实公司和财务事实 | primary | high | obtained | single-source-primary | 标记缺口和下一步来源 |",
            "| 股价与估值 | 交易所/可信市场数据库 | 核实股价, 估值和市值 | near-primary | high | obtained | independently_verified | 行情口径限制已说明 |",
            "| 行业趋势与预测 | 可信数据库/行业报告 | 对比趋势和预测指标 | near-primary | medium | paid-database | single-source-primary | 预测假设仍需验证 |",
            "| 补充市场信号 | 媒体/访谈/专家观点 | 补充观点 | secondary | low | obtained | secondary-only | 必须交叉验证 |",
            long_body,
        ]
    )
    fact_inference_body = "\n".join(
        [
            "| 类型 | 内容 | 来源/依据 | 证据层级 | 证据质量 | 来源状态 | 置信度 |",
            "|---|---|---|---|---|---|---|",
            "| 事实 | 公司财务和运营事实 | 公司公告或财报 | primary | high | obtained | 高 |",
            "| 待核验事实 | 二手行情或媒体转述数据 | 市场数据库或媒体 | secondary | low | obtained | 中 |",
            "| 观点 | 分析师或媒体观点 | 来源立场 | secondary | medium | obtained | 中 |",
            "| 推断 | 估值和预期差判断 | 基于事实和观点 | near-primary | medium | obtained | 中 |",
            long_body,
        ]
    )
    retrieval_gap_body = "\n".join(
        [
            "| 缺口 | 已尝试轮次和来源 | 当前状态 | 为什么仍重要 | 未补齐原因 | 下一步来源 |",
            "|---|---|---|---|---|---|",
            "| 目标公司分业务线收入, 毛利率, 现金流, 订单交付, 股价区间和估值倍数的最新一手口径 | 第1轮: 公司公告, 财报和 IR 材料. 第2轮: 交易所文件, 交易所行情和可信市场数据库. 第3轮: 替代关键词, 本地语言和可信二手交叉验证 | 仍未补齐 | 这些缺口会影响基本面变化, 估值锚, 市场预期差和资本市场情景判断 | 部分行情和一致预期需要付费库或登录, 公开检索无可靠结果 | 公司公告, 财报, IR, 交易所, 监管公告, 官方行业数据和可信数据库 |",
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
            "**研究含义:** " + "估值和盈利性需要按不同业务线加权, 不能只交易单一成长叙事." * 8,
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
            "**研究含义:** " + "估值和盈利性需要按不同业务线加权, 不能只交易单一成长叙事." * 8,
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
        "## 1. 目标公司/产品综合判断",
        long_body,
        "## 2. 研究边界",
        long_body,
        "### 2.1 研究计划摘要",
        sample_company_research_plan(capital=True),
        "### 2.2 来源矩阵和证据质量",
        source_matrix_body,
        "### 2.3 检索缺口闭环结果",
        retrieval_gap_body,
        "## 3. 宏观环境分析",
        macro_body,
        "## 4. 中观行业分析",
        meso_body,
        "### 4.0 多业务线中观拆分",
        multibusiness_body,
        "### 4.3 行业地图",
        mermaid_map_body,
        "### 4.4 生命周期判断",
        lifecycle_body,
        "## 5. 七个核心模块分析",
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
            "## 13. 风险, 机会和不确定性",
            long_body,
            "## 15. 方法论和数据来源说明",
            long_body,
            "## 16. 后续验证清单",
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
            "**证据:** " + "证据内容" * 60,
            "**机制:** " + "机制内容" * 60,
            "**研究含义:** " + "影响内容" * 60,
            "**关键指标和后续验证:** " + "指标验证" * 60,
        ]
    )
    long_body = "分析内容" * 260
    source_matrix_body = "\n".join(
        [
            "| 关键 Claim | 来源类型 | 本报告用途 | 证据层级 | 证据质量 | 来源状态 | 独立验证状态 | 限制和缺口处理 |",
            "|---|---|---|---|---|---|---|---|",
            "| 公司财务与经营 | 公司公告/财报/IR/交易所文件 | 核实公司和财务事实 | primary | high | obtained | single-source-primary | 标记缺口和下一步来源 |",
            "| 股价与估值 | 交易所/可信市场数据库 | 核实股价, 估值和市值 | near-primary | high | obtained | independently_verified | 行情口径限制已说明 |",
            "| 行业趋势与预测 | 可信数据库/行业报告 | 对比趋势和预测指标 | near-primary | medium | paid-database | single-source-primary | 预测假设仍需验证 |",
            "| 补充市场信号 | 媒体/访谈/专家观点 | 补充观点 | secondary | low | obtained | secondary-only | 必须交叉验证 |",
            long_body,
        ]
    )
    fact_inference_body = "\n".join(
        [
            "| 类型 | 内容 | 来源/依据 | 证据层级 | 证据质量 | 来源状态 | 置信度 |",
            "|---|---|---|---|---|---|---|",
            "| 事实 | 公司财务和运营事实 | 公司公告或财报 | primary | high | obtained | 高 |",
            "| 待核验事实 | 二手行情或媒体转述数据 | 市场数据库或媒体 | secondary | low | obtained | 中 |",
            "| 观点 | 分析师或媒体观点 | 来源立场 | secondary | medium | obtained | 中 |",
            "| 推断 | 估值和预期差判断 | 基于事实和观点 | near-primary | medium | obtained | 中 |",
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
        "## 1. 目标公司/产品综合判断",
        long_body,
        "## 2. 研究边界",
        long_body,
        "### 2.1 研究计划摘要",
        sample_company_research_plan(capital=True),
        "### 2.2 来源矩阵和证据质量",
        source_matrix_body,
        "### 2.3 检索缺口闭环结果",
        long_body,
        "## 3. 宏观环境分析",
        long_body,
        "## 4. 中观行业分析",
        long_body,
        "### 4.0 多业务线中观拆分",
        long_body,
        "### 4.3 行业地图",
        mermaid_map_body,
        "### 4.4 生命周期判断",
        lifecycle_body,
        "## 5. 七个核心模块分析",
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
            "## 13. 风险, 机会和不确定性",
            long_body,
            "## 15. 方法论和数据来源说明",
            long_body,
            "## 16. 后续验证清单",
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
            "**证据:** " + "证据内容" * 60,
            "**机制:** " + "机制内容" * 60,
            "**研究含义:** " + "影响内容" * 60,
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
            "| 关键 Claim | 来源类型 | 本报告用途 | 证据层级 | 证据质量 | 来源状态 | 独立验证状态 | 限制和缺口处理 |",
            "|---|---|---|---|---|---|---|---|",
            "| 公司财务与经营 | 公司公告/财报/IR/交易所文件 | 核实公司和财务事实 | primary | high | obtained | single-source-primary | 标记缺口和下一步来源 |",
            "| 股价与估值 | 交易所/可信市场数据库 | 核实股价, 估值和市值 | near-primary | high | obtained | independently_verified | 行情口径限制已说明 |",
            "| 行业趋势与预测 | 可信数据库/行业报告 | 对比趋势和预测指标 | near-primary | medium | paid-database | single-source-primary | 预测假设仍需验证 |",
            "| 补充市场信号 | 媒体/访谈/专家观点 | 补充观点 | secondary | low | obtained | secondary-only | 必须交叉验证 |",
            long_body,
        ]
    )
    fact_inference_body = "\n".join(
        [
            "| 类型 | 内容 | 来源/依据 | 证据层级 | 证据质量 | 来源状态 | 置信度 |",
            "|---|---|---|---|---|---|---|",
            "| 事实 | 公司财务和运营事实 | 公司公告或财报 | primary | high | obtained | 高 |",
            "| 待核验事实 | 二手行情或媒体转述数据 | 市场数据库或媒体 | secondary | low | obtained | 中 |",
            "| 观点 | 分析师或媒体观点 | 来源立场 | secondary | medium | obtained | 中 |",
            "| 推断 | 估值和预期差判断 | 基于事实和观点 | near-primary | medium | obtained | 中 |",
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
            "**研究含义:** " + "估值和盈利性需要按不同业务线加权, 不能只交易单一成长叙事." * 8,
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
            "review_mode: multi-agent. 四个核心角色独立审查同一工作草稿和研究工件.",
            "| 质疑 ID | 视角 | 目标 Claim/章节 | 重要性 | 核心质疑 | 裁决 | 证据/Gap | 报告改动 | 复核状态 |",
            "|---|---|---|---|---|---|---|---|---|",
            "| challenge-industry | 行业专家 | claim-market-size / 4.4 生命周期判断 | high | 价值链和生命周期判断可能过于乐观, 行业利润池未必向目标环节转移 | confirmed | gap-market-definition | 收窄生命周期结论并补充利润池限制 | closed |",
            "| challenge-investment | 投资研究员 | claim-market-size / 11.3 估值逻辑和市场预期差 | medium | 估值修复可能依赖过高盈利假设, 市场可能把短期订单当成长期利润 | refuted | source-example | 保留估值框架并补充复核依据 | closed |",
            "| challenge-policy | 政策/监管 | claim-market-size / 5.6 外部因素 | medium | 监管约束可能改变业务增长节奏, 安全合规事件可能提高风险折现 | out_of_scope | source-policy | 在研究边界中澄清监管排除项 | closed |",
            "| challenge-operator | 经营者/创业者 | claim-market-size / 6. 微观公司/产品分析 | medium | 执行难度可能高于战略叙事, 交付和售后能力可能成为瓶颈 | partially_valid | source-operator | 下调执行置信度并增加跟踪指标 | closed |",
        ]
    )
    risk_body = "\n\n".join(
        [
            "事实风险, 假设风险, 数据缺口, 上行机会和触发条件需要逐项记录并连接证据状态." * 12,
            "风险需要拆成行业结构风险和目标公司自身风险. 行业结构风险来自竞争强度, 价格战, 监管变化, 技术路线切换和上游成本周期, 这些因素会压缩行业利润池并提高估值折现率." * 12,
            "目标公司或目标产品风险来自产品质量, 交付能力, 渠道效率, 现金流承压, 品牌舆情和管理执行, 这些变量会影响七模块里的盈利性, 防守性和景气度判断." * 12,
            "机会也需要拆成行业机会和目标自身机会. 行业机会来自渗透率提升, 政策支持, 供给出清和技术成本下降, 目标公司机会来自品牌, 渠道, 生态协同, 产品组合和运营效率改善." * 12,
        ]
    )
    verification_body = "\n".join(
        [
            "| 待验证问题 | 当前证据状态 | 为什么重要 | 推荐来源 | 优先级 |",
            "|---|---|---|---|---|",
            "| 验证行业规模, 增速和渗透率是否仍支持增长假设 | 部分补齐 | 这些指标决定行业空间和生命周期判断是否成立 | 官方统计, 行业协会, 监管文件, 可信数据库 | 高 |",
            "| 验证目标公司收入, 利润, 现金流和运营指标是否支持估值逻辑 | 部分补齐 | 这些指标决定基本面变化和市场预期差是否真实 | 公司公告, 财报, 交易所文件, IR 材料 | 高 |",
            "| 验证目标产品质量, 交付, 投诉, 召回或合规风险 | 待验证 | 这些指标决定风险折现和品牌韧性 | 监管公告, 召回平台, 售后数据, 用户投诉数据库 | 高 |",
            "| 验证竞争对手价格, 产能, 渠道和新品节奏 | 待验证 | 这些信息决定行业结构风险和机会是否变化 | 同业公告, 行业数据库, 渠道调研, 媒体访谈 | 中 |",
        ]
    )
    retrieval_gap_body = "\n".join(
        [
            "| 缺口 | 已尝试轮次和来源 | 当前状态 | 为什么仍重要 | 未补齐原因 | 下一步来源 |",
            "|---|---|---|---|---|---|",
            "| 目标公司分业务线收入, 毛利率, 现金流, 订单交付, 股价区间和估值倍数的最新一手口径 | 第1轮: 公司公告, 财报和 IR 材料. 第2轮: 交易所文件, 交易所行情和可信市场数据库. 第3轮: 替代关键词, 本地语言和可信二手交叉验证 | 仍未补齐 | 这些缺口会影响基本面变化, 估值锚, 市场预期差和资本市场情景判断 | 部分行情和一致预期需要付费库或登录, 公开检索无可靠结果 | 公司公告, 财报, IR, 交易所, 监管公告, 官方行业数据和可信数据库 |",
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
        "## 1. 目标公司/产品综合判断",
        long_body,
        "## 2. 研究边界",
        long_body,
        "### 2.1 研究计划摘要",
        sample_company_research_plan(capital=True),
        "### 2.2 来源矩阵和证据质量",
        source_matrix_body,
        "### 2.3 检索缺口闭环结果",
        retrieval_gap_body,
        "## 3. 宏观环境分析",
        macro_body,
        "## 4. 中观行业分析",
        meso_body,
        "### 4.0 多业务线中观拆分",
        multibusiness_body,
        "### 4.1 行业一句话定义",
        "行业定义和研究口径需要与多业务拆分保持一致." * 40,
        "### 4.2 行业关键指标",
        "行业关键指标包括规模, 增速, 渗透率, 竞争强度, 盈利水平和景气度." * 40,
        "### 4.3 行业地图",
        mermaid_map_body,
        "### 4.4 生命周期判断",
        lifecycle_body,
        "## 5. 七个核心模块分析",
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
            "## 7. SWOT",
            "优势, 劣势, 机会和威胁需要连接行业结构, 目标能力和证据缺口." * 60,
            "## 9. 竞争对手对比",
            "竞争对手对比覆盖产品, 价格, 渠道, 盈利能力, 护城河和关键验证限制." * 60,
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
            "## 13. 风险, 机会和不确定性",
            risk_body,
            "## 14. 后续行动建议",
            "行动建议围绕产品, 渠道, 运营, 风险控制和里程碑展开, 与证据补齐任务分离." * 60,
            "## 15. 方法论和数据来源说明",
            long_body,
            "## 16. 后续验证清单",
            verification_body,
            "## 17. 报告合规自检表",
            "\n".join(
                [
                    "| 检查项 | 是否通过 | 说明 |",
                    "|---|---|---|",
                    "| 模板骨架完整 | 通过 | 已保留 0-17 主骨架和公司/产品报告必需章节 |",
                    "| 研究简报转译已完成 | 通过 | 已按 research brief 锁定路由, 来源计划和深度契约 |",
                    "| Deep Research 可见痕迹完整 | 通过 | 已展示研究计划, 来源矩阵和检索缺口闭环结果 |",
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
    return add_sample_trace_ids("\n\n".join(parts))


def sample_company_report() -> str:
    """
    构造不启用资本市场模块的公司报告样例.

    :return: Markdown 样例文本.
    """
    report = re.sub(
        r"(?ms)^## 11\. 资本市场表现与估值预期变化\s*.*?(?=^## 12\. 多视角压力测试)",
        "",
        sample_company_capital_pass(),
    )
    return report.replace("capital_market=enabled", "capital_market=disabled", 1)


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
        r"(?ms)(^## 12\. 多视角压力测试\s*\n\n).*?(?=\n\n## 13\. 风险, 机会和不确定性)",
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
        r"(?ms)(^## 6\. 微观公司/产品分析\s*\n\n).*?(?=\n\n## 7\. SWOT)",
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
        r"(?ms)(^## 13\. 风险, 机会和不确定性\s*\n\n).*?(?=\n\n## 15\. 方法论和数据来源说明)",
        r"\1太薄",
        text,
    )
    return re.sub(
        r"(?ms)(^## 16\. 后续验证清单\s*\n\n).*?(?=\n\n## 17\. 报告合规自检表)",
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
        r"(?ms)(^### 0\.4 图表清单或图表占位\s*\n\n).*?(?=\n\n## 1\. 目标公司/产品综合判断)",
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
            "**证据:** " + "证据内容" * 28,
            "**机制:** " + "机制内容" * 28,
            "**研究含义:** " + "影响内容" * 28,
        ]
    )
    priority_module_body = "\n\n".join(
        [
            "**结论:** " + "结论内容" * 46,
            "**证据:** " + "证据内容" * 46,
            "**机制:** " + "机制内容" * 46,
            "**研究含义:** " + "影响内容" * 46,
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
            "review_mode: single-agent-simulated. 以下角色视角由同一 Agent 分别执行, 不代表独立 Agent 审查.",
            "| 质疑 ID | 视角 | 目标 Claim/章节 | 重要性 | 核心质疑 | 裁决 | 证据/Gap | 报告改动 | 复核状态 |",
            "|---|---|---|---|---|---|---|---|---|",
            "| challenge-industry | 行业专家 | claim-market-size / 4.4 生命周期判断 | high | 行业结构和生命周期判断可能偏乐观 | confirmed | gap-market-definition | 收窄生命周期结论并补充边界 | closed |",
            "| challenge-investment | 投资研究员 | claim-market-size / 5.5 估值 | medium | 估值和现金流假设可能偏乐观 | refuted | source-example | 保留估值判断并补充复核依据 | closed |",
            "| challenge-policy | 政策/监管 | claim-market-size / 5.6 外部因素 | medium | 政策监管约束可能遗漏 | out_of_scope | source-policy | 在研究边界中澄清排除项 | closed |",
            "| challenge-operator | 经营者/创业者 | claim-market-size / 6. 微观公司/产品分析 | medium | 执行路径可能不现实 | partially_valid | source-operator | 下调执行置信度并增加跟踪指标 | closed |",
        ]
    )
    risk_body = "风险机会行业结构目标公司目标产品竞争监管成本品牌渠道现金流质量交付机会验证" * 8
    verification_body = "\n".join(
        [
            "| 待验证问题 | 当前证据状态 | 为什么重要 | 推荐来源 | 优先级 |",
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
        "## 1. 目标公司/产品综合判断",
        brief_body,
        "## 2. 研究边界",
        brief_body,
        "### 2.1 研究计划摘要",
        sample_company_research_plan(capital=True),
        "### 2.2 来源矩阵和证据质量",
        brief_body,
        "### 2.3 检索缺口闭环结果",
        brief_body,
        "## 3. 宏观环境分析",
        macro_body,
        "## 4. 中观行业分析",
        meso_body,
        "### 4.0 多业务线中观拆分",
        brief_body,
        "### 4.3 行业地图",
        mermaid_map_body,
        "### 4.4 生命周期判断",
        brief_body,
        "## 5. 七个核心模块分析",
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
            "## 13. 风险, 机会和不确定性",
            risk_body,
            "## 15. 方法论和数据来源说明",
            brief_body,
            "## 16. 后续验证清单",
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
        r"(?ms)(^### 2\.2 来源矩阵和证据质量\s*\n\n).*?(?=\n\n### 2\.3 检索缺口闭环结果)",
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
        r"(?ms)(^### 2\.2 来源矩阵和证据质量\s*\n\n).*?(?=\n\n### 2\.3 检索缺口闭环结果)",
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
        r"(?ms)(^## 7\. 事实, 观点和推断分层\s*\n\n).*?(?=\n\n## 8\. 多视角压力测试)",
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
        r"(?ms)(^## 7\. 证据链分析\s*\n\n).*?(?=\n\n## 8\. 生命周期判断)",
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
        r"(?ms)(^### 4\.4 生命周期判断\s*\n\n).*?(?=\n\n## 5\. 七个核心模块分析)",
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
        r"(?ms)(^### 4\.0 多业务线中观拆分\s*\n\n).*?(?=\n\n### 4\.1 行业一句话定义)",
        r"\1" + weak_body,
        text,
    )


def sample_company_capital_weak_retrieval_gap() -> str:
    """
    构造检索缺口闭环结果缺少可执行验证信息的资本市场报告样例.

    :return: Markdown 样例文本.
    """
    text = sample_company_capital_pass()
    return re.sub(
        r"(?ms)(^### 2\.3 检索缺口闭环结果\s*\n\n).*?(?=\n\n## 3\. 宏观环境分析)",
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
            "**证据:** " + "证据内容" * 70,
            "**机制:** " + "机制内容" * 70,
            "**研究含义:** " + "影响内容" * 70,
        ]
    )
    return re.sub(
        r"(?ms)(^### 5\.1 可行性\s*\n\n).*?(?=\n\n### 5\.2 规模性)",
        r"\1" + weak_body,
        text,
    )


def sample_overview_weak_retrieval_gap() -> str:
    """
    构造检索缺口闭环结果缺少可执行验证信息的行业全览报告样例.

    :return: Markdown 样例文本.
    """
    text = sample_overview_report(20)
    return re.sub(
        r"(?ms)(^### 2\.3 检索缺口闭环结果\s*\n\n).*?(?=\n\n## 3\. 行业地图)",
        r"\1后续继续关注相关信息." + "说明内容" * 80,
        text,
    )


def sample_specific_weak_retrieval_gap() -> str:
    """
    构造检索缺口闭环结果缺少可执行验证信息的行业具体问题报告样例.

    :return: Markdown 样例文本.
    """
    text = sample_specific_report(20)
    return re.sub(
        r"(?ms)(^### 3\.3 检索缺口闭环结果\s*\n\n).*?(?=\n\n## 4\. 行业一句话定义)",
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
        r"(?ms)(^## 4\. 生命周期判断\s*\n\n).*?(?=\n\n## 5\. 七个核心模块分析)",
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
        r"(?ms)(^## 8\. 生命周期判断\s*\n\n).*?(?=\n\n## 9\. 七个核心模块分析)",
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
        "Research Implication: decision makers should track the stated indicators and verify gaps "
        "against a Primary Source before changing the conclusion."
    )
    module_body = "\n\n".join(
        [
            "**Conclusion:** " + analysis,
            "**Evidence:** " + analysis,
            "**Mechanism:** " + analysis,
            "**Research Implication:** " + " ".join([analysis] * 13),
            "**Key Metrics and Follow-up Verification:** " + analysis,
        ]
    )
    direct_answer = "\n\n".join([analysis] * 4)
    return add_sample_trace_ids("\n\n".join(
        [
            "# Example Industry Question Research Report",
            "## 1. Direct Answer\n\n" + direct_answer,
            "## 2. Conclusion Summary\n\n" + analysis,
            "## 3. Research Scope\n\nGlobal market, 2024-2026, with explicit inclusions, exclusions, and assumptions.",
            "### 3.1 Research Plan Summary\n\n" + analysis,
            "### 3.2 Source Matrix and Evidence Quality\n\n"
            "| Key Claim | Source Type | Use in This Report | Evidence Tier | Evidence Quality | Source Status | Independent Verification Status | Limitations and Gap Handling |\n"
            "|---|---|---|---|---|---|---|---|\n"
            "| Market demand | Official Source | Market Size and Policy | primary | high | obtained | independently_verified | none |",
            "### 3.3 Retrieval Gap Closure Results\n\n"
            "Missing Evidence remains important because it may change the conclusion. Attempted Rounds and Sources "
            "included Round 1 with a Primary Source, Round 2 with a Near-Primary Source, and Round 3 with an "
            "Industry Association and Credible Database. Attempted Sources are recorded. Current Status is "
            "Partially Closed. Unresolved Reason is Paid Database and Definition Mismatch. Next Source is an "
            "Official Source for Verification.\n\n"
            "| Gap | Attempted Rounds and Sources | Current Status | Why It Still Matters | Unresolved Reason | Next Source |\n"
            "|---|---|---|---|---|---|\n"
            "| Missing Evidence | Round 1, Round 2, Round 3 | Partially Closed | Evidence may change the result | Paid Database | Primary Source |",
            "## 4. One-Sentence Industry Definition\n\nThe industry boundary covers the defined value chain and excludes adjacent substitutes unless stated.",
            "## 5. Industry Map\n\n```mermaid\nflowchart LR\nA[Supply] --> B[Market]\nB --> C[Demand]\n```",
            "## 6. Problem Decomposition and Issue Tree\n\n" + analysis,
            "## 7. Evidence Chain Analysis\n\n"
            "| Sub-question | Conclusion | Fact | Opinion | Inference | Source/Basis | Evidence Tier | Evidence Quality | Source Status | Confidence |\n"
            "|---|---|---|---|---|---|---|---|---|---|\n"
            "| Demand | Conditional growth | Fact | Opinion | Inference | Official Source | primary | high | obtained | high |",
            "## 8. Lifecycle Assessment\n\n"
            "**Lifecycle Phase:** Growth Phase. " + analysis + "\n\n"
            "**Evidence:** Evidence supports expansion. " + analysis + "\n\n"
            "**Counterevidence:** Uneven adoption challenges the base case. " + analysis + "\n\n"
            "**Confidence:** Medium. " + analysis + "\n\n"
            "**Research Implication:** Timing, segment selection, and verification matter. " + analysis,
            "## 9. Seven Core Modules Analysis",
            "### 9.1 Feasibility\n\n" + module_body,
            "### 9.2 Scalability\n\n" + module_body,
            "### 9.3 Defensibility\n\n" + module_body,
            "### 9.4 Profitability\n\n" + module_body,
            "### 9.5 Valuation\n\n" + module_body,
            "### 9.6 External Factors\n\n" + module_body,
            "### 9.7 Prosperity\n\n" + module_body,
            "## 10. Multi-Perspective Pressure Test\n\n"
            "review_mode: single-agent-simulated. These role perspectives were simulated by one Agent and are not independent Agent reviews.\n\n"
            "| Challenge ID | Perspective | Target Claim/Section | Materiality | Core Challenge | Resolution | Evidence/Gap | Report Change | Reviewer Status |\n"
            "|---|---|---|---|---|---|---|---|---|\n"
            "| challenge-industry | Industry Expert | claim-market-size / 8. Lifecycle Assessment | high | Industry structure may differ | confirmed | gap-market-definition | Narrowed the lifecycle conclusion and disclosed the limitation | closed |\n"
            "| challenge-investment | Investment Researcher | claim-market-size / 9.5 Valuation | medium | Profitability may be weaker | refuted | source-example | Retained the conclusion and added review grounds | closed |\n"
            "| challenge-policy | Policy/Regulatory | claim-market-size / 9.6 External Factors | medium | Policy may tighten | out_of_scope | source-policy | Clarified the exclusion in the research scope | closed |\n"
            "| challenge-operator | Operator/Entrepreneur | claim-market-size / 9.1 Feasibility | medium | Execution may be harder | partially_valid | source-operator | Downgraded confidence and added operating conditions | closed |",
            "## 11. Risks, Opportunities, and Uncertainties\n\nFact Risk, Assumption Risk, Data Gap, Upside Opportunity, and Trigger Condition are assessed separately. " + analysis,
            "## 12. Follow-up Verification Checklist\n\n"
            "| Verification Item | Current Evidence Status | Why It Matters | Recommended Source | Priority |\n"
            "|---|---|---|---|---|\n"
            "| Demand evidence | Partially Closed | Changes the conclusion | Official Source | High |",
            "## 13. Report Compliance Checklist\n\n"
            "| Check | Passed | Explanation |\n"
            "|---|---|---|\n"
            "| Report structure | Yes | The report preserves the required structure, Evidence rules, and Verification gaps. |",
            "This report is for research and informational purposes only. It does not constitute investment advice or any guarantee of returns.",
        ]
    ))


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
            "关键 Claim": "Key Claim",
            "证据质量": "Evidence Quality",
            "独立验证状态": "Independent Verification Status",
            "限制和缺口处理": "Limitations and Gap Handling",
            "当前证据状态": "Current Evidence Status",
            "来源状态": "Source Status",
            "研究含义": "Research Implication",
            "已尝试轮次和来源": "Attempted Rounds and Sources",
            "对目标公司的含义": "Implication for the Target Company",
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


def add_sample_trace_ids(text: str) -> str:
    """
    为规范样例的来源矩阵和缺口表添加稳定追踪 ID.

    :param text: Markdown 样例文本.
    :return: 带规范 `claim_id` 和 `gap_id` 的样例文本.
    """
    lines = text.splitlines()
    mode = ""
    claim_number = 0
    gap_number = 0
    for index, line in enumerate(lines):
        cells = parse_markdown_table_cells(line)
        if cells and cells[0] in {"关键 Claim", "Key Claim"}:
            mode = "claim"
            continue
        if cells and cells[0] in {"缺口", "Gap"}:
            mode = "gap"
            continue
        if not cells:
            mode = ""
            continue
        if is_markdown_separator_row(cells):
            continue
        if mode == "claim" and not extract_trace_id(cells[0], "claim"):
            claim_number += 1
            cells[0] = f"`claim-sample-{claim_number}`: {cells[0]}"
            lines[index] = "| " + " | ".join(cells) + " |"
        elif mode == "gap" and not extract_trace_id(cells[0], "gap"):
            gap_number += 1
            cells[0] = f"`gap-sample-{gap_number}`: {cells[0]}"
            lines[index] = "| " + " | ".join(cells) + " |"
    return "\n".join(lines)


def write_v63_fixtures(root: Path) -> None:
    """
    写入 v63 中英文规范正例和定向负例.

    :param root: 测试样例根目录.
    :return: None.
    """
    valid_root = root / "valid"
    invalid_root = root / "invalid"
    valid_root.mkdir(parents=True, exist_ok=True)
    invalid_root.mkdir(parents=True, exist_ok=True)
    valid_reports = {
        "overview-zh.md": add_sample_trace_ids(sample_overview_report(20)),
        "overview-en.md": add_sample_trace_ids(
            englishize_contract_fixture(sample_overview_report(20))
        ),
        "specific-zh.md": add_sample_trace_ids(sample_specific_report(20)),
        "specific-en.md": add_sample_trace_ids(sample_english_specific_report()),
        "company-zh.md": add_sample_trace_ids(sample_company_report()),
        "company-en.md": add_sample_trace_ids(
            englishize_contract_fixture(sample_company_report())
        ),
        "company-capital-zh.md": add_sample_trace_ids(sample_company_capital_pass()),
        "company-capital-en.md": add_sample_trace_ids(
            englishize_contract_fixture(sample_company_capital_pass())
        ),
    }
    for name, report in valid_reports.items():
        (valid_root / name).write_text(report, encoding="utf-8")

    overview = valid_reports["overview-zh.md"]
    specific = valid_reports["specific-zh.md"]
    company = valid_reports["company-zh.md"]
    company_capital = valid_reports["company-capital-zh.md"]
    invalid_reports = {
        "overview-missing-lifecycle.md": overview.replace("## 4. 生命周期判断", "## 4. 阶段说明", 1),
        "specific-missing-evidence-chain.md": re.sub(
            r"(?ms)^## 7\. 证据链分析\s*.*?(?=^## 8\. 生命周期判断)", "", specific
        ),
        "company-missing-industry-map.md": re.sub(
            r"(?ms)^### 4\.3 行业地图\s*.*?(?=^### 4\.4 生命周期判断)", "", company
        ),
        "company-capital-missing-capital-section.md": company,
        "overview-legacy-heading.md": overview.replace(
            "### 2.3 检索缺口闭环结果", "### 2.3 二次检索缺口", 1
        ),
        "overview-missing-module-verification.md": overview.replace(
            "**关键指标和后续验证:**", "**后续观察:**", 1
        ),
        "overview-conflated-source-fields.md": overview.replace(
            "| 关键 Claim | 来源类型 | 本报告用途 | 证据层级 | 证据质量 | 来源状态 | 独立验证状态 | 限制和缺口处理 |",
            "| 来源类型 | 本报告用途 | 证据等级 | 检索状态 | 限制 |",
            1,
        ),
        "overview-noncanonical-evidence-tier.md": overview.replace(
            "| primary | high | obtained |",
            "| primary/near-primary | high | obtained |",
            1,
        ),
        "overview-invalid-source-row-width.md": overview.replace(
            "| `claim-sample-1`: 市场规模与供需 | 官方统计/监管/行业协会 | 核实市场, 政策, 供需和价格 | primary | high | obtained | independently_verified | 口径和时效限制已说明 |",
            "| `claim-sample-1`: 市场规模与供需 | 官方统计/监管/行业协会 | primary | high | obtained |",
            1,
        ),
        "overview-missing-claim-id.md": overview.replace(
            "`claim-sample-1`: ",
            "",
            1,
        ),
        "overview-missing-gap-id.md": overview.replace(
            "`gap-sample-1`: ",
            "",
            1,
        ),
        "overview-risk-missing-opportunity.md": overview.replace(
            "事实风险, 假设风险, 数据缺口, 上行机会和触发条件",
            "风险因素和不确定性",
        ),
        "overview-verification-missing-status.md": overview.replace(
            "| 待验证问题 | 当前证据状态 | 为什么重要 | 推荐来源 | 优先级 |",
            "| 待验证问题 | 为什么重要 | 推荐来源 | 优先级 |",
            1,
        ),
        "company-unexpected-capital-module.md": company_capital,
        "company-empty-portfolio-module.md": company.replace(
            "## 9. 竞争对手对比", "## 8. 业务/产品组合分析\n\n不适用.\n\n## 9. 竞争对手对比", 1
        ),
        "company-missing-conditional-declaration.md": re.sub(
            r"(?m)^\| 条件模块 \|.*\|\s*$",
            "",
            company,
        ),
        "company-multibusiness-declaration-conflict.md": company.replace(
            "multi_business_split=enabled",
            "multi_business_split=disabled",
            1,
        ),
        "overview-company-opening.md": overview.replace(
            "## 1. 行业一句话定义", "## 0. 研报前置区", 1
        ),
        "specific-overview-opening.md": specific.replace(
            "## 1. 直接回答", "## 1. 行业一句话定义\n\n错误 opening.\n\n## 1. 直接回答", 1
        ),
        "company-capital-missing-multibusiness.md": re.sub(
            r"(?ms)^### 4\.0 多业务线中观拆分\s*.*?(?=^### 4\.1 行业一句话定义)",
            "",
            company_capital,
        ),
        "company-map-missing-target-position.md": re.sub(
            r"(?ms)(^### 4\.3 行业地图\s*.*?)(?=^### 4\.4 生命周期判断)",
            lambda match: match.group(1)
            .replace("目标公司/产品", "研究对象")
            .replace("目标公司", "研究对象")
            .replace("目标产品", "研究对象")
            .replace("目标位置", "对象关系")
            .replace("研究对象位置", "对象关系"),
            company,
        ),
    }
    expectations = {
        "overview-missing-lifecycle.md": {"profile": "overview", "error_contains": "missing heading: ## 4. 生命周期判断"},
        "specific-missing-evidence-chain.md": {"profile": "specific", "error_contains": "missing heading: ## 7. 证据链分析"},
        "company-missing-industry-map.md": {"profile": "company", "error_contains": "missing heading: ### 4.3 行业地图"},
        "company-capital-missing-capital-section.md": {"profile": "company-capital", "error_contains": "missing heading: ## 11. 资本市场表现与估值预期变化"},
        "overview-legacy-heading.md": {"profile": "overview", "error_contains": "legacy report structure is not accepted"},
        "overview-missing-module-verification.md": {"profile": "overview", "error_contains": "noncanonical contract labels"},
        "overview-conflated-source-fields.md": {"profile": "overview", "error_contains": "noncanonical contract header"},
        "overview-noncanonical-evidence-tier.md": {"profile": "overview", "error_contains": "noncanonical evidence tier"},
        "overview-invalid-source-row-width.md": {"profile": "overview", "error_contains": "noncanonical table row width"},
        "overview-missing-claim-id.md": {"profile": "overview", "error_contains": "source matrix row 1: missing unique claim_id"},
        "overview-missing-gap-id.md": {"profile": "overview", "error_contains": "retrieval gap row 1: missing unique gap_id"},
        "overview-risk-missing-opportunity.md": {"profile": "overview", "error_contains": "missing checklist concept under ## 9. 风险, 机会和不确定性: 事实风险"},
        "overview-verification-missing-status.md": {"profile": "overview", "error_contains": "noncanonical contract header"},
        "company-unexpected-capital-module.md": {"profile": "company", "error_contains": "unexpected conditional module"},
        "company-empty-portfolio-module.md": {"profile": "company", "error_contains": "thin section: ## 8. 业务/产品组合分析"},
        "company-missing-conditional-declaration.md": {"profile": "company", "error_contains": "missing or invalid conditional module declaration"},
        "company-multibusiness-declaration-conflict.md": {"profile": "company", "error_contains": "conditional module declaration conflicts with rendered section: multi_business_split"},
        "overview-company-opening.md": {"profile": "overview", "error_contains": "wrong route opening after H1"},
        "specific-overview-opening.md": {"profile": "specific", "error_contains": "wrong route opening after H1"},
        "company-capital-missing-multibusiness.md": {"profile": "company-capital", "error_contains": "missing heading: ### 4.0 多业务线中观拆分"},
        "company-map-missing-target-position.md": {"profile": "company", "error_contains": "missing checklist concept under ### 4.3 行业地图"},
    }
    for name, report in invalid_reports.items():
        (invalid_root / name).write_text(report, encoding="utf-8")
    (invalid_root / "expected-errors.json").write_text(
        json.dumps(expectations, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def validate_v63_fixture_directory(root: Path) -> list[str]:
    """
    校验 v63 测试样例目录的显式路由, 自动路由和定向错误.

    :param root: 测试样例根目录.
    :return: 测试样例失败列表.
    """
    failures: list[str] = []
    for path in sorted((root / "valid").glob("*.md")):
        profile = path.stem.rsplit("-", 1)[0]
        report = read_text(path)
        explicit_errors = run_profile(report, profile)
        auto_errors = run_profile(report, "auto")
        if explicit_errors:
            failures.append(f"{path.name} explicit profile failed: {explicit_errors[0]}")
        if auto_errors:
            failures.append(f"{path.name} auto profile failed: {auto_errors[0]}")
        if explicit_errors != auto_errors:
            failures.append(f"{path.name} explicit and auto results differ")
    expectations = json.loads(read_text(root / "invalid" / "expected-errors.json"))
    for name, expectation in expectations.items():
        errors = run_profile(read_text(root / "invalid" / name), expectation["profile"])
        if not errors:
            failures.append(f"{name} unexpectedly passed")
        elif not any(expectation["error_contains"] in error for error in errors):
            failures.append(f"{name} missing expected error: {expectation['error_contains']}")
    return failures


def find_v63_fixture_root() -> Path | None:
    """
    查找仓库级 v63 测试样例目录.

    :return: 仓库级测试样例目录, 独立安装环境未找到时返回 None.
    """
    script_path = Path(__file__).resolve()
    for parent in script_path.parents:
        candidate = parent / "tests" / "fixtures" / "v63"
        if candidate.exists():
            return candidate
    return None


def run_reader_view_self_test() -> list[str]:
    """
    运行报告读者视图与研究运行工件一致性自检.

    :return: 自检失败列表.
    """
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as temporary:
        repo_root = Path(temporary)
        run_id = "reader-view-v63-test"
        report_path = repo_root / "reports" / f"{run_id}.md"
        run_dir = repo_root / "research_runs" / run_id
        report_path.parent.mkdir(parents=True)
        run_dir.mkdir(parents=True)
        report = sample_overview_report(20)
        report = re.sub(
            r"(?ms)(^### 2\.2 来源矩阵和证据质量\s*\n\n).*?(?=\n\n### 2\.3 检索缺口闭环结果)",
            r"\1| 关键 Claim | 来源类型 | 本报告用途 | 证据层级 | 证据质量 | 来源状态 | 独立验证状态 | 限制和缺口处理 |\n|---|---|---|---|---|---|---|---|\n| `claim-market-size`: 市场规模 | 官方统计 | 判断规模 | primary | high | obtained | independently_verified | 无 |",
            report,
        )
        report = re.sub(
            r"(?ms)(^### 2\.3 检索缺口闭环结果\s*\n\n).*?(?=\n\n## 3\. 行业地图)",
            r"\1| 缺口 | 已尝试轮次和来源 | 当前状态 | 为什么仍重要 | 未补齐原因 | 下一步来源 |\n|---|---|---|---|---|---|\n| `gap-market-definition`: 市场定义 | initial 官方统计 | open | 影响规模结论 | 公开口径不一致 | 官方统计原表 |",
            report,
        )
        report_path.write_text(report, encoding="utf-8")
        manifest = {
            "run_id": run_id,
            "status": "completed",
            "engine_report_permission": True,
            "report_path": f"reports/{run_id}.md",
            "report_status": "generated",
        }
        (run_dir / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
        )
        (run_dir / "plan.json").write_text(
            json.dumps(
                {
                    "claims": [
                        {"claim_id": "claim-market-size"},
                        {"claim_id": "claim-other"},
                    ]
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        (run_dir / "evidence.jsonl").write_text(
            "\n".join(
                [
                    json.dumps(
                        {
                            "claim_id": "claim-market-size",
                            "access_status": "obtained",
                            "evidence_tier": "primary",
                            "independence_status": "independently_verified",
                        },
                        ensure_ascii=False,
                    ),
                    json.dumps(
                        {
                            "claim_id": "claim-other",
                            "access_status": "blocked",
                            "evidence_tier": "secondary",
                            "independence_status": "single-source-primary",
                        },
                        ensure_ascii=False,
                    ),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        (run_dir / "gaps.json").write_text(
            json.dumps(
                {
                    "gaps": [
                        {
                            "gap_id": "gap-market-definition",
                            "status": "open",
                            "unresolved_reason": "公开口径不一致",
                            "next_source_route": "官方统计原表",
                        }
                    ]
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        challenge_rows = [
            {
                "challenge_id": "challenge-industry",
                "reviewer_role": "industry-expert",
                "target_claim_id": "claim-market-size",
                "target_section": "4. 生命周期判断",
                "materiality": "high",
                "challenge": "行业判断可能过于乐观",
                "resolution": "confirmed",
                "gap_id": "gap-market-definition",
                "evidence_refs": [],
                "report_change": "收窄生命周期结论并披露定义限制",
                "reviewer_status": "closed",
            },
            {
                "challenge_id": "challenge-investment",
                "reviewer_role": "investment-researcher",
                "target_claim_id": "claim-market-size",
                "target_section": "5.4 盈利性",
                "materiality": "medium",
                "challenge": "盈利假设可能高估",
                "resolution": "refuted",
                "gap_id": None,
                "evidence_refs": [{"source_id": "source-example"}],
                "report_change": "保留原结论并补充复核依据",
                "reviewer_status": "closed",
            },
            {
                "challenge_id": "challenge-policy",
                "reviewer_role": "policy-regulatory",
                "target_claim_id": "claim-market-size",
                "target_section": "5.6 外部因素",
                "materiality": "medium",
                "challenge": "监管边界可能遗漏",
                "resolution": "out_of_scope",
                "gap_id": None,
                "evidence_refs": [{"source_id": "source-policy"}],
                "report_change": "在研究边界中明确排除项",
                "reviewer_status": "closed",
            },
            {
                "challenge_id": "challenge-operator",
                "reviewer_role": "operator-entrepreneur",
                "target_claim_id": "claim-market-size",
                "target_section": "5.1 可行性",
                "materiality": "medium",
                "challenge": "执行难度可能被低估",
                "resolution": "partially_valid",
                "gap_id": None,
                "evidence_refs": [{"source_id": "source-operator"}],
                "report_change": "下调执行置信度并增加条件",
                "reviewer_status": "closed",
            },
        ]
        (run_dir / "challenges.json").write_text(
            json.dumps(
                {
                    "schema_version": "v65",
                    "run_id": run_id,
                    "review_mode": "single-agent-simulated",
                    "challenges": challenge_rows,
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        valid_errors = validate_reader_view_consistency(
            report_path, report, "overview", "zh", run_dir, repo_root
        )
        if valid_errors:
            failures.append(f"reader_view_valid: {valid_errors[0]}")

        mismatch_report = report.replace(
            "| obtained | independently_verified |",
            "| blocked | single-source-primary |",
            1,
        )
        mismatch_errors = validate_reader_view_consistency(
            report_path, mismatch_report, "overview", "zh", run_dir, repo_root
        )
        if not any("not supported for claim-market-size" in error for error in mismatch_errors):
            failures.append("reader_view_access_mismatch")

        missing_claim_id_errors = validate_reader_view_consistency(
            report_path,
            report.replace("`claim-market-size`: ", "", 1),
            "overview",
            "zh",
            run_dir,
            repo_root,
        )
        if not any("missing unique claim_id" in error for error in missing_claim_id_errors):
            failures.append("reader_view_missing_claim_id")

        gap_mismatch_errors = validate_reader_view_consistency(
            report_path,
            report.replace("公开口径不一致", "错误原因", 1),
            "overview",
            "zh",
            run_dir,
            repo_root,
        )
        if not any("unresolved reason does not match" in error for error in gap_mismatch_errors):
            failures.append("reader_view_gap_identity_mismatch")

        challenge_mismatch_errors = validate_reader_view_consistency(
            report_path,
            report.replace("| confirmed | gap-market-definition |", "| refuted | gap-market-definition |", 1),
            "overview",
            "zh",
            run_dir,
            repo_root,
        )
        if not any("resolution does not match challenge-industry" in error for error in challenge_mismatch_errors):
            failures.append("reader_view_challenge_resolution_mismatch")

        fabricated_errors = validate_reader_view_consistency(
            report_path,
            report.replace("challenge-industry", "challenge-fabricated", 1),
            "overview",
            "zh",
            run_dir,
            repo_root,
        )
        if not any("not found in challenges.json" in error for error in fabricated_errors):
            failures.append("reader_view_fabricated_challenge_id")

        report_change_errors = validate_reader_view_consistency(
            report_path,
            report.replace("收窄生命周期结论并披露定义限制", "未执行约定改写", 1),
            "overview",
            "zh",
            run_dir,
            repo_root,
        )
        if not any("report_change does not match challenge-industry" in error for error in report_change_errors):
            failures.append("reader_view_challenge_report_change_mismatch")

        missing_required_report = re.sub(
            r"(?m)^\| challenge-industry \|.*\n",
            "",
            report,
            count=1,
        )
        missing_required_errors = validate_reader_view_consistency(
            report_path,
            missing_required_report,
            "overview",
            "zh",
            run_dir,
            repo_root,
        )
        if not any("required Challenge rows missing" in error for error in missing_required_errors):
            failures.append("reader_view_missing_required_challenge")

        barrier_report = report.replace(
            "| obtained | independently_verified |",
            "| login-required | single-source-primary |",
            1,
        )
        (run_dir / "evidence.jsonl").write_text(
            json.dumps(
                {
                    "claim_id": "claim-market-size",
                    "access_status": "login-required",
                    "evidence_tier": "primary",
                    "independence_status": "single-source-primary",
                },
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        barrier_errors = validate_reader_view_consistency(
            report_path, barrier_report, "overview", "zh", run_dir, repo_root
        )
        if barrier_errors:
            failures.append(f"reader_view_access_barrier: {barrier_errors[0]}")

        incomplete_manifest = dict(
            manifest,
            status="incomplete",
            engine_report_permission=False,
        )
        (run_dir / "manifest.json").write_text(
            json.dumps(incomplete_manifest, ensure_ascii=False), encoding="utf-8"
        )
        incomplete_errors = validate_reader_view_consistency(
            report_path, barrier_report, "overview", "zh", run_dir, repo_root
        )
        if not any("completed Run and Engine permission" in error for error in incomplete_errors):
            failures.append("reader_view_incomplete_run")

        association_manifest = dict(manifest, report_path="reports/different.md")
        (run_dir / "manifest.json").write_text(
            json.dumps(association_manifest, ensure_ascii=False), encoding="utf-8"
        )
        association_errors = validate_reader_view_consistency(
            report_path, barrier_report, "overview", "zh", run_dir, repo_root
        )
        if not any("manifest report_path mismatch" in error for error in association_errors):
            failures.append("reader_view_report_association")
    return failures


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
                    "结构要求: 包含 0. 研报前置区, 2.1 研究计划摘要, 2.2 来源矩阵和证据质量, 2.3 检索缺口闭环结果, 5.1-5.7, 6. 微观公司/产品分析, 11.1, 11.2, 11.3, 11.4, 12. 多视角压力测试, 17. 报告合规自检表.",
                    "必需章节: 0. 研报前置区, 研究计划摘要, 来源矩阵, 检索缺口闭环结果, 事实/观点/推断, 压力测试, 报告合规自检表.",
                    "深度要求: 目标字数 12000-18000 中文字符, 七模块 5.1 到 5.7 独立展开, 不压缩成表格.",
                    "证据要求: 一手来源优先, 重要数字标注来源或进入检索缺口闭环结果.",
                    "合规要求: 不构成投资建议.",
                    "维护验证命令: 先从已加载的 SKILL.md 解析 <skill-root>; python -B <skill-root>/scripts/report_contract_check.py <report.md> --profile company-capital --language auto --run-dir <research-run-directory> --repo-root .; python -B <skill-root>/scripts/deep_search_contract_check.py <research-run-directory> --repo-root .",
                    "输出前重写触发器: 缺少模板, 11.1-11.4, 来源矩阵, 检索缺口闭环结果或报告合规自检表时必须重写.",
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
                    "结构要求: 包含 0. 研报前置区, 2.1 研究计划摘要, 2.2 来源矩阵和证据质量, 2.3 检索缺口闭环结果, 5.1-5.7, 6. 微观公司/产品分析, 11.1, 11.2, 11.3, 11.4, 12. 多视角压力测试, 17. 报告合规自检表.",
                    "必需章节: 0. 研报前置区, 研究计划摘要, 来源矩阵, 检索缺口闭环结果, 事实/观点/推断, 压力测试, 报告合规自检表.",
                    "深度要求: 目标字数 12000-18000 中文字符, 七模块 5.1 到 5.7 独立展开, 不压缩成表格.",
                    "证据要求: 一手来源优先, 重要数字标注来源或进入检索缺口闭环结果.",
                    "合规要求: 不构成投资建议.",
                    "维护验证命令: 先从已加载的 SKILL.md 解析 <skill-root>; python -B <skill-root>/scripts/report_contract_check.py <report.md> --profile company-capital --language auto --run-dir <research-run-directory> --repo-root .; python -B <skill-root>/scripts/deep_search_contract_check.py <research-run-directory> --repo-root .",
                    "输出前重写触发器: 缺少模板, 11.1-11.4, 来源矩阵, 检索缺口闭环结果或报告合规自检表时必须重写.",
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
                    "Structure Requirements: include 0. Research Front Matter, 2.1 Research Plan Summary, 2.2 Source Matrix, 2.3 Retrieval Gap Closure Results, 5.1-5.7, 6. Micro Company/Product Analysis, 11.1, 11.2, 11.3, 11.4, 12. Multi-Perspective Pressure Test, and 17. Report Compliance Checklist.",
                    "Required Sections: Research Plan Summary, Source Matrix, Retrieval Gap Closure Results, Fact/Opinion/Inference, Pressure Test, and Report Compliance Checklist.",
                    "Depth Requirements: Target Length is the standard range and seven modules remain independent.",
                    "Evidence Requirements: Primary-Source-First and place unsupported figures in Retrieval Gap Closure Results.",
                    "Compliance Requirements: Not Investment Advice.",
                    "Maintenance commands: resolve <skill-root> from the loaded SKILL.md; python -B <skill-root>/scripts/report_contract_check.py <report.md> --profile company-capital --language auto --run-dir <research-run-directory> --repo-root .; python -B <skill-root>/scripts/deep_search_contract_check.py <research-run-directory> --repo-root .",
                    "Rewrite before output when the template, 11.1-11.4, Source Matrix, Retrieval Gap Closure Results, or Report Compliance Checklist is missing.",
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
                "### 9.7 Prosperity",
                "### 9.7 景气度",
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
            "overview_noncanonical_evidence_tier_fail",
            "overview",
            sample_overview_report(20).replace(
                "| primary | high | obtained |",
                "| primary/near-primary | high | obtained |",
                1,
            ),
            True,
        ),
        (
            "overview_noncanonical_source_status_fail",
            "overview",
            sample_overview_report(20).replace(
                "| primary | high | obtained |",
                "| primary | high | partially-obtained |",
                1,
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
            sample_english_specific_report().replace("Attempted Rounds and Sources", "Rounds"),
            True,
        ),
        (
            "company_capital_fail",
            "company-capital",
            "## 1. 目标公司/产品综合判断\n\n这是一个不完整报告.",
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
            sample_overview_report(1)
            .replace("结论内容" * 25, "短")
            .replace("证据内容" * 25, "短")
            .replace("机制内容" * 25, "短")
            .replace("研究含义" * 25, "短")
            .replace("跟踪指标和一手来源验证" * 25, "短"),
            True,
        ),
        (
            "specific_total_length_fail",
            "specific",
            sample_specific_report(1)
            .replace("结论内容" * 20, "短")
            .replace("证据内容" * 20, "短")
            .replace("机制内容" * 20, "短")
            .replace("问题含义" * 20, "短")
            .replace("跟踪指标和一手来源验证" * 20, "短"),
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
        "data gap": "数据缺口",
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

    with tempfile.TemporaryDirectory() as temporary:
        generated_fixture_root = Path(temporary) / "v63"
        write_v63_fixtures(generated_fixture_root)
        failures.extend(validate_v63_fixture_directory(generated_fixture_root))
    failures.extend(run_reader_view_self_test())

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
    parser.add_argument(
        "--write-v63-fixtures",
        type=Path,
        help="Write canonical v63 fixtures to the given directory.",
    )
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
    parser.add_argument(
        "--run-dir",
        type=Path,
        help="Optional Research Run directory for reader-view consistency checks.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root used with --run-dir.",
    )
    return parser


def main() -> int:
    """
    执行命令行入口.

    :return: 退出码, 0 表示通过, 1 表示失败.
    """
    parser = build_parser()
    args = parser.parse_args()
    if args.write_v63_fixtures:
        write_v63_fixtures(args.write_v63_fixtures)
        print(f"WROTE {args.write_v63_fixtures}")
        return 0
    if args.self_test:
        return run_self_test(json_output=args.json)
    if not args.report or not args.profile:
        parser.error("report and --profile are required unless --self-test is used")
    text = read_text(args.report)
    errors = run_profile(text, args.profile, language=args.language)
    if args.run_dir:
        resolved_language = detect_report_language(text) if args.language == "auto" else args.language
        normalized_text = normalize_report_contract(text, resolved_language)
        resolved_profile = detect_profile(normalized_text) if args.profile == "auto" else args.profile
        if resolved_profile not in {"overview", "specific", "company", "company-capital"}:
            errors.append("--run-dir is supported only for formal report profiles")
        else:
            errors.extend(
                validate_reader_view_consistency(
                    args.report,
                    text,
                    resolved_profile,
                    resolved_language,
                    args.run_dir,
                    args.repo_root,
                )
            )
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
