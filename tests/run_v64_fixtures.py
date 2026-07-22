"""
运行 v64 Claim 忠实度的确定性 fixture 套件.
"""

from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = REPO_ROOT / "skills" / "industry-research" / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

from truthfulness_contract_check import (
    build_valid_self_test,
    evidence_span_sha256,
    final_check,
    pre_report_check,
    read_json,
    sample_evidence,
    write_json,
)
from report_contract_check import (
    add_sample_trace_ids,
    englishize_contract_fixture,
    run_profile,
    sample_overview_report,
)


def read_cases(path: Path) -> list[dict[str, str]]:
    """
    读取 fixture case 列表.

    :param path: cases.json 路径.
    :return: Case 对象列表.
    """
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise ValueError(f"{path}: root must be a list")
    return value


def load_fixture(run_dir: Path) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    """
    读取一个临时 fixture 的核心工件.

    :param run_dir: Run 目录.
    :return: Plan, Gaps 和 Evidence.
    """
    plan = read_json(run_dir / "plan.json")
    gaps = read_json(run_dir / "gaps.json")
    evidence = [
        json.loads(line)
        for line in (run_dir / "evidence.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return plan, gaps, evidence


def write_evidence(path: Path, records: list[dict[str, Any]]) -> None:
    """
    写入 fixture Evidence JSONL.

    :param path: Evidence 文件路径.
    :param records: Evidence records.
    :return: None.
    """
    payload = "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records)
    path.write_text(payload, encoding="utf-8")


def set_span_and_reference(
    run_dir: Path,
    report_path: Path,
    span: str,
    evidence: dict[str, Any],
    status: str = "supported",
) -> dict[str, Any]:
    """
    同步 fixture 的报告正文和 canonical binding.

    :param run_dir: Run 目录.
    :param report_path: 报告路径.
    :param span: 新 report span.
    :param evidence: 绑定 Evidence.
    :param status: Claim 状态.
    :return: 更新后的 report-claims 对象.
    """
    report_path.write_text(f"# Example Report\n\n## 1. Direct Answer\n\n{span}\n", encoding="utf-8")
    report_claims = read_json(run_dir / "report-claims.json")
    binding = report_claims["claims"][0]
    binding["claim_status"] = status
    binding["report_span"] = span
    binding["evidence_refs"] = [
        {
            "source_id": evidence["source_id"],
            "document_url": evidence["document_url"],
            "page_or_section": evidence["page_or_section"],
            "relation": evidence["relation"],
            "evidence_span_sha256": evidence_span_sha256(evidence["evidence_span"]),
        }
    ]
    write_json(run_dir / "report-claims.json", report_claims)
    return report_claims


def apply_valid_mutation(mutation: str, run_dir: Path, report_path: Path) -> None:
    """
    将一个基础 fixture 调整为指定有效场景.

    :param mutation: 场景名称.
    :param run_dir: Run 目录.
    :param report_path: 报告路径.
    :return: None.
    """
    if mutation == "base":
        return
    plan, gaps, evidence_records = load_fixture(run_dir)
    evidence = evidence_records[0]
    if mutation == "primary-for-near-primary":
        plan["claims"][0]["required_evidence_tier"] = "near-primary"
        write_json(run_dir / "plan.json", plan)
        return
    if mutation == "independently-verified":
        second = copy.deepcopy(evidence)
        evidence["independence_status"] = "independently_verified"
        second["source_id"] = "example-office-two"
        second["origin_source_id"] = "origin-example-office-two"
        second["document_url"] = "https://example.net/data"
        second["document_title"] = "Independent Example Dataset"
        second["independence_status"] = "independently_verified"
        write_evidence(run_dir / "evidence.jsonl", [evidence, second])
        report_claims = read_json(run_dir / "report-claims.json")
        report_claims["claims"][0]["evidence_refs"][0]["evidence_span_sha256"] = evidence_span_sha256(
            evidence["evidence_span"]
        )
        write_json(run_dir / "report-claims.json", report_claims)
        return
    if mutation == "supplemental-gap":
        gaps["gaps"] = [{"gap_id": "gap-extra", "claim_id": "claim-market-size", "status": "open"}]
        write_json(run_dir / "gaps.json", gaps)
        return
    if mutation == "refuted":
        evidence["relation"] = "refute"
        write_evidence(run_dir / "evidence.jsonl", [evidence])
        span = "The available evidence does not support the claim that the 2025 market value was 100 USD billion."
        report_claims = set_span_and_reference(run_dir, report_path, span, evidence, "refuted")
        report_claims["claims"][0]["numeric_checks"] = [
            {
                "reported_value": "100",
                "mode": "direct",
                "evidence_values": ["100"],
                "unit": "billion",
                "currency": "USD",
                "reporting_period": "2025",
                "review_note": "The refuting Evidence contains the tested value.",
            }
        ]
        report_claims["claims"][0]["numeric_exclusions"] = [
            {"value": "2025", "reason": "date", "review_note": "Reporting period."}
        ]
        write_json(run_dir / "report-claims.json", report_claims)
        return
    if mutation == "percentage-change":
        evidence["evidence_span"] = "The value increased from 80 to 100 USD billion."
        write_evidence(run_dir / "evidence.jsonl", [evidence])
        span = "The value increased from 80 to 100 USD billion, a 25% increase."
        report_claims = set_span_and_reference(run_dir, report_path, span, evidence)
        binding = report_claims["claims"][0]
        binding["numeric_checks"] = [
            {"reported_value": "80", "mode": "direct", "evidence_values": ["80"], "unit": "billion", "currency": "USD", "reporting_period": "2025", "review_note": "Opening value."},
            {"reported_value": "100", "mode": "direct", "evidence_values": ["100"], "unit": "billion", "currency": "USD", "reporting_period": "2025", "review_note": "Closing value."},
            {"reported_value": "25%", "mode": "derived", "evidence_values": ["80", "100"], "operation": "percentage-change", "unit": "percent", "currency": "not-applicable", "reporting_period": "2025", "tolerance": "0.001", "review_note": "Safe percentage change."},
        ]
        binding["numeric_exclusions"] = []
        write_json(run_dir / "report-claims.json", report_claims)
        return
    if mutation in {"identity", "sum", "difference", "ratio", "share"}:
        scenarios = {
            "identity": ("The input was 100 USD billion.", "The derived value was 100 USD billion.", ["100"], "100", "billion", "USD"),
            "sum": ("The inputs were 40 and 60 USD billion.", "The combined value was 100 USD billion.", ["40", "60"], "100", "billion", "USD"),
            "difference": ("The inputs were 140 and 40 USD billion.", "The difference was 100 USD billion.", ["140", "40"], "100", "billion", "USD"),
            "ratio": ("The inputs were 100 and 4.", "The ratio was 25.", ["100", "4"], "25", "not-applicable", "not-applicable"),
            "share": ("The inputs were 25 and 100.", "The share was 25%.", ["25", "100"], "25%", "percent", "not-applicable"),
        }
        evidence_span, span, values, reported, unit, currency = scenarios[mutation]
        evidence["evidence_span"] = evidence_span
        if unit == "not-applicable" or unit == "percent":
            evidence["unit_and_currency"] = "not-applicable"
        write_evidence(run_dir / "evidence.jsonl", [evidence])
        report_claims = set_span_and_reference(run_dir, report_path, span, evidence)
        binding = report_claims["claims"][0]
        binding["numeric_checks"] = [
            {"reported_value": reported, "mode": "derived", "evidence_values": values, "operation": mutation, "unit": unit, "currency": currency, "reporting_period": "2025", "tolerance": "0", "review_note": f"Safe {mutation} calculation."}
        ]
        binding["numeric_exclusions"] = []
        write_json(run_dir / "report-claims.json", report_claims)
        return
    if mutation == "decimal-scale":
        evidence["unit_and_currency"] = "USD million"
        evidence["evidence_span"] = "The value was 100 USD million."
        write_evidence(run_dir / "evidence.jsonl", [evidence])
        span = "The value was 0.1 USD billion."
        report_claims = set_span_and_reference(run_dir, report_path, span, evidence)
        binding = report_claims["claims"][0]
        binding["numeric_checks"] = [
            {"reported_value": "0.1", "mode": "converted", "evidence_values": ["100"], "operation": "decimal-scale", "unit": "billion", "currency": "USD", "reporting_period": "2025", "tolerance": "0", "review_note": "Million to billion decimal scaling."}
        ]
        binding["numeric_exclusions"] = []
        write_json(run_dir / "report-claims.json", report_claims)
        return
    if mutation == "manual-number":
        span = "The adjusted value was 105 USD billion."
        report_claims = set_span_and_reference(run_dir, report_path, span, evidence)
        binding = report_claims["claims"][0]
        binding["numeric_checks"] = [
            {"reported_value": "105", "mode": "manual", "evidence_values": ["100"], "unit": "billion", "currency": "USD", "reporting_period": "2025", "review_note": "Manual adjustment requires reviewer recalculation."}
        ]
        binding["numeric_exclusions"] = []
        binding["manual_review_required"] = True
        write_json(run_dir / "report-claims.json", report_claims)
        return
    if mutation == "chinese-span":
        span = "证据显示, 2025 年市场规模为 100 十亿美元."
        report_claims = set_span_and_reference(run_dir, report_path, span, evidence)
        binding = report_claims["claims"][0]
        binding["numeric_checks"] = [
            {"reported_value": "100", "mode": "direct", "evidence_values": ["100"], "unit": "billion", "currency": "USD", "reporting_period": "2025", "review_note": "直接数字一致."}
        ]
        binding["numeric_exclusions"] = [
            {"value": "2025", "reason": "date", "review_note": "报告期间."}
        ]
        write_json(run_dir / "report-claims.json", report_claims)
        return
    if mutation in {"full-overview-en", "full-overview-zh"}:
        language = "en" if mutation.endswith("en") else "zh"
        heading = "1. One-Sentence Industry Definition" if language == "en" else "1. 行业一句话定义"
        span = (
            "This canonical statement is supported by the obtained primary Evidence."
            if language == "en"
            else "这条规范正文陈述得到已取得的一手 Evidence 支持."
        )
        report_text = add_sample_trace_ids(sample_overview_report(20))
        if language == "en":
            report_text = englishize_contract_fixture(report_text)
        marker = f"## {heading}"
        report_text = report_text.replace(marker, f"{marker}\n\n{span}", 1)
        report_path.write_text(report_text, encoding="utf-8")
        evidence["evidence_span"] = span
        evidence["reporting_period"] = "not-applicable"
        evidence["unit_and_currency"] = "not-applicable"
        write_evidence(run_dir / "evidence.jsonl", [evidence])
        plan["claims"][0]["claim_text"] = span
        write_json(run_dir / "plan.json", plan)
        report_claims = read_json(run_dir / "report-claims.json")
        binding = report_claims["claims"][0]
        binding["report_section"] = heading
        binding["report_span"] = span
        binding["evidence_refs"] = [
            {
                "source_id": evidence["source_id"],
                "document_url": evidence["document_url"],
                "page_or_section": evidence["page_or_section"],
                "relation": evidence["relation"],
                "evidence_span_sha256": evidence_span_sha256(evidence["evidence_span"]),
            }
        ]
        binding["numeric_checks"] = []
        binding["numeric_exclusions"] = []
        write_json(run_dir / "report-claims.json", report_claims)
        return
    raise ValueError(f"unknown valid mutation: {mutation}")


def apply_pre_report_invalid(mutation: str, run_dir: Path) -> bool:
    """
    应用 pre-report 失败场景.

    :param mutation: 场景名称.
    :param run_dir: Run 目录.
    :return: 是否已经完成 mutation.
    """
    plan, gaps, evidence_records = load_fixture(run_dir)
    evidence = evidence_records[0]
    if mutation in {"orphaned", "gapped"}:
        write_evidence(run_dir / "evidence.jsonl", [])
        if mutation == "gapped":
            gaps["gaps"] = [{"gap_id": "gap-missing", "claim_id": "claim-market-size", "status": "open"}]
            write_json(run_dir / "gaps.json", gaps)
        return True
    if mutation == "neutral-only":
        evidence["relation"] = "neutral"
        write_evidence(run_dir / "evidence.jsonl", [evidence])
        return True
    if mutation == "failed-access-only":
        evidence.update({"access_status": "blocked", "relation": "neutral", "evidence_span": ""})
        write_evidence(run_dir / "evidence.jsonl", [evidence])
        return True
    if mutation == "tier-too-low":
        evidence["evidence_tier"] = "secondary"
        write_evidence(run_dir / "evidence.jsonl", [evidence])
        return True
    if mutation == "support-refute-conflict":
        refute = copy.deepcopy(evidence)
        refute["relation"] = "refute"
        refute["document_url"] = "https://example.org/refute"
        refute["document_title"] = "Refuting Dataset"
        write_evidence(run_dir / "evidence.jsonl", [evidence, refute])
        return True
    if mutation == "unresolved-conflict":
        evidence["independence_status"] = "unresolved-conflict"
        evidence["contradiction_group"] = "conflict-market-size"
        write_evidence(run_dir / "evidence.jsonl", [evidence])
        return True
    if mutation == "same-origin-false-independence":
        second = copy.deepcopy(evidence)
        evidence["independence_status"] = "independently_verified"
        second["source_id"] = "example-office-copy"
        second["document_url"] = "https://example.net/copy"
        second["document_title"] = "Copied Example Dataset"
        second["independence_status"] = "independently_verified"
        write_evidence(run_dir / "evidence.jsonl", [evidence, second])
        return True
    return False


def apply_final_invalid(mutation: str, run_dir: Path, report_path: Path) -> None:
    """
    应用 final fidelity 失败场景.

    :param mutation: 场景名称.
    :param run_dir: Run 目录.
    :param report_path: 报告路径.
    :return: None.
    """
    evidence = json.loads((run_dir / "evidence.jsonl").read_text(encoding="utf-8").splitlines()[0])
    report_claims = read_json(run_dir / "report-claims.json")
    binding = report_claims["claims"][0]
    if mutation == "refuted-written-as-support":
        evidence["relation"] = "refute"
        write_evidence(run_dir / "evidence.jsonl", [evidence])
        binding["claim_status"] = "refuted"
        binding["evidence_refs"][0]["relation"] = "refute"
        binding["evidence_refs"][0]["evidence_span_sha256"] = evidence_span_sha256(evidence["evidence_span"])
    elif mutation == "missing-binding":
        report_claims["claims"] = []
    elif mutation == "duplicate-binding":
        report_claims["claims"].append(copy.deepcopy(binding))
    elif mutation == "unknown-claim":
        binding["claim_id"] = "claim-unknown"
    elif mutation == "missing-report-span":
        binding["report_span"] = "A missing statement 100."
    elif mutation == "duplicate-report-span":
        report_path.write_text(report_path.read_text(encoding="utf-8") + "\nThe 2025 market value was 100 USD billion.\n", encoding="utf-8")
    elif mutation == "unknown-evidence-reference":
        binding["evidence_refs"][0]["source_id"] = "unknown-source"
    elif mutation == "wrong-direct-number":
        binding["numeric_checks"][0]["reported_value"] = "101"
    elif mutation == "wrong-derived-number":
        apply_valid_mutation("percentage-change", run_dir, report_path)
        report_claims = read_json(run_dir / "report-claims.json")
        report_claims["claims"][0]["numeric_checks"][2]["reported_value"] = "26%"
    elif mutation == "division-by-zero":
        evidence["evidence_span"] = "The inputs were 100 and 0."
        evidence["unit_and_currency"] = "not-applicable"
        write_evidence(run_dir / "evidence.jsonl", [evidence])
        report_claims = set_span_and_reference(run_dir, report_path, "The ratio was 0.", evidence)
        report_claims["claims"][0]["numeric_checks"] = [
            {"reported_value": "0", "mode": "derived", "evidence_values": ["100", "0"], "operation": "ratio", "unit": "not-applicable", "currency": "not-applicable", "reporting_period": "2025", "tolerance": "0", "review_note": "Division by zero must fail."}
        ]
        report_claims["claims"][0]["numeric_exclusions"] = []
    elif mutation == "wrong-decimal-scale":
        apply_valid_mutation("decimal-scale", run_dir, report_path)
        report_claims = read_json(run_dir / "report-claims.json")
        report_claims["claims"][0]["numeric_checks"][0]["reported_value"] = "0.15"
    elif mutation == "same-unit-decimal-scale":
        binding["numeric_checks"][0]["mode"] = "converted"
        binding["numeric_checks"][0]["operation"] = "decimal-scale"
        binding["numeric_checks"][0]["tolerance"] = "0"
    elif mutation == "manual-without-review":
        apply_valid_mutation("manual-number", run_dir, report_path)
        report_claims = read_json(run_dir / "report-claims.json")
        report_claims["claims"][0]["manual_review_required"] = False
    elif mutation == "unit-conflict":
        binding["numeric_checks"][0]["unit"] = "kilograms"
    elif mutation == "currency-conflict":
        binding["numeric_checks"][0]["currency"] = "CNY"
    elif mutation == "period-conflict":
        binding["numeric_checks"][0]["reporting_period"] = "2024"
    elif mutation == "missing-truthfulness-audit":
        (run_dir / "truthfulness-audit.md").unlink()
    elif mutation == "audit-missing-claim-detail":
        (run_dir / "truthfulness-audit.md").write_text(
            "# Truthfulness Audit\n\n"
            "- reviewer_type: agent-self-check\n"
            "- reviewed_claim_ids: claim-market-size\n",
            encoding="utf-8",
        )
    elif mutation == "report-path-mismatch":
        report_claims["report_path"] = "reports/other.md"
    else:
        raise ValueError(f"unknown invalid mutation: {mutation}")
    write_json(run_dir / "report-claims.json", report_claims)


def run_case(case: dict[str, str], should_pass: bool) -> list[str]:
    """
    运行单个 v64 fixture case.

    :param case: Fixture case.
    :param should_pass: 是否预期通过.
    :return: 失败说明列表.
    """
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        run_dir, report_path = build_valid_self_test(root)
        mutation = case["mutation"]
        if should_pass:
            apply_valid_mutation(mutation, run_dir, report_path)
            result = final_check(run_dir, report_path, root)
            errors = list(result.errors)
            if mutation in {"full-overview-en", "full-overview-zh"}:
                language = "en" if mutation.endswith("en") else "zh"
                report_text = report_path.read_text(encoding="utf-8")
                errors.extend(run_profile(report_text, "overview", language=language))
                errors.extend(run_profile(report_text, "auto", language=language))
            return [] if not errors else [f"{case['name']}: unexpected errors: {errors}"]
        if apply_pre_report_invalid(mutation, run_dir):
            result = pre_report_check(run_dir)
        else:
            apply_final_invalid(mutation, run_dir, report_path)
            result = final_check(run_dir, report_path, root)
        expected = case["expected"]
        if not result.errors:
            return [f"{case['name']}: expected failure but passed"]
        if not any(expected in error for error in result.errors):
            return [f"{case['name']}: missing expected fragment {expected}: {result.errors}"]
        return []


def main() -> int:
    """
    执行 v64 fixture suite.

    :return: 进程退出码.
    """
    fixture_root = REPO_ROOT / "tests" / "fixtures" / "v64"
    valid_cases = read_cases(fixture_root / "valid" / "cases.json")
    invalid_cases = read_cases(fixture_root / "invalid" / "cases.json")
    failures: list[str] = []
    for case in valid_cases:
        failures.extend(run_case(case, True))
    for case in invalid_cases:
        failures.extend(run_case(case, False))
    payload = {
        "status": "fail" if failures else "pass",
        "valid": len(valid_cases),
        "invalid": len(invalid_cases),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
