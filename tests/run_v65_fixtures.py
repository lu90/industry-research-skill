#!/usr/bin/env python3
"""
运行 v65 Pressure Test 正反向 fixtures.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = ROOT / "skills" / "industry-research" / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

import deep_search_contract_check as deep_check
import report_contract_check as report_check


def read_cases(path: Path) -> list[dict[str, str]]:
    """
    读取 fixture case 列表.

    :param path: JSON fixture 路径.
    :return: Case 对象列表.
    """
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{path}: expected a list")
    return payload


def valid_challenge_context() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    """
    构造 Challenge validator 的有效跨工件上下文.

    :return: Challenge Ledger, Gaps 和 Evidence records.
    """
    evidence = deep_check.sample_evidence("run-v65-fixture")
    reference = {
        "source_id": evidence["source_id"],
        "document_url": evidence["document_url"],
        "page_or_section": evidence["page_or_section"],
        "relation": evidence["relation"],
        "evidence_span_sha256": deep_check.evidence_span_sha256(evidence),
    }
    base = {
        "challenge_id": "challenge-industry",
        "reviewer_role": "industry-expert",
        "target_claim_id": "claim-market-size",
        "target_section": "4. Lifecycle Assessment",
        "challenge": "The definition may combine non-comparable categories.",
        "materiality": "high",
        "verification_method": "retrieval",
        "verification_required": "Check the official dataset definition.",
        "gap_id": "gap-market-definition",
        "resolution": "confirmed",
        "evidence_refs": [reference],
        "verification_notes": "The official definition confirms the challenged scope.",
        "report_change": "The report narrows the market definition.",
        "confidence_action": "downgraded",
        "reviewer_status": "closed",
        "closed_by": "original-reviewer",
        "reviewer_note": "The revised scope resolves the challenge.",
    }
    challenges = [
        base,
        dict(base, challenge_id="challenge-investment", reviewer_role="investment-researcher", materiality="medium", closed_by="organizer"),
        dict(base, challenge_id="challenge-policy", reviewer_role="policy-regulatory", materiality="medium", closed_by="organizer"),
        dict(base, challenge_id="challenge-operator", reviewer_role="operator-entrepreneur", materiality="medium", closed_by="organizer"),
    ]
    ledger = {
        "schema_version": "v65",
        "run_id": "run-v65-fixture",
        "review_mode": "multi-agent",
        "challenges": challenges,
    }
    gaps = {
        "gaps": [
            {
                "gap_id": "gap-market-definition",
                "claim_id": "claim-market-size",
                "status": "closed",
            }
        ]
    }
    return ledger, gaps, [evidence]


def mutate_invalid_case(name: str, ledger: dict[str, Any]) -> None:
    """
    按 fixture 名称对 Challenge Ledger 施加一个定向错误.

    :param name: Invalid fixture 名称.
    :param ledger: 待原地修改的 Challenge Ledger.
    :return: None.
    """
    challenge = ledger["challenges"][0]
    if name == "invalid-enum":
        challenge["materiality"] = "critical"
    elif name == "unknown-claim":
        challenge["target_claim_id"] = "claim-unknown"
    elif name == "retrieval-missing-gap":
        challenge["gap_id"] = "gap-unknown"
    elif name == "non-retrieval-gap":
        challenge["verification_method"] = "logic"
    elif name == "evidence-zero-match":
        challenge["evidence_refs"][0]["evidence_span_sha256"] = "0" * 64
    elif name == "confirmed-no-change":
        challenge["report_change"] = ""
    elif name == "confirmed-retrieval-no-evidence":
        challenge["evidence_refs"] = []
    elif name == "refuted-no-basis":
        challenge.update(resolution="refuted", verification_method="retrieval", evidence_refs=[], verification_notes="")
    elif name == "refuted-no-report-change":
        challenge.update(resolution="refuted", report_change="")
    elif name == "unresolved-unchanged":
        challenge.update(resolution="unresolved", confidence_action="unchanged")
    elif name == "high-organizer-close":
        challenge["closed_by"] = "organizer"
    elif name == "high-disputed-formal":
        challenge["reviewer_status"] = "disputed"
    elif name == "pending-formal":
        challenge.update(resolution="pending", reviewer_status="open")


def run_report_fixtures(failures: list[str]) -> int:
    """
    运行八个双语 route 正例和报告结构负例.

    :param failures: 失败记录列表.
    :return: 已执行 case 数.
    """
    count = 0
    fixture_root = ROOT / "tests" / "fixtures" / "v65"
    cases = read_cases(fixture_root / "valid" / "cases.json")
    for case in cases:
        report = (fixture_root / "valid" / case["file"]).read_text(encoding="utf-8")
        for profile in (case["profile"], "auto"):
            errors = report_check.run_profile(report, profile, case["language"])
            count += 1
            if errors:
                failures.append(f"{case['file']} {profile}: {errors[0]}")
    overview = (fixture_root / "valid" / "overview-zh.md").read_text(encoding="utf-8")
    report_cases = {
        "legacy-four-column": overview.replace(
            "| 质疑 ID | 视角 | 目标 Claim/章节 | 重要性 | 核心质疑 | 裁决 | 证据/Gap | 报告改动 | 复核状态 |",
            "| 视角 | 质疑 | 为什么重要 | 需要验证 |",
            1,
        ),
        "pending-reader-row": overview.replace("| confirmed |", "| pending |", 1),
        "open-reader-row": overview.replace("| closed |", "| open |", 1),
        "missing-core-role": overview.replace("投资研究员", "行业专家", 1),
    }
    expected = {case["name"]: case["expected"] for case in read_cases(fixture_root / "invalid" / "cases.json")}
    for name, report in report_cases.items():
        errors = report_check.run_profile(report, "overview", "zh")
        count += 1
        if not any(expected[name] in error for error in errors):
            failures.append(f"{name}: missing directed error {expected[name]!r}")
    no_change_challenge = {
        "materiality": "low",
        "resolution": "refuted",
        "report_change": "无报告改动: 现有证据已证伪该质疑.",
    }
    count += 1
    if report_check.challenge_requires_reader_row(no_change_challenge):
        failures.append("no-change-reason: incorrectly treated as an actual report rewrite")
    return count


def run_challenge_fixtures(failures: list[str]) -> int:
    """
    运行 Challenge schema 和状态机正反例.

    :param failures: 失败记录列表.
    :return: 已执行 case 数.
    """
    ledger, gaps, evidence = valid_challenge_context()
    errors = deep_check.validate_challenges(
        ledger,
        "run-v65-fixture",
        {"claim-market-size"},
        gaps,
        evidence,
        True,
    )
    count = 1
    if errors:
        failures.append(f"valid-challenge-ledger: {errors[0]}")
    invalid_cases = read_cases(ROOT / "tests" / "fixtures" / "v65" / "invalid" / "cases.json")
    for case in invalid_cases:
        if case["name"] in {"legacy-four-column", "pending-reader-row", "open-reader-row", "missing-core-role"}:
            continue
        mutated = json.loads(json.dumps(ledger))
        mutate_invalid_case(case["name"], mutated)
        mutated_gaps = json.loads(json.dumps(gaps))
        if case["name"] == "retrieval-open-gap":
            mutated_gaps["gaps"][0]["status"] = "open"
        errors = deep_check.validate_challenges(
            mutated,
            "run-v65-fixture",
            {"claim-market-size"},
            mutated_gaps,
            evidence,
            True,
        )
        count += 1
        if not any(case["expected"] in error for error in errors):
            failures.append(f"{case['name']}: missing directed error {case['expected']!r}")
    return count


def main() -> int:
    """
    执行 v65 fixture suite 并输出 JSON 结果.

    :return: 退出码, 0 表示通过, 1 表示失败.
    """
    failures: list[str] = []
    report_count = run_report_fixtures(failures)
    challenge_count = run_challenge_fixtures(failures)
    reader_failures = report_check.run_reader_view_self_test()
    failures.extend(f"reader-view: {failure}" for failure in reader_failures)
    payload = {
        "status": "fail" if failures else "pass",
        "report_cases": report_count,
        "challenge_cases": challenge_count,
        "reader_binding_cases": 1,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
