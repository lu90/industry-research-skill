"""
校验 v64 Claim 证据准入和报告忠实度合同.

本脚本复用 v61 Evidence 校验, 并检查逐 Claim 状态, 正文绑定, 数字忠实度和抽样审计.
它不证明外部来源真实, 也不执行任意表达式或复杂语义判断.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
import unicodedata
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from source_contract_check import load_evidence_jsonl, validate_evidence


TIER_RANK = {"weak": 0, "secondary": 1, "near-primary": 2, "primary": 3}
CLAIM_STATUSES = {"supported", "refuted", "conflicted", "gapped", "orphaned"}
REPORT_CLAIM_STATUSES = {"supported", "refuted"}
ASSERTION_KINDS = {"fact", "external-opinion", "inference", "causal", "forecast"}
NUMERIC_MODES = {"direct", "derived", "converted", "manual"}
SAFE_OPERATIONS = {"identity", "sum", "difference", "ratio", "share", "percentage-change", "decimal-scale"}
EXCLUSION_REASONS = {"date", "identifier", "section-number", "non-claim-context"}
PERCENT_OPERATIONS = {"share", "percentage-change"}
DECIMAL_UNIT_SCALES = {
    "thousand": 3,
    "million": 6,
    "billion": 9,
    "trillion": 12,
    "千": 3,
    "万": 4,
    "百万": 6,
    "千万": 7,
    "亿": 8,
    "十亿": 9,
    "万亿": 12,
}
REPORT_CLAIMS_FIELDS = {"schema_version", "run_id", "report_path", "claims"}
BINDING_FIELDS = {
    "claim_id",
    "claim_status",
    "assertion_kind",
    "report_section",
    "report_span",
    "evidence_refs",
    "numeric_checks",
    "numeric_exclusions",
    "verification_notes",
    "manual_review_required",
}
EVIDENCE_REF_FIELDS = {
    "source_id",
    "document_url",
    "page_or_section",
    "relation",
    "evidence_span_sha256",
}
NUMERIC_CHECK_FIELDS = {
    "reported_value",
    "mode",
    "evidence_values",
    "unit",
    "currency",
    "reporting_period",
    "review_note",
}
NUMERIC_EXCLUSION_FIELDS = {"value", "reason", "review_note"}
NUMBER_PATTERN = re.compile(r"(?<![\w.])[-+]?\d[\d,]*(?:\.\d+)?%?")
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
REFUTATION_MARKERS = (
    "不支持",
    "不受支持",
    "被反驳",
    "无法证明",
    "未能证实",
    "证据不足",
    "not supported",
    "unsupported",
    "refuted",
    "does not support",
    "failed to confirm",
    "evidence is insufficient",
)
FORBIDDEN_SECTION_FRAGMENTS = (
    "来源矩阵",
    "source matrix",
    "合规自检",
    "compliance checklist",
    "方法论",
    "methodology",
    "免责声明",
    "disclaimer",
)
AUDIT_FIELDS = (
    "atomicity",
    "evidence_relation",
    "report_fidelity",
    "numeric_scope",
    "inference_limits",
    "counterevidence",
)


@dataclass
class CheckResult:
    """
    保存 Checker 的错误, 警告和逐 Claim 状态.
    """

    errors: list[str]
    warnings: list[str]
    claims: list[dict[str, Any]]


def read_json(path: Path) -> dict[str, Any]:
    """
    读取 UTF-8 JSON 对象.

    :param path: JSON 文件路径.
    :return: JSON 对象.
    """
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    return value


def normalize_text(value: str) -> str:
    """
    规范 Unicode 和空白以支持稳定哈希.

    :param value: 原始文本.
    :return: 规范文本.
    """
    return " ".join(unicodedata.normalize("NFKC", value).split())


def evidence_span_sha256(value: str) -> str:
    """
    计算规范 Evidence span 的 SHA-256.

    :param value: Evidence span.
    :return: 十六进制摘要.
    """
    return hashlib.sha256(normalize_text(value).encode("utf-8")).hexdigest()


def missing_fields(record: dict[str, Any], required: set[str]) -> list[str]:
    """
    返回记录缺少的必填字段.

    :param record: 待检查记录.
    :param required: 必填字段集合.
    :return: 已排序的缺失字段.
    """
    return sorted(required - set(record))


def tier_satisfies(actual: Any, required: Any) -> bool:
    """
    判断实际 Evidence tier 是否达到 Claim 最低层级.

    :param actual: 实际 Evidence tier.
    :param required: Claim 要求的最低 Evidence tier.
    :return: 是否达到最低层级.
    """
    return actual in TIER_RANK and required in TIER_RANK and TIER_RANK[actual] >= TIER_RANK[required]


def qualifying_evidence(claim: dict[str, Any], records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    筛选一个 Claim 可用于准入的 Evidence.

    :param claim: Plan Claim.
    :param records: 全部 Evidence records.
    :return: 达标 Evidence records.
    """
    claim_id = claim.get("claim_id")
    required_tier = claim.get("required_evidence_tier")
    return [
        record
        for record in records
        if record.get("claim_id") == claim_id
        and record.get("access_status") == "obtained"
        and record.get("relation") in {"support", "refute"}
        and bool(str(record.get("evidence_span", "")).strip())
        and bool(str(record.get("page_or_section", "")).strip())
        and tier_satisfies(record.get("evidence_tier"), required_tier)
    ]


def calculate_claim_status(
    claim: dict[str, Any],
    records: list[dict[str, Any]],
    gaps: list[dict[str, Any]],
) -> tuple[str, list[dict[str, Any]], str]:
    """
    计算一个 Claim 的 v64 状态.

    :param claim: Plan Claim.
    :param records: 全部 Evidence records.
    :param gaps: 全部 Gap records.
    :return: Claim 状态, 达标 Evidence 和原因.
    """
    claim_id = claim.get("claim_id")
    admitted = qualifying_evidence(claim, records)
    relations = {record.get("relation") for record in admitted}
    unresolved = any(record.get("independence_status") == "unresolved-conflict" for record in admitted)
    if unresolved or relations == {"support", "refute"}:
        return "conflicted", admitted, "material support and refute conflict remains"
    if relations == {"support"}:
        return "supported", admitted, "qualifying support evidence exists"
    if relations == {"refute"}:
        return "refuted", admitted, "qualifying refute evidence exists"
    if any(gap.get("claim_id") == claim_id for gap in gaps if isinstance(gap, dict)):
        return "gapped", admitted, "no qualifying evidence and an explicit Gap exists"
    return "orphaned", admitted, "no qualifying evidence or matching Gap exists"


def validate_plan_shape(plan: dict[str, Any]) -> list[str]:
    """
    校验 v64 所需的最小 Plan 结构.

    :param plan: Plan 对象.
    :return: 错误列表.
    """
    errors: list[str] = []
    claims = plan.get("claims")
    if not isinstance(claims, list) or not claims:
        return ["plan: claims must be a non-empty list"]
    seen: set[str] = set()
    for index, claim in enumerate(claims, start=1):
        if not isinstance(claim, dict):
            errors.append(f"plan.claims[{index}]: must be an object")
            continue
        claim_id = claim.get("claim_id")
        if not isinstance(claim_id, str) or not re.fullmatch(r"claim-[a-z0-9]+(?:-[a-z0-9]+)*", claim_id):
            errors.append(f"plan.claims[{index}]: invalid claim_id")
        if claim_id in seen:
            errors.append(f"plan.claims[{index}]: duplicate claim_id")
        seen.add(str(claim_id))
        if claim.get("required_evidence_tier") not in TIER_RANK:
            errors.append(f"plan.claims[{index}]: invalid required_evidence_tier")
    return errors


def pre_report_check(run_dir: Path) -> CheckResult:
    """
    执行逐 Claim 证据准入检查.

    :param run_dir: Research Run 目录.
    :return: Checker 结果.
    """
    errors: list[str] = []
    warnings: list[str] = []
    outcomes: list[dict[str, Any]] = []
    required_paths = ("plan.json", "evidence.jsonl", "gaps.json")
    missing = [name for name in required_paths if not (run_dir / name).is_file()]
    if missing:
        return CheckResult([f"missing artifact: {name}" for name in missing], warnings, outcomes)
    try:
        plan = read_json(run_dir / "plan.json")
        gaps_object = read_json(run_dir / "gaps.json")
        records = load_evidence_jsonl(run_dir / "evidence.jsonl")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return CheckResult([str(exc)], warnings, outcomes)
    errors.extend(validate_plan_shape(plan))
    errors.extend(validate_evidence(records))
    gap_records = gaps_object.get("gaps", [])
    if not isinstance(gap_records, list):
        errors.append("gaps: gaps must be a list")
        gap_records = []
    if errors:
        return CheckResult(errors, warnings, outcomes)
    run_id = run_dir.name
    if plan.get("run_id") != run_id:
        errors.append("plan: run_id mismatch")
    if gaps_object.get("run_id") != run_id:
        errors.append("gaps: run_id mismatch")
    for record in records:
        if record.get("run_id") != run_id:
            errors.append(f"{record.get('claim_id', 'unknown')}: Evidence run_id mismatch")
    for claim in plan["claims"]:
        status, admitted, reason = calculate_claim_status(claim, records, gap_records)
        outcome = {
            "claim_id": claim["claim_id"],
            "status": status,
            "qualifying_evidence_count": len(admitted),
            "reason": reason,
        }
        outcomes.append(outcome)
        if status not in REPORT_CLAIM_STATUSES:
            errors.append(f"{claim['claim_id']}: formal report denied because Claim is {status}")
        if status in REPORT_CLAIM_STATUSES and any(
            record.get("independence_status") == "single-source-primary" for record in admitted
        ):
            warnings.append(f"{claim['claim_id']}: single-source-primary limitation must remain visible")
    return CheckResult(errors, warnings, outcomes)


def find_evidence_matches(
    claim_id: str,
    reference: dict[str, Any],
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    使用 v64 组合定位字段查找 Evidence.

    :param claim_id: 目标 Claim ID.
    :param reference: Evidence reference.
    :param records: 全部 Evidence records.
    :return: 匹配的 Evidence records.
    """
    return [
        record
        for record in records
        if record.get("claim_id") == claim_id
        and record.get("source_id") == reference.get("source_id")
        and record.get("document_url") == reference.get("document_url")
        and record.get("page_or_section") == reference.get("page_or_section")
        and record.get("relation") == reference.get("relation")
        and evidence_span_sha256(str(record.get("evidence_span", "")))
        == reference.get("evidence_span_sha256")
    ]


def find_section(report_text: str, heading: str) -> tuple[str | None, int]:
    """
    提取一个精确 Markdown 章节的文本.

    :param report_text: 最终报告文本.
    :param heading: 不带井号的规范章节标题.
    :return: 章节文本和匹配次数.
    """
    matches = list(HEADING_PATTERN.finditer(report_text))
    selected = [index for index, match in enumerate(matches) if match.group(2).strip() == heading.strip()]
    if len(selected) != 1:
        return None, len(selected)
    position = selected[0]
    current = matches[position]
    level = len(current.group(1))
    end = len(report_text)
    for later in matches[position + 1 :]:
        if len(later.group(1)) <= level:
            end = later.start()
            break
    return report_text[current.start() : end], 1


def parse_decimal(value: Any) -> Decimal:
    """
    将展示数字解析为 Decimal.

    :param value: 数字或数字字符串.
    :return: Decimal 数值.
    """
    text = str(value).strip().replace(",", "")
    if text.endswith("%"):
        text = text[:-1]
    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"invalid decimal value: {value}") from exc


def numeric_tokens(value: str) -> list[str]:
    """
    提取正文中的数字 token.

    :param value: 正文文本.
    :return: 原始数字 token 列表.
    """
    return NUMBER_PATTERN.findall(value)


def evidence_contains_value(value: Any, records: list[dict[str, Any]]) -> bool:
    """
    判断绑定 Evidence 是否包含一个数字值.

    :param value: 待定位数字.
    :param records: 绑定 Evidence records.
    :return: 是否存在数值相等的 token.
    """
    try:
        target = parse_decimal(value)
    except ValueError:
        return False
    for record in records:
        for token in numeric_tokens(str(record.get("evidence_span", ""))):
            try:
                if parse_decimal(token) == target:
                    return True
            except ValueError:
                continue
    return False


def calculate_numeric(operation: str, values: list[Decimal]) -> Decimal:
    """
    使用固定安全操作计算派生数字.

    :param operation: 安全操作名称.
    :param values: Evidence 数值.
    :return: 计算结果.
    """
    if operation == "identity" and len(values) == 1:
        return values[0]
    if operation == "sum" and values:
        return sum(values, Decimal("0"))
    if operation == "difference" and len(values) == 2:
        return values[0] - values[1]
    if operation == "ratio" and len(values) == 2 and values[1] != 0:
        return values[0] / values[1]
    if operation == "share" and len(values) == 2 and values[1] != 0:
        return values[0] / values[1] * Decimal("100")
    if operation == "percentage-change" and len(values) == 2 and values[0] != 0:
        return (values[1] - values[0]) / values[0] * Decimal("100")
    raise ValueError(f"unsupported operand count for {operation}")


def decimal_scale_matches(reported: Decimal, source: Decimal, tolerance: Decimal) -> bool:
    """
    判断两个数字是否只相差十进制数量级.

    :param reported: 报告数字.
    :param source: Evidence 数字.
    :param tolerance: 允许误差.
    :return: 是否为支持范围内的十进制缩放.
    """
    for exponent in range(-12, 13):
        if abs(source * (Decimal(10) ** exponent) - reported) <= tolerance:
            return True
    return False


def detect_decimal_unit_scale(value: str) -> int | None:
    """
    从单位文本提取十进制数量级.

    :param value: 单位文本.
    :return: 十进制指数或 None.
    """
    normalized = value.casefold()
    for word in sorted(DECIMAL_UNIT_SCALES, key=len, reverse=True):
        if word in normalized:
            return DECIMAL_UNIT_SCALES[word]
    return None


def validate_numeric_check(
    check: dict[str, Any],
    records: list[dict[str, Any]],
    location: str,
) -> tuple[list[str], list[str]]:
    """
    校验一条 Numeric check record.

    :param check: Numeric check record.
    :param records: 绑定 Evidence records.
    :param location: 错误位置标签.
    :return: 错误和警告列表.
    """
    errors: list[str] = []
    warnings: list[str] = []
    missing = missing_fields(check, NUMERIC_CHECK_FIELDS)
    if missing:
        return [f"{location}: missing fields: {', '.join(missing)}"], warnings
    mode = check.get("mode")
    if mode not in NUMERIC_MODES:
        return [f"{location}: invalid mode"], warnings
    evidence_values = check.get("evidence_values")
    if not isinstance(evidence_values, list):
        return [f"{location}: evidence_values must be a list"], warnings
    if not str(check.get("review_note", "")).strip():
        errors.append(f"{location}: review_note must be non-empty")
    operation = check.get("operation")
    if mode in {"derived", "converted"} and operation not in SAFE_OPERATIONS:
        errors.append(f"{location}: invalid or missing operation")
    if mode in {"derived", "converted"} and "tolerance" not in check:
        errors.append(f"{location}: derived or converted mode requires tolerance")
    if mode == "converted" and operation != "decimal-scale":
        errors.append(f"{location}: converted mode requires decimal-scale")
    if not evidence_values:
        errors.append(f"{location}: numeric check requires evidence_values")
    if not records:
        errors.append(f"{location}: no uniquely bound Evidence")
        return errors, warnings
    for value in evidence_values:
        if not evidence_contains_value(value, records):
            errors.append(f"{location}: evidence value {value} is absent from bound Evidence")
    if mode == "manual":
        return errors, warnings
    try:
        reported = parse_decimal(check.get("reported_value"))
        values = [parse_decimal(value) for value in evidence_values]
        tolerance = parse_decimal(check.get("tolerance", "0"))
    except ValueError as exc:
        errors.append(f"{location}: {exc}")
        return errors, warnings
    if tolerance < 0:
        errors.append(f"{location}: tolerance must be non-negative")
        return errors, warnings
    if mode == "direct":
        if not evidence_contains_value(check.get("reported_value"), records):
            errors.append(f"{location}: direct reported value is absent from bound Evidence")
    elif mode == "derived":
        try:
            expected = calculate_numeric(str(operation), values)
        except ValueError as exc:
            errors.append(f"{location}: {exc}")
        else:
            if abs(expected - reported) > tolerance:
                errors.append(f"{location}: derived value does not match safe recalculation")
    elif len(values) != 1 or not decimal_scale_matches(reported, values[0], tolerance):
        errors.append(f"{location}: converted value is not a decimal-scale conversion")
    periods = {str(record.get("reporting_period", "")).casefold() for record in records}
    reporting_period = str(check.get("reporting_period", "")).casefold()
    if reporting_period not in periods:
        if mode == "manual" or periods & {"unknown", "not-applicable"}:
            warnings.append(f"{location}: reporting_period requires manual compatibility review")
        else:
            errors.append(f"{location}: reporting_period is incompatible with bound Evidence")
    unit_currency = " ".join(str(record.get("unit_and_currency", "")).casefold() for record in records)
    currency = str(check.get("currency", "")).casefold()
    if currency != "not-applicable" and currency not in unit_currency:
        if mode == "manual" or "unknown" in unit_currency:
            warnings.append(f"{location}: currency requires manual compatibility review")
        else:
            errors.append(f"{location}: currency is incompatible with bound Evidence")
    unit = str(check.get("unit", "")).casefold()
    if unit != "not-applicable" and unit not in unit_currency:
        convertible_units = detect_decimal_unit_scale(unit) is not None and detect_decimal_unit_scale(
            unit_currency
        ) is not None
        derived_percent = mode == "derived" and operation in PERCENT_OPERATIONS and unit in {"percent", "%"}
        if mode == "manual" or "unknown" in unit_currency:
            warnings.append(f"{location}: unit requires manual compatibility review")
        elif derived_percent or (mode == "converted" and convertible_units):
            pass
        else:
            errors.append(f"{location}: unit is incompatible with bound Evidence")
    if mode == "converted" and values:
        report_scale = detect_decimal_unit_scale(unit)
        evidence_scale = detect_decimal_unit_scale(unit_currency)
        if report_scale is None or evidence_scale is None or report_scale == evidence_scale:
            errors.append(f"{location}: converted mode requires distinct supported decimal-scale units")
        else:
            expected = values[0] * (Decimal(10) ** (evidence_scale - report_scale))
            if abs(expected - reported) > tolerance:
                errors.append(f"{location}: converted value does not match declared unit scaling")
    return errors, warnings


def validate_binding(
    binding: dict[str, Any],
    expected_status: str,
    report_text: str,
    records: list[dict[str, Any]],
    required_tier: str,
    location: str,
) -> tuple[list[str], list[str]]:
    """
    校验一个 Claim binding record.

    :param binding: Claim binding record.
    :param expected_status: Pre-report 计算的 Claim 状态.
    :param report_text: 最终报告文本.
    :param records: 全部 Evidence records.
    :param required_tier: Claim 要求的最低 Evidence tier.
    :param location: 错误位置标签.
    :return: 错误和警告列表.
    """
    errors: list[str] = []
    warnings: list[str] = []
    missing = missing_fields(binding, BINDING_FIELDS)
    if missing:
        return [f"{location}: missing fields: {', '.join(missing)}"], warnings
    if binding.get("claim_status") not in REPORT_CLAIM_STATUSES:
        errors.append(f"{location}: invalid claim_status")
    if binding.get("claim_status") != expected_status:
        errors.append(f"{location}: claim_status does not match pre-report status")
    if binding.get("assertion_kind") not in ASSERTION_KINDS:
        errors.append(f"{location}: invalid assertion_kind")
    if not isinstance(binding.get("verification_notes"), str) or not binding["verification_notes"].strip():
        errors.append(f"{location}: verification_notes must be non-empty")
    if not isinstance(binding.get("manual_review_required"), bool):
        errors.append(f"{location}: manual_review_required must be Boolean")
    report_span = binding.get("report_span")
    report_section = binding.get("report_section")
    if not isinstance(report_span, str) or not report_span.strip():
        errors.append(f"{location}: report_span must be non-empty")
        return errors, warnings
    if report_text.count(report_span) != 1:
        errors.append(f"{location}: report_span must appear exactly once")
    section_text, section_count = find_section(report_text, str(report_section))
    if section_count != 1:
        errors.append(f"{location}: report_section must match exactly one heading")
    elif report_span not in str(section_text):
        errors.append(f"{location}: report_span is outside report_section")
    lowered_section = str(report_section).casefold()
    if any(fragment in lowered_section for fragment in FORBIDDEN_SECTION_FRAGMENTS):
        errors.append(f"{location}: report_span cannot bind to excluded report boilerplate")
    if expected_status == "refuted" and not any(marker in report_span.casefold() for marker in REFUTATION_MARKERS):
        errors.append(f"{location}: refuted Claim is not presented as denied, narrowed, or unsupported")
    references = binding.get("evidence_refs")
    if not isinstance(references, list) or not references:
        errors.append(f"{location}: evidence_refs must be a non-empty list")
        references = []
    bound_records: list[dict[str, Any]] = []
    for index, reference in enumerate(references, start=1):
        ref_location = f"{location}.evidence_refs[{index}]"
        if not isinstance(reference, dict):
            errors.append(f"{ref_location}: must be an object")
            continue
        missing_reference = missing_fields(reference, EVIDENCE_REF_FIELDS)
        if missing_reference:
            errors.append(f"{ref_location}: missing fields: {', '.join(missing_reference)}")
            continue
        matches = find_evidence_matches(str(binding.get("claim_id")), reference, records)
        if len(matches) != 1:
            errors.append(f"{ref_location}: Evidence reference must match exactly one record")
        else:
            bound_records.extend(matches)
            if not tier_satisfies(matches[0].get("evidence_tier"), required_tier):
                errors.append(f"{ref_location}: Evidence tier is below Claim requirement")
            if matches[0].get("access_status") != "obtained":
                errors.append(f"{ref_location}: Evidence must be obtained")
            if reference.get("relation") != ("support" if expected_status == "supported" else "refute"):
                errors.append(f"{ref_location}: relation does not match claim_status")
    checks = binding.get("numeric_checks")
    exclusions = binding.get("numeric_exclusions")
    if not isinstance(checks, list):
        errors.append(f"{location}: numeric_checks must be a list")
        checks = []
    if not isinstance(exclusions, list):
        errors.append(f"{location}: numeric_exclusions must be a list")
        exclusions = []
    covered: list[str] = []
    manual_present = False
    for index, check in enumerate(checks, start=1):
        check_location = f"{location}.numeric_checks[{index}]"
        if not isinstance(check, dict):
            errors.append(f"{check_location}: must be an object")
            continue
        covered.append(str(check.get("reported_value", "")))
        manual_present = manual_present or check.get("mode") == "manual"
        check_errors, check_warnings = validate_numeric_check(check, bound_records, check_location)
        errors.extend(check_errors)
        warnings.extend(check_warnings)
    for index, exclusion in enumerate(exclusions, start=1):
        exclusion_location = f"{location}.numeric_exclusions[{index}]"
        if not isinstance(exclusion, dict):
            errors.append(f"{exclusion_location}: must be an object")
            continue
        missing_exclusion = missing_fields(exclusion, NUMERIC_EXCLUSION_FIELDS)
        if missing_exclusion:
            errors.append(f"{exclusion_location}: missing fields: {', '.join(missing_exclusion)}")
            continue
        if exclusion.get("reason") not in EXCLUSION_REASONS:
            errors.append(f"{exclusion_location}: invalid reason")
        if not str(exclusion.get("review_note", "")).strip():
            errors.append(f"{exclusion_location}: review_note must be non-empty")
        covered.append(str(exclusion.get("value", "")))
    expected_tokens = Counter(numeric_tokens(report_span))
    covered_tokens = Counter(covered)
    if expected_tokens != covered_tokens:
        errors.append(f"{location}: numeric token coverage mismatch")
    if manual_present and binding.get("manual_review_required") is not True:
        errors.append(f"{location}: manual numeric check requires manual_review_required true")
    if binding.get("assertion_kind") in {"inference", "causal", "forecast"} and not binding.get(
        "manual_review_required"
    ):
        warnings.append(f"{location}: complex assertion should be prioritized for manual review")
    return errors, warnings


def repository_relative_path(path: Path, repo_root: Path) -> str:
    """
    将文件路径转为仓库相对 POSIX 路径.

    :param path: 文件路径.
    :param repo_root: 仓库根目录.
    :return: 仓库相对路径.
    """
    absolute = path if path.is_absolute() else repo_root / path
    try:
        return absolute.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError("report must be inside repo_root") from exc


def validate_audit(run_dir: Path, claim_ids: list[str], required_ids: set[str]) -> list[str]:
    """
    校验 truthfulness audit 的抽样数量和 reviewer 声明.

    :param run_dir: Research Run 目录.
    :param claim_ids: 全部正式报告 Claim ID.
    :param required_ids: 必须人工复核的 Claim ID.
    :return: 错误列表.
    """
    path = run_dir / "truthfulness-audit.md"
    if not path.is_file():
        return ["missing artifact: truthfulness-audit.md"]
    text = path.read_text(encoding="utf-8")
    reviewer_match = re.search(r"(?mi)^-\s*reviewer_type:\s*(human|agent-self-check)\s*$", text)
    reviewed_match = re.search(r"(?mi)^-\s*reviewed_claim_ids:\s*(.+?)\s*$", text)
    errors: list[str] = []
    if not reviewer_match:
        errors.append("truthfulness-audit: missing valid reviewer_type")
    if not reviewed_match:
        return errors + ["truthfulness-audit: missing reviewed_claim_ids"]
    reviewed = {item.strip() for item in reviewed_match.group(1).split(",") if item.strip()}
    unknown = reviewed - set(claim_ids)
    if unknown:
        errors.append(f"truthfulness-audit: unknown reviewed Claim IDs: {', '.join(sorted(unknown))}")
    minimum = min(3, len(claim_ids))
    if len(reviewed) < minimum:
        errors.append(f"truthfulness-audit: at least {minimum} Claims must be reviewed")
    missing_required = required_ids - reviewed
    if missing_required:
        errors.append(
            "truthfulness-audit: manual_review_required Claims are missing: "
            + ", ".join(sorted(missing_required))
        )
    for claim_id in reviewed:
        section, count = find_section(text, claim_id)
        if count != 1:
            errors.append(f"truthfulness-audit: {claim_id} must have exactly one review section")
            continue
        for field in AUDIT_FIELDS:
            pattern = rf"(?mi)^-\s*{re.escape(field)}:\s*(\S.*?)\s*$"
            if not re.search(pattern, str(section)):
                errors.append(f"truthfulness-audit: {claim_id} missing non-empty {field}")
    return errors


def final_check(run_dir: Path, report_path: Path, repo_root: Path) -> CheckResult:
    """
    执行报告正文和数字忠实度终检.

    :param run_dir: Research Run 目录.
    :param report_path: 最终报告或待审草稿路径.
    :param repo_root: 仓库根目录.
    :return: Checker 结果.
    """
    pre_result = pre_report_check(run_dir)
    errors = list(pre_result.errors)
    warnings = list(pre_result.warnings)
    outcomes = list(pre_result.claims)
    if errors:
        return CheckResult(errors, warnings, outcomes)
    required_paths = (run_dir / "report-claims.json", report_path)
    missing = [str(path) for path in required_paths if not path.is_file()]
    if missing:
        return CheckResult(errors + [f"missing artifact: {path}" for path in missing], warnings, outcomes)
    try:
        report_claims = read_json(run_dir / "report-claims.json")
        records = load_evidence_jsonl(run_dir / "evidence.jsonl")
        report_text = report_path.read_text(encoding="utf-8")
        expected_report_path = repository_relative_path(report_path, repo_root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return CheckResult(errors + [str(exc)], warnings, outcomes)
    missing_top = missing_fields(report_claims, REPORT_CLAIMS_FIELDS)
    if missing_top:
        errors.append(f"report-claims: missing fields: {', '.join(missing_top)}")
        return CheckResult(errors, warnings, outcomes)
    if report_claims.get("schema_version") != "v64":
        errors.append("report-claims: schema_version must be v64")
    if report_claims.get("run_id") != run_dir.name:
        errors.append("report-claims: run_id mismatch")
    if report_claims.get("report_path") != expected_report_path:
        errors.append("report-claims: report_path mismatch")
    if not str(report_claims.get("report_path", "")).startswith("reports/"):
        errors.append("report-claims: report_path must use a reports/ path")
    if Path(str(report_claims.get("report_path", ""))).stem != run_dir.name:
        errors.append("report-claims: report filename stem must equal run_id")
    bindings = report_claims.get("claims")
    if not isinstance(bindings, list):
        return CheckResult(errors + ["report-claims: claims must be a list"], warnings, outcomes)
    expected_statuses = {outcome["claim_id"]: outcome["status"] for outcome in outcomes}
    plan = read_json(run_dir / "plan.json")
    required_tiers = {
        str(claim.get("claim_id")): str(claim.get("required_evidence_tier"))
        for claim in plan.get("claims", [])
        if isinstance(claim, dict)
    }
    binding_ids = [binding.get("claim_id") for binding in bindings if isinstance(binding, dict)]
    counts = Counter(binding_ids)
    for claim_id in expected_statuses:
        if counts[claim_id] != 1:
            errors.append(f"report-claims: {claim_id} must have exactly one binding record")
    for claim_id in counts:
        if claim_id not in expected_statuses:
            errors.append(f"report-claims: unknown claim_id {claim_id}")
    manual_ids: set[str] = set()
    for index, binding in enumerate(bindings, start=1):
        location = f"report-claims.claims[{index}]"
        if not isinstance(binding, dict):
            errors.append(f"{location}: must be an object")
            continue
        claim_id = str(binding.get("claim_id", ""))
        if claim_id not in expected_statuses:
            continue
        binding_errors, binding_warnings = validate_binding(
            binding,
            expected_statuses[claim_id],
            report_text,
            records,
            required_tiers[claim_id],
            location,
        )
        errors.extend(binding_errors)
        warnings.extend(binding_warnings)
        if binding.get("manual_review_required") is True:
            manual_ids.add(claim_id)
    errors.extend(validate_audit(run_dir, list(expected_statuses), manual_ids))
    manifest_path = run_dir / "manifest.json"
    if manifest_path.is_file():
        try:
            manifest = read_json(manifest_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(str(exc))
        else:
            if manifest.get("report_status") == "generated" and manifest.get("report_path") != expected_report_path:
                errors.append("manifest: generated report_path does not match audited report")
    return CheckResult(errors, warnings, outcomes)


def sample_plan(run_id: str) -> dict[str, Any]:
    """
    构造 self-test 使用的最小 Plan.

    :param run_id: Run ID.
    :return: Plan 对象.
    """
    return {
        "schema_version": "v62",
        "run_id": run_id,
        "claims": [
            {
                "claim_id": "claim-market-size",
                "claim_text": "The market value was 100 in 2025.",
                "required_evidence_tier": "primary",
            }
        ],
    }


def sample_evidence(run_id: str, relation: str = "support") -> dict[str, Any]:
    """
    构造 self-test 使用的 Evidence record.

    :param run_id: Run ID.
    :param relation: Evidence 关系.
    :return: Evidence record.
    """
    return {
        "run_id": run_id,
        "claim_id": "claim-market-size",
        "source_id": "example-office",
        "registry_status": "registered",
        "document_title": "Example Dataset",
        "document_url": "https://example.org/data",
        "publisher": "Example Office",
        "published_at": "2026-06-30",
        "accessed_at": "2026-07-21",
        "reporting_period": "2025",
        "geography": "global",
        "unit_and_currency": "USD billion",
        "definition": "Annual nominal market value.",
        "page_or_section": "Table 1",
        "evidence_span": "The 2025 market value was 100 USD billion.",
        "relation": relation,
        "evidence_tier": "primary",
        "access_status": "obtained",
        "origin_source_id": "origin-example-office",
        "independence_status": "single-source-primary",
        "contradiction_group": "",
        "confidence": "high",
    }


def write_json(path: Path, value: dict[str, Any]) -> None:
    """
    写入 self-test 使用的 UTF-8 JSON.

    :param path: 目标路径.
    :param value: JSON 对象.
    :return: None.
    """
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def build_valid_self_test(root: Path) -> tuple[Path, Path]:
    """
    构造完整有效的 v64 self-test fixture.

    :param root: 临时仓库根目录.
    :return: Run 目录和报告路径.
    """
    run_id = "run-v64-test"
    run_dir = root / "research_runs" / run_id
    report_path = root / "reports" / f"{run_id}.md"
    run_dir.mkdir(parents=True)
    report_path.parent.mkdir(parents=True)
    plan = sample_plan(run_id)
    evidence = sample_evidence(run_id)
    write_json(run_dir / "plan.json", plan)
    write_json(run_dir / "gaps.json", {"schema_version": "v62", "run_id": run_id, "gaps": [], "contradictions": []})
    (run_dir / "evidence.jsonl").write_text(json.dumps(evidence, ensure_ascii=False) + "\n", encoding="utf-8")
    report_span = "The 2025 market value was 100 USD billion."
    report_path.write_text(f"# Example Report\n\n## 1. Direct Answer\n\n{report_span}\n", encoding="utf-8")
    reference = {
        "source_id": evidence["source_id"],
        "document_url": evidence["document_url"],
        "page_or_section": evidence["page_or_section"],
        "relation": "support",
        "evidence_span_sha256": evidence_span_sha256(evidence["evidence_span"]),
    }
    binding = {
        "claim_id": "claim-market-size",
        "claim_status": "supported",
        "assertion_kind": "fact",
        "report_section": "1. Direct Answer",
        "report_span": report_span,
        "evidence_refs": [reference],
        "numeric_checks": [
            {
                "reported_value": "100",
                "mode": "direct",
                "evidence_values": ["100"],
                "unit": "billion",
                "currency": "USD",
                "reporting_period": "2025",
                "review_note": "Direct value and scope match.",
            }
        ],
        "numeric_exclusions": [
            {"value": "2025", "reason": "date", "review_note": "This token identifies the reporting period."}
        ],
        "verification_notes": "Single primary source limitation remains visible.",
        "manual_review_required": False,
    }
    write_json(
        run_dir / "report-claims.json",
        {
            "schema_version": "v64",
            "run_id": run_id,
            "report_path": f"reports/{run_id}.md",
            "claims": [binding],
        },
    )
    (run_dir / "truthfulness-audit.md").write_text(
        "# Truthfulness Audit\n\n"
        "- reviewer_type: agent-self-check\n"
        "- reviewed_claim_ids: claim-market-size\n\n"
        "## claim-market-size\n\n"
        "- atomicity: One verifiable market-value statement.\n"
        "- evidence_relation: The primary Evidence supports the Claim.\n"
        "- report_fidelity: The report span preserves the Evidence scope.\n"
        "- numeric_scope: The value and reporting period were checked.\n"
        "- inference_limits: No inference extends beyond the Evidence.\n"
        "- counterevidence: No material counterevidence was obtained.\n",
        encoding="utf-8",
    )
    return run_dir, report_path


def run_self_test(json_output: bool = False) -> int:
    """
    运行 v64 确定性 self-test.

    :param json_output: 是否输出 JSON.
    :return: 退出码, 0 表示通过, 1 表示失败.
    """
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        run_dir, report_path = build_valid_self_test(root)
        valid = final_check(run_dir, report_path, root)
        if valid.errors:
            failures.append("valid_final")
        evidence_path = run_dir / "evidence.jsonl"
        original_evidence = evidence_path.read_text(encoding="utf-8")
        evidence_path.write_text("", encoding="utf-8")
        if not pre_report_check(run_dir).errors:
            failures.append("orphaned_claim")
        evidence_path.write_text(original_evidence, encoding="utf-8")
        report_claims_path = run_dir / "report-claims.json"
        report_claims = read_json(report_claims_path)
        report_claims["claims"][0]["numeric_checks"][0]["reported_value"] = "101"
        write_json(report_claims_path, report_claims)
        if not final_check(run_dir, report_path, root).errors:
            failures.append("incorrect_direct_number")
        report_claims["claims"][0]["numeric_checks"][0]["reported_value"] = "100"
        report_claims["claims"][0]["report_span"] = "missing span 100"
        write_json(report_claims_path, report_claims)
        if not final_check(run_dir, report_path, root).errors:
            failures.append("missing_report_span")
    status = "fail" if failures else "pass"
    if json_output:
        print(json.dumps({"status": status, "failures": failures}, ensure_ascii=False, indent=2))
    elif failures:
        print("SELF TEST FAIL")
        for failure in failures:
            print(f"- {failure}")
    else:
        print("SELF TEST PASS")
    return 1 if failures else 0


def build_parser() -> argparse.ArgumentParser:
    """
    构建命令行解析器.

    :return: argparse 解析器.
    """
    parser = argparse.ArgumentParser(description="Check v64 Claim admission and report fidelity contracts.")
    parser.add_argument("--stage", choices=("pre-report", "final"), help="Validation stage.")
    parser.add_argument("--run-dir", type=Path, help="Research Run directory.")
    parser.add_argument("--report", type=Path, help="Report path for final validation.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in deterministic tests.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser


def print_result(result: CheckResult, json_output: bool) -> None:
    """
    输出 Checker 结果.

    :param result: Checker 结果.
    :param json_output: 是否输出 JSON.
    :return: None.
    """
    status = "fail" if result.errors else "pass"
    if json_output:
        print(
            json.dumps(
                {"status": status, "errors": result.errors, "warnings": result.warnings, "claims": result.claims},
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    print("PASS" if not result.errors else "FAIL")
    for error in result.errors:
        print(f"ERROR: {error}")
    for warning in result.warnings:
        print(f"WARNING: {warning}")
    for claim in result.claims:
        print(f"CLAIM: {claim['claim_id']} {claim['status']} {claim['qualifying_evidence_count']}")


def main() -> int:
    """
    执行命令行入口.

    :return: 进程退出码.
    """
    args = build_parser().parse_args()
    if args.self_test:
        return run_self_test(args.json)
    if args.stage is None or args.run_dir is None:
        print("--stage and --run-dir are required unless --self-test is used", file=sys.stderr)
        return 2
    if args.stage == "final" and args.report is None:
        print("--report is required for final validation", file=sys.stderr)
        return 2
    if args.stage == "pre-report":
        result = pre_report_check(args.run_dir)
    else:
        result = final_check(args.run_dir, args.report, args.repo_root)
    print_result(result, args.json)
    return 1 if result.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
