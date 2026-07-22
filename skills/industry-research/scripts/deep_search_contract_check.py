#!/usr/bin/env python3
"""
校验 v62 Deep Search Protocol 和 Research Run 工件合同.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from source_contract_check import load_evidence_jsonl, validate_evidence


RUN_STATUSES = {"running", "completed", "incomplete"}
STOP_REASONS = {
    "evidence_sufficient",
    "information_saturated",
    "budget_exhausted",
    "access_blocked",
    "tool_error",
    "user_stopped",
}
REPORT_STATUSES = {"not_generated", "generated", "superseded"}
ROUTE_STAGES = {"registered_canonical", "registered_fallback", "open_discovery"}
ACTION_STATUSES = {"completed", "failed", "blocked", "skipped_duplicate"}
TRACKING_PARAMETERS = {
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "ref",
    "ref_src",
}
MANIFEST_FIELDS = {
    "schema_version",
    "run_id",
    "status",
    "stop_reason",
    "question",
    "created_at",
    "completed_at",
    "parent_run_id",
    "supersedes",
    "controller_id",
    "worker_ids",
    "budgets",
    "usage",
    "budget_overrides",
    "engine_report_permission",
    "report_path",
    "report_status",
    "errors",
}
PLAN_FIELDS = {
    "schema_version",
    "run_id",
    "question",
    "boundary",
    "claims",
    "source_routes",
    "rounds",
    "worker_assignments",
}
CLAIM_FIELDS = {
    "claim_id",
    "claim_text",
    "claim_type",
    "geography",
    "time_range",
    "required_evidence_tier",
    "preferred_source_categories",
}
GAPS_FIELDS = {"schema_version", "run_id", "gaps", "contradictions"}
GAP_FIELDS = {
    "gap_id",
    "claim_id",
    "missing_item",
    "impact",
    "status",
    "attempted_actions",
    "unresolved_reason",
    "next_source_route",
}
WORKER_SUMMARY_FIELDS = {
    "schema_version",
    "run_id",
    "worker_id",
    "assignment",
    "attempted_queries",
    "visited_sources",
    "learnings",
    "remaining_gaps",
    "contradictions",
    "new_source_candidates",
    "usage",
    "stop_reason",
}
QUERY_FIELDS = {
    "attempt_id",
    "query",
    "normalized_query",
    "claim_ids",
    "gap_id",
    "route_stage",
    "derived_from_evidence_ids",
    "derived_from_learning_ids",
    "action_status",
    "retry_count",
    "result_count",
}
VISIT_FIELDS = {
    "visit_id",
    "locator",
    "canonical_url",
    "source_id",
    "claim_ids",
    "access_status",
    "document_key",
    "retry_count",
}
BUDGET_FIELDS = {"search_limit", "visit_limit", "retry_limit", "elapsed_minutes_limit"}
USAGE_FIELDS = {"search_count", "visit_count", "elapsed_minutes"}
DEFAULT_BUDGETS = {"search_limit": 60, "visit_limit": 120, "retry_limit": 2, "elapsed_minutes_limit": 30}
CHALLENGE_FIELDS = {
    "challenge_id",
    "reviewer_role",
    "target_claim_id",
    "target_section",
    "challenge",
    "materiality",
    "verification_method",
    "verification_required",
    "gap_id",
    "resolution",
    "evidence_refs",
    "verification_notes",
    "report_change",
    "confidence_action",
    "reviewer_status",
    "closed_by",
    "reviewer_note",
}
EVIDENCE_REF_FIELDS = {
    "source_id",
    "document_url",
    "page_or_section",
    "relation",
    "evidence_span_sha256",
}
REVIEWER_ROLES = {
    "industry-expert",
    "investment-researcher",
    "policy-regulatory",
    "operator-entrepreneur",
    "intern",
    "devils-advocate",
}
CORE_REVIEWER_ROLES = {
    "industry-expert",
    "investment-researcher",
    "policy-regulatory",
    "operator-entrepreneur",
}
REVIEW_MODES = {"multi-agent", "single-agent-simulated"}
MATERIALITIES = {"high", "medium", "low"}
VERIFICATION_METHODS = {"retrieval", "data-definition", "calculation", "logic", "scope", "scenario"}
RESOLUTIONS = {"pending", "confirmed", "partially_valid", "refuted", "unresolved", "out_of_scope"}
CONFIDENCE_ACTIONS = {"unchanged", "downgraded", "withdrawn", "not-applicable"}
REVIEWER_STATUSES = {"open", "closed", "disputed"}
CLOSED_BY_VALUES = {"original-reviewer", "organizer"}


def read_json(path: Path) -> dict[str, Any]:
    """
读取一个 UTF-8 JSON 对象.

    :param path: JSON 文件路径.
    :return: JSON 对象.
    """
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    return value


def missing_fields(record: dict[str, Any], required: set[str]) -> list[str]:
    """
返回对象缺少的字段.

    :param record: 待检查对象.
    :param required: 必需字段集合.
    :return: 已排序的缺失字段.
    """
    return sorted(required - set(record))


def normalize_query(query: str) -> str:
    """
规范 Query 以支持确定性去重.

    :param query: 原始 Query.
    :return: Unicode 规范化并折叠空白后的 Query.
    """
    normalized = unicodedata.normalize("NFKC", query).casefold()
    normalized = re.sub(r"[^\w\-./]+", " ", normalized, flags=re.UNICODE)
    return " ".join(normalized.split())


def normalize_url(url: str) -> str:
    """
规范 URL 并删除无意义追踪参数.

    :param url: 原始 HTTP 或 HTTPS URL.
    :return: 可用于去重的 canonical URL.
    """
    parts = urlsplit(url.strip())
    scheme = parts.scheme.casefold()
    host = (parts.hostname or "").casefold()
    port = parts.port
    if port and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        host = f"{host}:{port}"
    path = re.sub(r"/{2,}", "/", parts.path or "/")
    if path != "/":
        path = path.rstrip("/")
    query_items = []
    for key, value in parse_qsl(parts.query, keep_blank_values=True):
        lowered = key.casefold()
        if lowered.startswith("utm_") or lowered in TRACKING_PARAMETERS:
            continue
        query_items.append((key, value))
    return urlunsplit((scheme, host, path, urlencode(sorted(query_items)), ""))


def document_key(record: dict[str, Any]) -> str:
    """
生成文档级去重键.

    :param record: Evidence 或访问记录.
    :return: 内容哈希或文档元数据哈希.
    """
    content_hash = str(record.get("content_hash", "")).strip().casefold()
    if content_hash:
        return f"hash:{content_hash}"
    fields = [
        normalize_query(str(record.get("document_title", ""))),
        normalize_query(str(record.get("publisher", ""))),
        str(record.get("published_at", "")).strip(),
        normalize_query(str(record.get("document_series_id", ""))),
    ]
    if not any(fields):
        raw_url = str(record.get("document_url") or record.get("canonical_url") or "")
        fields.append(normalize_url(raw_url) if raw_url else "unknown")
    digest = hashlib.sha256("|".join(fields).encode("utf-8")).hexdigest()
    return f"meta:{digest}"


def source_independence_key(record: dict[str, Any]) -> str:
    """
返回来源独立性去重键.

    :param record: Evidence record.
    :return: 原始数据生成源标识.
    """
    return str(record.get("origin_source_id", "")).strip().casefold()


def normalize_evidence_span(value: object) -> str:
    """
    规范 Evidence 片段以计算稳定摘要.

    :param value: Evidence 片段值.
    :return: Unicode 规范化并折叠空白后的文本.
    """
    normalized = unicodedata.normalize("NFKC", str(value))
    return " ".join(normalized.split())


def evidence_span_sha256(record: dict[str, Any]) -> str:
    """
    计算 Evidence 片段的 SHA-256 定位摘要.

    :param record: Evidence record.
    :return: 小写十六进制 SHA-256.
    """
    span = normalize_evidence_span(record.get("evidence_span", ""))
    return hashlib.sha256(span.encode("utf-8")).hexdigest()


def validate_evidence_reference(
    reference: object,
    claim_id: str,
    evidence: list[dict[str, Any]],
    label: str,
) -> list[str]:
    """
    校验 Challenge Evidence 复合定位唯一命中同一 Claim.

    :param reference: 待校验的 Evidence reference.
    :param claim_id: Challenge 目标 Claim ID.
    :param evidence: 最终 Evidence Ledger records.
    :param label: 错误位置标签.
    :return: 错误列表.
    """
    if not isinstance(reference, dict):
        return [f"{label}: evidence reference must be an object"]
    missing = missing_fields(reference, EVIDENCE_REF_FIELDS)
    if missing:
        return [f"{label}: evidence reference missing fields: {', '.join(missing)}"]
    if set(reference) != EVIDENCE_REF_FIELDS:
        return [f"{label}: evidence reference has noncanonical fields"]
    if reference.get("relation") not in {"support", "refute"}:
        return [f"{label}: invalid evidence relation"]
    matches = [
        record
        for record in evidence
        if record.get("claim_id") == claim_id
        and record.get("access_status") == "obtained"
        and record.get("source_id") == reference.get("source_id")
        and record.get("document_url") == reference.get("document_url")
        and record.get("page_or_section") == reference.get("page_or_section")
        and record.get("relation") == reference.get("relation")
        and evidence_span_sha256(record) == reference.get("evidence_span_sha256")
    ]
    if len(matches) != 1:
        return [f"{label}: evidence reference must uniquely match one obtained same-Claim record"]
    return []


def validate_challenges(
    payload: dict[str, Any],
    run_id: str,
    claim_ids: set[str],
    gaps: dict[str, Any],
    evidence: list[dict[str, Any]],
    formal_report: bool,
) -> list[str]:
    """
    校验 v65 Challenge Ledger 和跨工件闭环门禁.

    :param payload: challenges.json 顶层对象.
    :param run_id: 预期 Run ID.
    :param claim_ids: Plan 中的 Claim ID.
    :param gaps: Gaps 工件.
    :param evidence: 最终 Evidence Ledger records.
    :param formal_report: 当前 Run 是否已登记正式报告.
    :return: 错误列表.
    """
    errors: list[str] = []
    if set(payload) != {"schema_version", "run_id", "review_mode", "challenges"}:
        errors.append("challenges: noncanonical top-level fields")
    if payload.get("schema_version") != "v65":
        errors.append("challenges: schema_version must be v65")
    if payload.get("run_id") != run_id:
        errors.append("challenges: run_id mismatch")
    if payload.get("review_mode") not in REVIEW_MODES:
        errors.append("challenges: invalid review_mode")
    challenges = payload.get("challenges")
    if not isinstance(challenges, list):
        return errors + ["challenges: challenges must be a list"]
    if formal_report and not challenges:
        errors.append("challenges: formal report requires non-empty Challenge Ledger")
    final_gaps = {
        str(gap.get("gap_id", "")): gap
        for gap in gaps.get("gaps", [])
        if isinstance(gap, dict)
    }
    seen_ids: set[str] = set()
    seen_roles: set[str] = set()
    for index, challenge in enumerate(challenges, start=1):
        label = f"challenges[{index}]"
        if not isinstance(challenge, dict):
            errors.append(f"{label}: must be an object")
            continue
        missing = missing_fields(challenge, CHALLENGE_FIELDS)
        if missing:
            errors.append(f"{label}: missing fields: {', '.join(missing)}")
            continue
        if set(challenge) != CHALLENGE_FIELDS:
            errors.append(f"{label}: noncanonical fields")
        challenge_id = str(challenge.get("challenge_id", ""))
        if not re.fullmatch(r"challenge-[a-z0-9]+(?:-[a-z0-9]+)*", challenge_id):
            errors.append(f"{label}: invalid challenge_id")
        if challenge_id in seen_ids:
            errors.append(f"{label}: duplicate challenge_id")
        seen_ids.add(challenge_id)
        role = challenge.get("reviewer_role")
        if role not in REVIEWER_ROLES:
            errors.append(f"{label}: invalid reviewer_role")
        else:
            seen_roles.add(str(role))
        claim_id = str(challenge.get("target_claim_id", ""))
        if claim_id not in claim_ids:
            errors.append(f"{label}: unknown target_claim_id")
        for field, allowed in (
            ("materiality", MATERIALITIES),
            ("verification_method", VERIFICATION_METHODS),
            ("resolution", RESOLUTIONS),
            ("confidence_action", CONFIDENCE_ACTIONS),
            ("reviewer_status", REVIEWER_STATUSES),
            ("closed_by", CLOSED_BY_VALUES),
        ):
            if challenge.get(field) not in allowed:
                errors.append(f"{label}: invalid {field}")
        for field in ("target_section", "challenge", "verification_required"):
            if not isinstance(challenge.get(field), str) or not challenge[field].strip():
                errors.append(f"{label}: {field} must be non-empty")
        method = challenge.get("verification_method")
        gap_id = challenge.get("gap_id")
        if method == "retrieval":
            gap = final_gaps.get(str(gap_id)) if isinstance(gap_id, str) else None
            if gap is None:
                errors.append(f"{label}: retrieval Challenge requires a known gap_id")
            elif gap.get("claim_id") != claim_id:
                errors.append(f"{label}: gap_id must reference the target Claim")
            else:
                gap_status = normalize_query(str(gap.get("status", "")))
                closed_gap_statuses = {"closed", "resolved", normalize_query("已补齐")}
                open_gap_statuses = {"open", "unresolved", "still open", normalize_query("仍未补齐")}
                if challenge.get("resolution") in {"confirmed", "refuted", "out_of_scope"} and gap_status in open_gap_statuses:
                    errors.append(f"{label}: retrieval resolution conflicts with open Gap status")
                if challenge.get("resolution") == "unresolved" and gap_status in closed_gap_statuses:
                    errors.append(f"{label}: unresolved retrieval Challenge conflicts with closed Gap status")
        elif gap_id is not None:
            errors.append(f"{label}: non-retrieval Challenge requires null gap_id")
        references = challenge.get("evidence_refs")
        if not isinstance(references, list):
            errors.append(f"{label}: evidence_refs must be a list")
            references = []
        for reference_index, reference in enumerate(references, start=1):
            errors.extend(
                validate_evidence_reference(
                    reference,
                    claim_id,
                    evidence,
                    f"{label}.evidence_refs[{reference_index}]",
                )
            )
        resolution = challenge.get("resolution")
        notes = str(challenge.get("verification_notes", "")).strip()
        report_change = str(challenge.get("report_change", "")).strip()
        reviewer_note = str(challenge.get("reviewer_note", "")).strip()
        if method == "retrieval" and resolution in {"confirmed", "partially_valid", "refuted"} and not references:
            errors.append(f"{label}: retrieval resolution requires an Evidence reference")
        if resolution != "pending" and not notes:
            errors.append(f"{label}: resolved Challenge requires verification_notes")
        if resolution != "pending" and not report_change:
            errors.append(f"{label}: resolution requires report_change")
        if resolution == "refuted" and not references and (method == "retrieval" or not notes):
            errors.append(f"{label}: refuted Challenge requires Evidence or non-retrieval review notes")
        if resolution == "unresolved" and challenge.get("confidence_action") not in {"downgraded", "withdrawn"}:
            errors.append(f"{label}: unresolved Challenge requires downgraded or withdrawn confidence")
        if challenge.get("reviewer_status") == "closed" and not reviewer_note:
            errors.append(f"{label}: closed Challenge requires reviewer_note")
        if challenge.get("materiality") == "high":
            if challenge.get("reviewer_status") == "closed" and challenge.get("closed_by") != "original-reviewer":
                errors.append(f"{label}: high Challenge must be closed by original reviewer")
            if formal_report and challenge.get("reviewer_status") in {"open", "disputed"}:
                errors.append(f"{label}: open or disputed high Challenge blocks formal report")
        if formal_report and resolution == "pending":
            errors.append(f"{label}: pending Challenge blocks formal report")
    if formal_report:
        missing_roles = sorted(CORE_REVIEWER_ROLES - seen_roles)
        if missing_roles:
            errors.append(f"challenges: formal report missing core reviewer roles: {', '.join(missing_roles)}")
    return errors


def validate_challenge_artifact_requirement(manifest: dict[str, Any], challenge_path: Path) -> list[str]:
    """
    校验正式报告是否存在 Challenge Ledger 工件.

    :param manifest: Run Manifest.
    :param challenge_path: challenges.json 路径.
    :return: 错误列表.
    """
    if manifest.get("report_status") == "generated" and not challenge_path.is_file():
        return ["missing artifact: challenges.json for generated formal report"]
    return []


def is_information_saturated(actions: list[dict[str, Any]]) -> bool:
    """
判断最近两个有效动作是否达到信息饱和.

    :param actions: 按时间排序的检索进展记录.
    :return: 是否满足连续两个无新增动作合同.
    """
    effective = [
        action
        for action in actions
        if action.get("effective") is True
        and action.get("action_status") == "completed"
        and action.get("duplicate") is not True
        and action.get("retry") is not True
    ]
    if len(effective) < 2:
        return False
    for action in effective[-2:]:
        if action.get("new_high_quality_evidence") is True:
            return False
        if action.get("claim_coverage_improved") is True:
            return False
        if action.get("new_high_impact_contradiction") is True:
            return False
    return True


def budget_exhausted(budgets: dict[str, Any], usage: dict[str, Any]) -> bool:
    """
判断 Run 是否达到任一安全预算.

    :param budgets: 当前生效预算.
    :param usage: 当前使用量.
    :return: 是否达到安全上限.
    """
    comparisons = (
        ("search_limit", "search_count"),
        ("visit_limit", "visit_count"),
        ("elapsed_minutes_limit", "elapsed_minutes"),
    )
    return any(float(usage[used]) >= float(budgets[limit]) for limit, used in comparisons)


def choose_stop_reason(
    engine_evidence_sufficient: bool,
    actions: list[dict[str, Any]],
    budgets: dict[str, Any],
    usage: dict[str, Any],
    all_material_routes_blocked: bool = False,
) -> str | None:
    """
按协议优先级选择停止原因.

    :param engine_evidence_sufficient: Engine 是否确认最低证据门槛已满足.
    :param actions: 检索进展记录.
    :param budgets: 当前生效预算.
    :param usage: 当前使用量.
    :param all_material_routes_blocked: 所有关键剩余路线是否受阻.
    :return: 停止原因或 None.
    """
    if engine_evidence_sufficient:
        return "evidence_sufficient"
    if is_information_saturated(actions):
        return "information_saturated"
    if budget_exhausted(budgets, usage):
        return "budget_exhausted"
    if all_material_routes_blocked:
        return "access_blocked"
    return None


def validate_budget_objects(manifest: dict[str, Any]) -> list[str]:
    """
校验预算和使用量对象.

    :param manifest: Run Manifest.
    :return: 错误列表.
    """
    errors: list[str] = []
    budgets = manifest.get("budgets")
    usage = manifest.get("usage")
    if not isinstance(budgets, dict) or missing_fields(budgets, BUDGET_FIELDS):
        errors.append("manifest: invalid budgets")
        return errors
    if not isinstance(usage, dict) or missing_fields(usage, USAGE_FIELDS):
        errors.append("manifest: invalid usage")
        return errors
    for field in BUDGET_FIELDS:
        if not isinstance(budgets[field], (int, float)) or budgets[field] < 0:
            errors.append(f"manifest: invalid budget {field}")
    for field in USAGE_FIELDS:
        if not isinstance(usage[field], (int, float)) or usage[field] < 0:
            errors.append(f"manifest: invalid usage {field}")
    overrides = manifest.get("budget_overrides")
    if not isinstance(overrides, dict):
        errors.append("manifest: budget_overrides must be an object")
    else:
        for field, default in DEFAULT_BUDGETS.items():
            if budgets[field] != default and field not in overrides:
                errors.append(f"manifest: unrecorded budget override {field}")
    return errors


def validate_manifest(manifest: dict[str, Any], run_dir: Path, repo_root: Path) -> list[str]:
    """
校验 Manifest 状态和报告关联.

    :param manifest: Manifest 对象.
    :param run_dir: Run 目录.
    :param repo_root: 仓库根目录.
    :return: 错误列表.
    """
    errors: list[str] = []
    missing = missing_fields(manifest, MANIFEST_FIELDS)
    if missing:
        return [f"manifest: missing fields: {', '.join(missing)}"]
    if manifest["run_id"] != run_dir.name:
        errors.append("manifest: run_id must match directory name")
    if manifest["status"] not in RUN_STATUSES:
        errors.append("manifest: invalid status")
    if manifest["report_status"] not in REPORT_STATUSES:
        errors.append("manifest: invalid report_status")
    if manifest["status"] == "running":
        if manifest["stop_reason"] is not None or manifest["completed_at"] is not None:
            errors.append("manifest: running Run cannot be stopped or completed")
    elif manifest["stop_reason"] not in STOP_REASONS or not manifest["completed_at"]:
        errors.append("manifest: finalized Run requires stop_reason and completed_at")
    if manifest["status"] == "incomplete":
        if manifest["engine_report_permission"] is not False:
            errors.append("manifest: incomplete Run requires denied Engine report permission")
        if manifest["report_path"] is not None or manifest["report_status"] != "not_generated":
            errors.append("manifest: incomplete Run cannot generate a formal report")
    if manifest["report_status"] == "generated":
        report_path = manifest["report_path"]
        if not isinstance(report_path, str) or not report_path.startswith("reports/"):
            errors.append("manifest: generated report must use a reports/ path")
        else:
            if Path(report_path).stem != manifest["run_id"]:
                errors.append("manifest: generated report filename stem must equal run_id")
            if not (repo_root / Path(report_path)).is_file():
                errors.append("manifest: report_path does not exist")
        if manifest["status"] != "completed":
            errors.append("manifest: generated report requires completed status")
        if manifest["engine_report_permission"] is not True:
            errors.append("manifest: generated report requires Engine permission")
    elif manifest["report_path"] is not None:
        errors.append("manifest: non-generated report requires null report_path")
    errors.extend(validate_budget_objects(manifest))
    return errors


def validate_plan(plan: dict[str, Any], run_id: str) -> list[str]:
    """
校验 Plan 和 v61 Claim 接口.

    :param plan: Plan 对象.
    :param run_id: 预期 Run ID.
    :return: 错误列表.
    """
    errors: list[str] = []
    missing = missing_fields(plan, PLAN_FIELDS)
    if missing:
        return [f"plan: missing fields: {', '.join(missing)}"]
    if plan["run_id"] != run_id:
        errors.append("plan: run_id mismatch")
    if not isinstance(plan["claims"], list) or not plan["claims"]:
        errors.append("plan: claims must be a non-empty list")
    else:
        seen: set[str] = set()
        for index, claim in enumerate(plan["claims"], start=1):
            if not isinstance(claim, dict):
                errors.append(f"plan.claims[{index}]: must be an object")
                continue
            missing_claim = missing_fields(claim, CLAIM_FIELDS)
            if missing_claim:
                errors.append(f"plan.claims[{index}]: missing fields: {', '.join(missing_claim)}")
            claim_id = str(claim.get("claim_id", ""))
            if not re.fullmatch(r"claim-[a-z0-9]+(?:-[a-z0-9]+)*", claim_id):
                errors.append(f"plan.claims[{index}]: invalid claim_id")
            if claim_id in seen:
                errors.append(f"plan.claims[{index}]: duplicate claim_id")
            seen.add(claim_id)
    return errors


def validate_gaps(gaps: dict[str, Any], run_id: str, claim_ids: set[str]) -> list[str]:
    """
校验 Gaps 工件.

    :param gaps: Gaps 对象.
    :param run_id: 预期 Run ID.
    :param claim_ids: Plan 中的 Claim ID.
    :return: 错误列表.
    """
    errors: list[str] = []
    missing = missing_fields(gaps, GAPS_FIELDS)
    if missing:
        return [f"gaps: missing fields: {', '.join(missing)}"]
    if gaps["run_id"] != run_id:
        errors.append("gaps: run_id mismatch")
    if not isinstance(gaps["gaps"], list) or not isinstance(gaps["contradictions"], list):
        return errors + ["gaps: gaps and contradictions must be lists"]
    seen: set[str] = set()
    for index, gap in enumerate(gaps["gaps"], start=1):
        if not isinstance(gap, dict):
            errors.append(f"gaps[{index}]: must be an object")
            continue
        missing_gap = missing_fields(gap, GAP_FIELDS)
        if missing_gap:
            errors.append(f"gaps[{index}]: missing fields: {', '.join(missing_gap)}")
        if gap.get("claim_id") not in claim_ids:
            errors.append(f"gaps[{index}]: unknown claim_id")
        gap_id = str(gap.get("gap_id", ""))
        if gap_id in seen:
            errors.append(f"gaps[{index}]: duplicate gap_id")
        seen.add(gap_id)
    return errors


def validate_worker_summary(summary: dict[str, Any], path: Path, run_id: str, retry_limit: int) -> list[str]:
    """
校验一个 Worker Summary 和递归 Query 追溯字段.

    :param summary: Worker Summary 对象.
    :param path: Summary 路径.
    :param run_id: 预期 Run ID.
    :param retry_limit: 当前生效的单动作重试上限.
    :return: 错误列表.
    """
    label = path.name
    errors: list[str] = []
    missing = missing_fields(summary, WORKER_SUMMARY_FIELDS)
    if missing:
        return [f"{label}: missing fields: {', '.join(missing)}"]
    if summary["run_id"] != run_id:
        errors.append(f"{label}: run_id mismatch")
    if summary["stop_reason"] is not None and summary["stop_reason"] not in STOP_REASONS:
        errors.append(f"{label}: invalid stop_reason")
    if not isinstance(summary["usage"], dict) or missing_fields(summary["usage"], USAGE_FIELDS):
        errors.append(f"{label}: invalid usage")
    seen_queries: set[str] = set()
    for index, attempt in enumerate(summary["attempted_queries"], start=1):
        if not isinstance(attempt, dict) or missing_fields(attempt, QUERY_FIELDS):
            errors.append(f"{label}.attempted_queries[{index}]: invalid fields")
            continue
        normalized = normalize_query(str(attempt["query"]))
        if attempt["normalized_query"] != normalized:
            errors.append(f"{label}.attempted_queries[{index}]: normalized_query mismatch")
        if attempt["route_stage"] not in ROUTE_STAGES:
            errors.append(f"{label}.attempted_queries[{index}]: invalid route_stage")
        if attempt["action_status"] not in ACTION_STATUSES:
            errors.append(f"{label}.attempted_queries[{index}]: invalid action_status")
        if attempt["retry_count"] > retry_limit:
            errors.append(f"{label}.attempted_queries[{index}]: retry_count exceeds limit")
        is_follow_up = bool(attempt["gap_id"])
        derived = attempt["derived_from_evidence_ids"] or attempt["derived_from_learning_ids"]
        if is_follow_up and (not attempt["claim_ids"] or not derived):
            errors.append(f"{label}.attempted_queries[{index}]: untraceable follow-up query")
        if normalized in seen_queries and attempt["action_status"] != "skipped_duplicate":
            errors.append(f"{label}.attempted_queries[{index}]: duplicate query was executed")
        seen_queries.add(normalized)
    seen_urls: set[str] = set()
    seen_documents: set[str] = set()
    for index, visit in enumerate(summary["visited_sources"], start=1):
        if not isinstance(visit, dict) or missing_fields(visit, VISIT_FIELDS):
            errors.append(f"{label}.visited_sources[{index}]: invalid fields")
            continue
        expected_url = normalize_url(str(visit["locator"])) if str(visit["locator"]).startswith("http") else ""
        if expected_url and visit["canonical_url"] != expected_url:
            errors.append(f"{label}.visited_sources[{index}]: canonical_url mismatch")
        if visit["document_key"] in seen_documents:
            errors.append(f"{label}.visited_sources[{index}]: duplicate document visit")
        seen_documents.add(visit["document_key"])
        if visit["canonical_url"] in seen_urls:
            errors.append(f"{label}.visited_sources[{index}]: duplicate URL visit")
        seen_urls.add(visit["canonical_url"])
    return errors


def evidence_score(record: dict[str, Any]) -> tuple[int, int, int]:
    """
计算重复 Evidence 的保留优先级.

    :param record: Evidence record.
    :return: 取得状态, 元数据完整度和片段长度组成的排序键.
    """
    obtained = int(record.get("access_status") == "obtained")
    completeness = sum(value not in (None, "", "unknown") for value in record.values())
    span_length = len(str(record.get("evidence_span", "")))
    return obtained, completeness, span_length


def merge_worker_evidence(run_dir: Path) -> list[dict[str, Any]]:
    """
由 Controller 规则合并 Worker Evidence 文件.

    :param run_dir: Research Run 目录.
    :return: 去重后的 Evidence records.
    """
    selected: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for path in sorted((run_dir / "workers").glob("*-evidence.jsonl")):
        for record in load_evidence_jsonl(path):
            key = (
                str(record.get("claim_id", "")),
                document_key(record),
                str(record.get("relation", "")),
                str(record.get("contradiction_group", "")),
            )
            current = selected.get(key)
            if current is None or evidence_score(record) > evidence_score(current):
                selected[key] = record
    return [selected[key] for key in sorted(selected)]


def write_evidence_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    """
原子写入 Controller 最终 Evidence Ledger.

    :param path: 最终 JSONL 路径.
    :param records: 已合并 Evidence records.
    :return: None.
    """
    temporary = path.with_suffix(path.suffix + ".tmp")
    payload = "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records)
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(path)


def validate_authority_boundary(engine_text: str, protocol_text: str) -> list[str]:
    """
校验 Engine 和 Protocol 的职责边界声明.

    :param engine_text: Engine 文本.
    :param protocol_text: Protocol 文本.
    :return: 错误列表.
    """
    errors: list[str] = []
    engine_required = [
        ("owns evidence admission", "负责证据准入"),
        ("three-round gap-closure decision", "三轮缺口闭环决策"),
        ("minimum evidence threshold and formal-report permission", "最低证据门槛和正式报告许可"),
    ]
    protocol_required = [
        ("Engine remains the authority for research policy", "Engine 始终负责研究政策"),
        ("must not redefine the Engine's evidence threshold", "不得重新定义 Engine 的证据门槛"),
        (
            "Only the Engine decides whether the minimum evidence threshold is satisfied",
            "只有 Engine 可以判断最低证据门槛是否满足",
        ),
    ]
    for english_phrase, chinese_phrase in engine_required:
        if english_phrase not in engine_text and chinese_phrase not in engine_text:
            errors.append(f"engine boundary missing: {english_phrase}")
    for english_phrase, chinese_phrase in protocol_required:
        if english_phrase not in protocol_text and chinese_phrase not in protocol_text:
            errors.append(f"protocol boundary missing: {english_phrase}")
    forbidden = [
        "Protocol decides minimum evidence",
        "Protocol authorizes closure round",
        "Protocol 决定最低证据",
        "Protocol 授权闭环轮次",
    ]
    for phrase in forbidden:
        if phrase in protocol_text:
            errors.append(f"protocol duplicates Engine policy: {phrase}")
    return errors


def validate_run_index(manifests: list[tuple[str, dict[str, Any]]]) -> list[str]:
    """
校验跨 Run 的 ID 和正式报告关联唯一性.

    :param manifests: 路径标签和 Manifest 对象列表.
    :return: 错误列表.
    """
    errors: list[str] = []
    run_ids: dict[str, str] = {}
    report_paths: dict[str, str] = {}
    for label, manifest in manifests:
        run_id = str(manifest.get("run_id", ""))
        if run_id in run_ids:
            errors.append(f"{label}: duplicate run_id also used in {run_ids[run_id]}")
        else:
            run_ids[run_id] = label
        report_path = manifest.get("report_path")
        if manifest.get("report_status") == "generated" and isinstance(report_path, str):
            if report_path in report_paths:
                errors.append(f"{label}: report_path also owned by {report_paths[report_path]}")
            else:
                report_paths[report_path] = label
    return errors


def validate_research_root(research_root: Path) -> list[str]:
    """
校验 Research Run 根目录中的跨 Run 合同.

    :param research_root: Research Run 根目录.
    :return: 错误列表.
    """
    errors: list[str] = []
    manifests: list[tuple[str, dict[str, Any]]] = []
    for path in sorted(research_root.glob("*/manifest.json")):
        try:
            manifests.append((str(path), read_json(path)))
        except (ValueError, json.JSONDecodeError) as exc:
            errors.append(str(exc))
    errors.extend(validate_run_index(manifests))
    return errors


def validate_run_bundle(run_dir: Path, repo_root: Path) -> list[str]:
    """
校验一个完整 Research Run Bundle.

    :param run_dir: Research Run 目录.
    :param repo_root: 仓库根目录.
    :return: 错误列表.
    """
    errors: list[str] = []
    required_paths = ["manifest.json", "plan.json", "evidence.jsonl", "gaps.json", "run-summary.md", "workers"]
    for relative in required_paths:
        if not (run_dir / relative).exists():
            errors.append(f"missing artifact: {relative}")
    if errors:
        return errors
    try:
        manifest = read_json(run_dir / "manifest.json")
        plan = read_json(run_dir / "plan.json")
        gaps = read_json(run_dir / "gaps.json")
        evidence = load_evidence_jsonl(run_dir / "evidence.jsonl")
    except (ValueError, json.JSONDecodeError) as exc:
        return [str(exc)]
    errors.extend(validate_manifest(manifest, run_dir, repo_root))
    errors.extend(validate_plan(plan, run_dir.name))
    claim_ids = {str(claim.get("claim_id")) for claim in plan.get("claims", []) if isinstance(claim, dict)}
    errors.extend(validate_gaps(gaps, run_dir.name, claim_ids))
    errors.extend(validate_evidence(evidence))
    challenge_path = run_dir / "challenges.json"
    formal_report = manifest.get("report_status") == "generated"
    errors.extend(validate_challenge_artifact_requirement(manifest, challenge_path))
    if challenge_path.is_file():
        try:
            challenges = read_json(challenge_path)
        except (ValueError, json.JSONDecodeError) as exc:
            errors.append(str(exc))
        else:
            errors.extend(
                validate_challenges(
                    challenges,
                    run_dir.name,
                    claim_ids,
                    gaps,
                    evidence,
                    formal_report,
                )
            )
    worker_paths = sorted((run_dir / "workers").glob("*-summary.json"))
    evidence_paths = sorted((run_dir / "workers").glob("*-evidence.jsonl"))
    if not worker_paths or not evidence_paths:
        errors.append("workers: at least one Summary and Evidence file are required")
    worker_usage = {"search_count": 0, "visit_count": 0, "elapsed_minutes": 0}
    for path in worker_paths:
        try:
            summary = read_json(path)
        except (ValueError, json.JSONDecodeError) as exc:
            errors.append(str(exc))
        else:
            retry_limit = int(manifest.get("budgets", {}).get("retry_limit", 2))
            errors.extend(validate_worker_summary(summary, path, run_dir.name, retry_limit))
            usage = summary.get("usage", {})
            if isinstance(usage, dict):
                worker_usage["search_count"] += usage.get("search_count", 0)
                worker_usage["visit_count"] += usage.get("visit_count", 0)
                worker_usage["elapsed_minutes"] = max(worker_usage["elapsed_minutes"], usage.get("elapsed_minutes", 0))
    manifest_usage = manifest.get("usage", {})
    for field in ("search_count", "visit_count"):
        if manifest_usage.get(field) != worker_usage[field]:
            errors.append(f"manifest: {field} does not match Worker summaries")
    if manifest_usage.get("elapsed_minutes", 0) < worker_usage["elapsed_minutes"]:
        errors.append("manifest: elapsed_minutes is below a Worker summary")
    merged = merge_worker_evidence(run_dir)
    if evidence != merged:
        errors.append("evidence.jsonl: content does not match deterministic Controller merge")
    if manifest.get("status") == "completed" and not evidence:
        errors.append("manifest: completed Run requires Evidence")
    return errors


def sample_evidence(run_id: str = "run-v62-test") -> dict[str, Any]:
    """
构造自检使用的 Evidence record.

    :param run_id: Run ID.
    :return: 有效 Evidence record.
    """
    return {
        "run_id": run_id,
        "claim_id": "claim-market-size",
        "source_id": "example-office",
        "registry_status": "registered",
        "document_title": "Example Dataset",
        "document_url": "https://example.org/data?utm_source=test",
        "publisher": "Example Office",
        "published_at": "2026-06-30",
        "accessed_at": "2026-07-16",
        "reporting_period": "2025",
        "geography": "global",
        "unit_and_currency": "USD billion",
        "definition": "Annual nominal value.",
        "page_or_section": "Table 1",
        "evidence_span": "The value was 100.",
        "relation": "support",
        "evidence_tier": "primary",
        "access_status": "obtained",
        "origin_source_id": "origin-example-office",
        "independence_status": "single-source-primary",
        "contradiction_group": "",
        "confidence": "high",
    }


def run_self_test(json_output: bool = False) -> int:
    """
运行确定性协议契约测试.

    :param json_output: 是否输出 JSON.
    :return: 退出码, 0 表示通过, 1 表示失败.
    """
    failures: list[str] = []
    if normalize_query("  AI-Agent  市场 ") != normalize_query("ai-agent 市场"):
        failures.append("query_dedup")
    left = "HTTPS://Example.COM:443/a/?utm_source=x&b=2&a=1#top"
    right = "https://example.com/a?a=1&b=2"
    if normalize_url(left) != normalize_url(right):
        failures.append("url_dedup")
    first = sample_evidence()
    mirror = dict(first, document_url="https://mirror.example/data", evidence_span="The value was 100.")
    if document_key(first) != document_key(mirror):
        failures.append("document_dedup")
    if source_independence_key(first) != source_independence_key(mirror):
        failures.append("source_independence_dedup")
    if validate_evidence([first]):
        failures.append("valid_evidence")
    invalid_evidence = dict(first, access_status="blocked", evidence_span="Unseen content.")
    if not validate_evidence([invalid_evidence]):
        failures.append("invalid_evidence_access")
    no_progress = {
        "effective": True,
        "action_status": "completed",
        "duplicate": False,
        "retry": False,
        "new_high_quality_evidence": False,
        "claim_coverage_improved": False,
        "new_high_impact_contradiction": False,
    }
    if is_information_saturated([no_progress]) or not is_information_saturated([no_progress, no_progress]):
        failures.append("saturation_window")
    progress = dict(no_progress, claim_coverage_improved=True)
    if is_information_saturated([no_progress, progress]):
        failures.append("saturation_progress_reset")
    retry = dict(no_progress, retry=True)
    if is_information_saturated([no_progress, retry]):
        failures.append("saturation_ignores_retry")
    budgets = dict(DEFAULT_BUDGETS)
    usage = {"search_count": 60, "visit_count": 1, "elapsed_minutes": 1}
    if choose_stop_reason(False, [], budgets, usage) != "budget_exhausted":
        failures.append("budget_exhausted")
    if choose_stop_reason(True, [no_progress, no_progress], budgets, usage) != "evidence_sufficient":
        failures.append("stop_precedence")
    valid_manifest = {
        "schema_version": "v62",
        "run_id": "run-v62-test",
        "status": "incomplete",
        "stop_reason": "information_saturated",
        "question": "Example question",
        "created_at": "2026-07-16T00:00:00Z",
        "completed_at": "2026-07-16T00:10:00Z",
        "parent_run_id": None,
        "supersedes": None,
        "controller_id": "controller-main",
        "worker_ids": ["worker-one"],
        "budgets": budgets,
        "usage": usage,
        "budget_overrides": {},
        "engine_report_permission": False,
        "report_path": None,
        "report_status": "not_generated",
        "errors": [],
    }
    if validate_manifest(valid_manifest, Path("run-v62-test"), Path.cwd()):
        failures.append("valid_incomplete_manifest")
    running_manifest = dict(valid_manifest, status="running", stop_reason=None, completed_at=None)
    if validate_manifest(running_manifest, Path("run-v62-test"), Path.cwd()):
        failures.append("valid_running_manifest")
    invalid_status_manifest = dict(valid_manifest, status="finished")
    if not validate_manifest(invalid_status_manifest, Path("run-v62-test"), Path.cwd()):
        failures.append("invalid_run_status")
    invalid_stop_manifest = dict(valid_manifest, stop_reason="done")
    if not validate_manifest(invalid_stop_manifest, Path("run-v62-test"), Path.cwd()):
        failures.append("invalid_stop_reason")
    invalid_manifest = dict(valid_manifest, report_path="reports/forbidden.md", report_status="generated")
    if not validate_manifest(invalid_manifest, Path("run-v62-test"), Path.cwd()):
        failures.append("incomplete_report_gate")
    mismatched_report_manifest = dict(
        valid_manifest,
        status="completed",
        engine_report_permission=True,
        report_path="reports/different-name.md",
        report_status="generated",
    )
    mismatch_errors = validate_manifest(mismatched_report_manifest, Path("run-v62-test"), Path.cwd())
    if not any("filename stem must equal run_id" in error for error in mismatch_errors):
        failures.append("report_run_name_link")
    duplicate_index = [
        ("run-a", dict(valid_manifest, run_id="duplicate-run")),
        ("run-b", dict(valid_manifest, run_id="duplicate-run")),
    ]
    if not validate_run_index(duplicate_index):
        failures.append("duplicate_run_id")
    report_index = [
        ("run-a", dict(valid_manifest, run_id="run-a", status="completed", engine_report_permission=True, report_status="generated", report_path="reports/shared.md")),
        ("run-b", dict(valid_manifest, run_id="run-b", status="completed", engine_report_permission=True, report_status="generated", report_path="reports/shared.md")),
    ]
    if not validate_run_index(report_index):
        failures.append("cross_run_report_overwrite")
    valid_plan = {
        "schema_version": "v62",
        "run_id": "run-v62-test",
        "question": "Example question",
        "boundary": {},
        "claims": [
            {
                "claim_id": "claim-market-size",
                "claim_text": "The market has measurable size.",
                "claim_type": "market-size",
                "geography": "global",
                "time_range": "2025",
                "required_evidence_tier": "primary",
                "preferred_source_categories": ["official-statistics"],
            }
        ],
        "source_routes": [],
        "rounds": ["initial"],
        "worker_assignments": [],
    }
    if validate_plan(valid_plan, "run-v62-test"):
        failures.append("valid_plan")
    valid_gaps = {
        "schema_version": "v62",
        "run_id": "run-v62-test",
        "gaps": [
            {
                "gap_id": "gap-market-definition",
                "claim_id": "claim-market-size",
                "missing_item": "Comparable definition",
                "impact": "high",
                "status": "closed",
                "attempted_actions": [],
                "unresolved_reason": "",
                "next_source_route": "registered_canonical",
            }
        ],
        "contradictions": [],
    }
    if validate_gaps(valid_gaps, "run-v62-test", {"claim-market-size"}):
        failures.append("valid_gaps")
    evidence_hash = evidence_span_sha256(first)
    base_challenge = {
        "challenge_id": "challenge-market-definition",
        "reviewer_role": "industry-expert",
        "target_claim_id": "claim-market-size",
        "target_section": "4. Lifecycle Assessment",
        "challenge": "The market definition may include non-comparable categories.",
        "materiality": "high",
        "verification_method": "retrieval",
        "verification_required": "Check the official dataset definition.",
        "gap_id": "gap-market-definition",
        "resolution": "confirmed",
        "evidence_refs": [
            {
                "source_id": first["source_id"],
                "document_url": first["document_url"],
                "page_or_section": first["page_or_section"],
                "relation": first["relation"],
                "evidence_span_sha256": evidence_hash,
            }
        ],
        "verification_notes": "The official definition includes the disputed category.",
        "report_change": "The report narrows the market definition.",
        "confidence_action": "downgraded",
        "reviewer_status": "closed",
        "closed_by": "original-reviewer",
        "reviewer_note": "The revised scope resolves the challenge.",
    }
    valid_challenges = {
        "schema_version": "v65",
        "run_id": "run-v62-test",
        "review_mode": "single-agent-simulated",
        "challenges": [
            base_challenge,
            dict(base_challenge, challenge_id="challenge-investment", reviewer_role="investment-researcher", materiality="medium", closed_by="organizer"),
            dict(base_challenge, challenge_id="challenge-policy", reviewer_role="policy-regulatory", materiality="medium", closed_by="organizer"),
            dict(base_challenge, challenge_id="challenge-operator", reviewer_role="operator-entrepreneur", materiality="medium", closed_by="organizer"),
        ],
    }
    challenge_errors = validate_challenges(
        valid_challenges,
        "run-v62-test",
        {"claim-market-size"},
        valid_gaps,
        [first],
        True,
    )
    if challenge_errors:
        failures.append(f"valid_challenges: {challenge_errors[0]}")
    pending_challenges = dict(
        valid_challenges,
        challenges=[dict(base_challenge, resolution="pending", reviewer_status="open")],
    )
    pending_errors = validate_challenges(
        pending_challenges,
        "run-v62-test",
        {"claim-market-size"},
        valid_gaps,
        [first],
        True,
    )
    if not any("pending Challenge blocks formal report" in error for error in pending_errors):
        failures.append("pending_challenge_report_gate")
    organizer_high = dict(
        valid_challenges,
        challenges=[dict(base_challenge, closed_by="organizer")],
    )
    organizer_errors = validate_challenges(
        organizer_high,
        "run-v62-test",
        {"claim-market-size"},
        valid_gaps,
        [first],
        False,
    )
    if not any("high Challenge must be closed by original reviewer" in error for error in organizer_errors):
        failures.append("high_original_reviewer_gate")
    non_retrieval_gap = dict(
        valid_challenges,
        challenges=[dict(base_challenge, verification_method="logic")],
    )
    non_retrieval_errors = validate_challenges(
        non_retrieval_gap,
        "run-v62-test",
        {"claim-market-size"},
        valid_gaps,
        [first],
        False,
    )
    if not any("non-retrieval Challenge requires null gap_id" in error for error in non_retrieval_errors):
        failures.append("non_retrieval_gap_gate")
    open_gap_challenges = json.loads(json.dumps(valid_challenges))
    open_gap_errors = validate_challenges(
        open_gap_challenges,
        "run-v62-test",
        {"claim-market-size"},
        dict(valid_gaps, gaps=[dict(valid_gaps["gaps"][0], status="open")]),
        [first],
        False,
    )
    if not any("retrieval resolution conflicts with open Gap status" in error for error in open_gap_errors):
        failures.append("retrieval_gap_status_gate")
    missing_ledger = Path("missing-challenges.json")
    if validate_challenge_artifact_requirement(valid_manifest, missing_ledger):
        failures.append("incomplete_challenge_artifact_optional")
    generated_without_ledger = dict(valid_manifest, report_status="generated")
    if not validate_challenge_artifact_requirement(generated_without_ledger, missing_ledger):
        failures.append("generated_challenge_artifact_gate")
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
    parser = argparse.ArgumentParser(description="Check v62 Deep Search Protocol and Research Run contracts.")
    parser.add_argument("run_dir", type=Path, nargs="?", help="Research Run directory.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root.")
    parser.add_argument(
        "--skill-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Industry research skill root. Defaults to the installed script parent.",
    )
    parser.add_argument("--research-root", type=Path, help="Optional Research Run root for cross-Run checks.")
    parser.add_argument("--self-test", action="store_true", help="Run deterministic contract tests.")
    parser.add_argument("--check-boundary", action="store_true", help="Check Engine and Protocol authority boundary.")
    parser.add_argument("--merge", action="store_true", help="Merge Worker Evidence before validation.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser


def main() -> int:
    """
执行命令行入口.

    :return: 退出码, 0 表示通过, 1 表示失败.
    """
    args = build_parser().parse_args()
    if args.self_test:
        return run_self_test(args.json)
    errors: list[str] = []
    if args.check_boundary:
        engine_text = (args.skill_root / "references" / "deep-research-engine.md").read_text(
            encoding="utf-8"
        )
        protocol_text = (args.skill_root / "references" / "deep-search-protocol.md").read_text(
            encoding="utf-8"
        )
        errors.extend(validate_authority_boundary(engine_text, protocol_text))
    if args.run_dir:
        if args.merge:
            write_evidence_jsonl(args.run_dir / "evidence.jsonl", merge_worker_evidence(args.run_dir))
        errors.extend(validate_run_bundle(args.run_dir, args.repo_root))
    if args.research_root:
        errors.extend(validate_research_root(args.research_root))
    if not args.run_dir and not args.check_boundary and not args.research_root:
        raise SystemExit("run_dir is required unless --self-test or --check-boundary is used")
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
