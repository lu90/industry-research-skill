"""
校验来源注册表和 Evidence Ledger 契约.

本脚本只检查 v61 固定字段, 枚举, 标识唯一性, 访问状态和来源独立性.
它不执行搜索, 页面访问或事实真伪判断.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REGISTRY_FILES = [
    "source-registry-official-and-industry.md",
    "source-registry-company-and-market.md",
    "source-registry-research-and-technology.md",
]

SOURCE_REQUIRED_FIELDS = {
    "source_id",
    "name",
    "publisher_type",
    "evidence_tier",
    "geography",
    "industries",
    "claim_types",
    "documents",
    "access_mode",
    "access_status",
    "update_frequency",
    "canonical_entry",
    "fallback_sources",
    "definition_risks",
    "independence_notes",
    "registry_status",
    "last_reviewed",
}

EVIDENCE_REQUIRED_FIELDS = {
    "run_id",
    "claim_id",
    "source_id",
    "registry_status",
    "document_title",
    "document_url",
    "publisher",
    "published_at",
    "accessed_at",
    "reporting_period",
    "geography",
    "unit_and_currency",
    "definition",
    "page_or_section",
    "evidence_span",
    "relation",
    "evidence_tier",
    "access_status",
    "origin_source_id",
    "independence_status",
    "contradiction_group",
    "confidence",
}

ENUMS = {
    "evidence_tier": {"primary", "near-primary", "secondary", "weak"},
    "source_access_status": {"public", "login-required", "paid-database", "API-key-required"},
    "evidence_access_status": {
        "obtained",
        "public-but-technical-failure",
        "login-required",
        "paid-database",
        "API-key-required",
        "blocked",
        "not-found",
        "definition-mismatch",
    },
    "registry_status": {"registered", "unregistered"},
    "relation": {"support", "refute", "neutral"},
    "independence_status": {
        "independently_verified",
        "same-origin-cross-check",
        "single-source-primary",
        "secondary-only",
        "unresolved-conflict",
    },
    "confidence": {"high", "medium", "low"},
}

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SOURCE_BLOCK_PATTERN = re.compile(
    r"<!-- source-registry:start -->\s*```json\s*(.*?)\s*```\s*<!-- source-registry:end -->",
    re.DOTALL,
)


def read_text(path: Path) -> str:
    """
    读取 UTF-8 文本.

    :param path: 文件路径.
    :return: 文件文本.
    """
    return path.read_text(encoding="utf-8")


def load_registry(path: Path) -> list[dict[str, Any]]:
    """
    从 Markdown 注册表读取 JSON 记录块.

    :param path: 注册表 Markdown 路径.
    :return: 来源记录列表.
    """
    text = read_text(path)
    match = SOURCE_BLOCK_PATTERN.search(text)
    if not match:
        raise ValueError("missing source registry JSON block")
    records = json.loads(match.group(1))
    if not isinstance(records, list):
        raise ValueError("source registry JSON block must be a list")
    return records


def load_evidence_jsonl(path: Path) -> list[dict[str, Any]]:
    """
    读取 Evidence Ledger JSONL.

    :param path: Evidence Ledger 路径.
    :return: Evidence 记录列表.
    """
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(read_text(path).splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"line {line_number}: invalid JSON: {exc.msg}") from exc
        if not isinstance(record, dict):
            raise ValueError(f"line {line_number}: evidence record must be an object")
        records.append(record)
    return records


def missing_fields(record: dict[str, Any], required: set[str]) -> list[str]:
    """
    返回记录缺少的必填字段.

    :param record: 待检查记录.
    :param required: 必填字段集合.
    :return: 按名称排序的缺失字段.
    """
    return sorted(required - set(record))


def validate_source_record(record: dict[str, Any], location: str) -> list[str]:
    """
    校验单条 Source record.

    :param record: 来源记录.
    :param location: 错误位置标签.
    :return: 错误列表.
    """
    errors: list[str] = []
    missing = missing_fields(record, SOURCE_REQUIRED_FIELDS)
    if missing:
        errors.append(f"{location}: missing fields: {', '.join(missing)}")
        return errors

    source_id = record["source_id"]
    if not isinstance(source_id, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", source_id):
        errors.append(f"{location}: invalid source_id")
    if record["evidence_tier"] not in ENUMS["evidence_tier"]:
        errors.append(f"{location}: invalid evidence_tier")
    if record["access_status"] not in ENUMS["source_access_status"]:
        errors.append(f"{location}: invalid access_status")
    if record["registry_status"] != "registered":
        errors.append(f"{location}: registry record must use registry_status registered")
    if not isinstance(record["canonical_entry"], str) or not re.match(r"^https?://", record["canonical_entry"]):
        errors.append(f"{location}: canonical_entry must be an HTTP URL")
    if not DATE_PATTERN.fullmatch(str(record["last_reviewed"])):
        errors.append(f"{location}: last_reviewed must use YYYY-MM-DD")
    for field in ("industries", "claim_types", "documents", "access_mode", "fallback_sources"):
        if not isinstance(record[field], list):
            errors.append(f"{location}: {field} must be a list")
    return errors


def validate_registries(registries: list[tuple[str, list[dict[str, Any]]]]) -> list[str]:
    """
    校验多份注册表并检查 source_id 全局唯一性.

    :param registries: 文件标签和来源记录列表.
    :return: 错误列表.
    """
    errors: list[str] = []
    seen: dict[str, str] = {}
    for label, records in registries:
        if not records:
            errors.append(f"{label}: registry must contain at least one record")
        for index, record in enumerate(records, start=1):
            location = f"{label}[{index}]"
            if not isinstance(record, dict):
                errors.append(f"{location}: source record must be an object")
                continue
            errors.extend(validate_source_record(record, location))
            source_id = record.get("source_id")
            if isinstance(source_id, str):
                if source_id in seen:
                    errors.append(f"{location}: duplicate source_id also used in {seen[source_id]}")
                else:
                    seen[source_id] = location
    return errors


def validate_evidence_record(record: dict[str, Any], location: str) -> list[str]:
    """
    校验单条 Evidence record.

    :param record: Evidence 记录.
    :param location: 错误位置标签.
    :return: 错误列表.
    """
    errors: list[str] = []
    missing = missing_fields(record, EVIDENCE_REQUIRED_FIELDS)
    if missing:
        errors.append(f"{location}: missing fields: {', '.join(missing)}")
        return errors

    enum_fields = {
        "registry_status": "registry_status",
        "relation": "relation",
        "evidence_tier": "evidence_tier",
        "access_status": "evidence_access_status",
        "independence_status": "independence_status",
        "confidence": "confidence",
    }
    for field, enum_name in enum_fields.items():
        if record[field] not in ENUMS[enum_name]:
            errors.append(f"{location}: invalid {field}")

    if not re.fullmatch(r"claim-[a-z0-9]+(?:-[a-z0-9]+)*", str(record["claim_id"])):
        errors.append(f"{location}: invalid claim_id")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", str(record["source_id"])):
        errors.append(f"{location}: invalid source_id")
    if record["registry_status"] == "unregistered" and not str(record["source_id"]).startswith("temp-"):
        errors.append(f"{location}: unregistered source_id must start with temp-")
    if record["access_status"] == "obtained":
        if not record["document_url"] or not record["evidence_span"] or not record["page_or_section"]:
            errors.append(f"{location}: obtained evidence requires URL, span, and page_or_section")
    elif record["evidence_span"] or record["relation"] != "neutral":
        errors.append(f"{location}: unavailable evidence must use an empty span and neutral relation")
    if not DATE_PATTERN.fullmatch(str(record["accessed_at"])):
        errors.append(f"{location}: accessed_at must use YYYY-MM-DD")
    return errors


def validate_independence(records: list[dict[str, Any]]) -> list[str]:
    """
    按 claim_id 校验独立双验状态和原始来源数量.

    :param records: Evidence 记录列表.
    :return: 错误列表.
    """
    errors: list[str] = []
    claims: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        claim_id = record.get("claim_id")
        if isinstance(claim_id, str):
            claims.setdefault(claim_id, []).append(record)

    for claim_id, claim_records in claims.items():
        obtained = [record for record in claim_records if record.get("access_status") == "obtained"]
        statuses = {record.get("independence_status") for record in obtained}
        origins = {record.get("origin_source_id") for record in obtained if record.get("origin_source_id")}
        if len(statuses) > 1:
            errors.append(f"{claim_id}: obtained records must use one consistent independence_status")
        if "independently_verified" in statuses and len(origins) < 2:
            errors.append(f"{claim_id}: independently_verified requires two distinct origin_source_id values")
        if "same-origin-cross-check" in statuses and len(origins) != 1:
            errors.append(f"{claim_id}: same-origin-cross-check requires one origin_source_id")
        if "single-source-primary" in statuses and len(origins) != 1:
            errors.append(f"{claim_id}: single-source-primary requires one origin_source_id")
        if "secondary-only" in statuses and any(
            record.get("evidence_tier") in {"primary", "near-primary"} for record in obtained
        ):
            errors.append(f"{claim_id}: secondary-only cannot include primary or near-primary evidence")
        if "unresolved-conflict" in statuses and any(not record.get("contradiction_group") for record in obtained):
            errors.append(f"{claim_id}: unresolved-conflict requires contradiction_group on every obtained record")
    return errors


def validate_evidence(records: list[dict[str, Any]]) -> list[str]:
    """
    校验 Evidence Ledger 全部记录.

    :param records: Evidence 记录列表.
    :return: 错误列表.
    """
    errors: list[str] = []
    for index, record in enumerate(records, start=1):
        errors.extend(validate_evidence_record(record, f"evidence[{index}]"))
    errors.extend(validate_independence(records))
    return errors


def validate_registry_links(records: list[dict[str, Any]], registered_ids: set[str]) -> list[str]:
    """
    校验 Evidence 的 registry_status 和注册表实际成员关系.

    :param records: Evidence 记录列表.
    :param registered_ids: 三份注册表中的 source_id 集合.
    :return: 错误列表.
    """
    errors: list[str] = []
    for index, record in enumerate(records, start=1):
        source_id = record.get("source_id")
        registry_status = record.get("registry_status")
        if registry_status == "registered" and source_id not in registered_ids:
            errors.append(f"evidence[{index}]: registered source_id is absent from registries")
        if registry_status == "unregistered" and source_id in registered_ids:
            errors.append(f"evidence[{index}]: registered source_id cannot use registry_status unregistered")
    return errors


def sample_source(source_id: str = "global-example") -> dict[str, Any]:
    """
    构造自检用 Source record.

    :param source_id: 来源标识.
    :return: 有效 Source record.
    """
    return {
        "source_id": source_id,
        "name": "Example Statistics Office",
        "publisher_type": "official-statistics",
        "evidence_tier": "primary",
        "geography": ["global"],
        "industries": ["cross-industry"],
        "claim_types": ["market-size"],
        "documents": ["dataset"],
        "access_mode": ["web"],
        "access_status": "public",
        "update_frequency": "annual",
        "canonical_entry": "https://example.org/data",
        "fallback_sources": ["national-statistics"],
        "definition_risks": "Check reporting period and constant prices.",
        "independence_notes": "May reuse national submissions.",
        "registry_status": "registered",
        "last_reviewed": "2026-07-15",
    }


def sample_evidence(
    source_id: str,
    origin_source_id: str,
    independence_status: str,
    registry_status: str = "registered",
) -> dict[str, Any]:
    """
    构造自检用 Evidence record.

    :param source_id: 来源标识.
    :param origin_source_id: 原始数据生成主体标识.
    :param independence_status: 独立验证状态.
    :param registry_status: 注册状态.
    :return: 有效 Evidence record.
    """
    return {
        "run_id": "run-20260715-example",
        "claim_id": "claim-market-size",
        "source_id": source_id,
        "registry_status": registry_status,
        "document_title": "Example Dataset",
        "document_url": "https://example.org/data",
        "publisher": "Example Publisher",
        "published_at": "2026-06-30",
        "accessed_at": "2026-07-15",
        "reporting_period": "2025",
        "geography": "global",
        "unit_and_currency": "USD billion",
        "definition": "Annual nominal market value.",
        "page_or_section": "Table 1",
        "evidence_span": "2025 market value: 100.",
        "relation": "support",
        "evidence_tier": "primary",
        "access_status": "obtained",
        "origin_source_id": origin_source_id,
        "independence_status": independence_status,
        "contradiction_group": "",
        "confidence": "high",
    }


def run_self_test(json_output: bool = False) -> int:
    """
    运行内置确定性契约测试.

    :param json_output: 是否输出 JSON.
    :return: 退出码, 0 表示通过, 1 表示失败.
    """
    valid_sources = [("registry-a", [sample_source("global-example")])]
    duplicate_sources = [
        ("registry-a", [sample_source("global-example")]),
        ("registry-b", [sample_source("global-example")]),
    ]
    valid_evidence = [
        sample_evidence("global-example", "origin-a", "independently_verified"),
        sample_evidence("global-example-2", "origin-b", "independently_verified"),
    ]
    same_origin = [
        sample_evidence("media-a", "origin-a", "independently_verified"),
        sample_evidence("media-b", "origin-a", "independently_verified"),
    ]
    honest_same_origin = [
        sample_evidence("media-a", "origin-a", "same-origin-cross-check"),
        sample_evidence("media-b", "origin-a", "same-origin-cross-check"),
    ]
    unregistered = sample_evidence(
        "temp-local-regulator",
        "origin-local-regulator",
        "single-source-primary",
        registry_status="unregistered",
    )
    inaccessible = sample_evidence("paid-example", "origin-paid", "single-source-primary")
    inaccessible.update({"access_status": "paid-database", "evidence_span": "", "relation": "neutral"})
    invalid_access = dict(inaccessible)
    invalid_access["evidence_span"] = "Unseen paid content."
    unknown_registered = sample_evidence("global-unknown", "origin-unknown", "single-source-primary")

    cases = [
        ("valid_registry", validate_registries(valid_sources), False),
        ("duplicate_source_id", validate_registries(duplicate_sources), True),
        ("valid_evidence", validate_evidence(valid_evidence), False),
        ("same_origin_false_independence", validate_evidence(same_origin), True),
        ("honest_same_origin", validate_evidence(honest_same_origin), False),
        ("valid_unregistered_source", validate_evidence([unregistered]), False),
        (
            "valid_registry_link",
            validate_registry_links(valid_evidence, {"global-example", "global-example-2"}),
            False,
        ),
        (
            "unknown_registered_source",
            validate_registry_links([unknown_registered], {"global-example"}),
            True,
        ),
        ("honest_inaccessible", validate_evidence([inaccessible]), False),
        ("dishonest_inaccessible", validate_evidence([invalid_access]), True),
    ]
    failures = [name for name, errors, should_fail in cases if bool(errors) != should_fail]
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


def validate_repository(skill_root: Path, evidence_path: Path | None = None) -> list[str]:
    """
    校验 Skill 中的三份注册表和可选 Evidence Ledger.

    :param skill_root: industry-research Skill 根目录.
    :param evidence_path: 可选 Evidence Ledger JSONL 路径.
    :return: 错误列表.
    """
    errors: list[str] = []
    registries: list[tuple[str, list[dict[str, Any]]]] = []
    for file_name in REGISTRY_FILES:
        path = skill_root / "references" / file_name
        if not path.exists():
            errors.append(f"missing registry: {path}")
            continue
        try:
            registries.append((file_name, load_registry(path)))
        except (ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{file_name}: {exc}")
    errors.extend(validate_registries(registries))
    registered_ids = {
        record["source_id"]
        for _, records in registries
        for record in records
        if isinstance(record, dict) and isinstance(record.get("source_id"), str)
    }

    if evidence_path:
        try:
            records = load_evidence_jsonl(evidence_path)
        except ValueError as exc:
            errors.append(str(exc))
        else:
            errors.extend(validate_evidence(records))
            errors.extend(validate_registry_links(records, registered_ids))
    return errors


def build_parser() -> argparse.ArgumentParser:
    """
    构建命令行解析器.

    :return: argparse 解析器.
    """
    parser = argparse.ArgumentParser(description="Check v61 source registry and evidence contracts.")
    parser.add_argument(
        "skill_root",
        type=Path,
        nargs="?",
        default=Path(__file__).resolve().parent.parent,
        help="Industry research skill root. Defaults to the installed script parent.",
    )
    parser.add_argument("--evidence", type=Path, help="Optional Evidence Ledger JSONL path.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract tests.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser


def main() -> int:
    """
    执行命令行入口.

    :return: 退出码, 0 表示通过, 1 表示失败.
    """
    parser = build_parser()
    args = parser.parse_args()
    if args.self_test:
        return run_self_test(args.json)
    errors = validate_repository(args.skill_root, args.evidence)
    status = "fail" if errors else "pass"
    if args.json:
        print(json.dumps({"status": status, "errors": errors}, ensure_ascii=False, indent=2))
    elif errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
    else:
        print("PASS")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
