"""
维护用批量 Markdown 报告检查器.

本脚本扫描目录中的 Markdown 文件, 并复用 report_contract_check 的 auto profile.
它只用于回归维护, 不参与正常报告生成.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from report_contract_check import read_text, run_profile


def collect_reports(root: Path, pattern: str, recursive: bool) -> list[Path]:
    """
    收集待检查 Markdown 报告.

    :param root: 报告目录或单个报告文件.
    :param pattern: 文件匹配模式.
    :param recursive: 是否递归扫描.
    :return: 报告路径列表.
    """
    if root.is_file():
        return [root]
    globber = root.rglob if recursive else root.glob
    return sorted(path for path in globber(pattern) if path.is_file())


def check_report(path: Path) -> dict[str, object]:
    """
    检查单个报告.

    :param path: 报告路径.
    :return: 检查结果.
    """
    text = read_text(path)
    errors = run_profile(text, "auto")
    return {
        "report": str(path),
        "status": "fail" if errors else "pass",
        "errors": errors,
    }


def run_batch(root: Path, pattern: str, recursive: bool) -> dict[str, object]:
    """
    执行批量检查.

    :param root: 报告目录或单个报告文件.
    :param pattern: 文件匹配模式.
    :param recursive: 是否递归扫描.
    :return: 汇总结果.
    """
    reports = collect_reports(root, pattern, recursive)
    results = [check_report(path) for path in reports]
    failed = [result for result in results if result["status"] == "fail"]
    return {
        "status": "fail" if failed else "pass",
        "total": len(results),
        "passed": len(results) - len(failed),
        "failed": len(failed),
        "results": results,
    }


def run_self_test(json_output: bool = False) -> int:
    """
    运行批量检查器内置自检.

    :param json_output: 是否输出 JSON.
    :return: 退出码, 0 表示自检通过, 1 表示自检失败.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        (root / "pass_short.md").write_text(
            "价格战通常来自供给扩张快于需求, 龙头希望用价格换份额, 中小玩家被迫跟进. 具体强度还需要结合销量, 库存和盈利数据验证.",
            encoding="utf-8",
        )
        (root / "fail_report.md").write_text(
            "## 1. 直接结论\n\n这是一个不完整报告.",
            encoding="utf-8",
        )
        summary = run_batch(root, "*.md", False)

    expected = {
        "status": "fail",
        "total": 2,
        "passed": 1,
        "failed": 1,
    }
    failures = [
        f"{key}: expected {value}, got {summary.get(key)}"
        for key, value in expected.items()
        if summary.get(key) != value
    ]

    if json_output:
        print(json.dumps({"status": "fail" if failures else "pass", "failures": failures}, ensure_ascii=False, indent=2))
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
    parser = argparse.ArgumentParser(description="Batch check industry research Markdown reports.")
    parser.add_argument("root", type=Path, nargs="?", help="Report file or directory.")
    parser.add_argument("--pattern", default="*.md", help="Glob pattern when root is a directory.")
    parser.add_argument("--recursive", action="store_true", help="Scan directory recursively.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-test.")
    return parser


def main() -> int:
    """
    执行命令行入口.

    :return: 退出码, 0 表示通过, 1 表示存在失败.
    """
    parser = build_parser()
    args = parser.parse_args()
    if args.self_test:
        return run_self_test(json_output=args.json)
    if not args.root:
        parser.error("root is required unless --self-test is used")
    if not args.root.exists():
        parser.error(f"root does not exist: {args.root}")

    summary = run_batch(args.root, args.pattern, args.recursive)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"{summary['status'].upper()} total={summary['total']} passed={summary['passed']} failed={summary['failed']}")
        for result in summary["results"]:
            print(f"- {result['status'].upper()} {result['report']}")
            for error in result["errors"]:
                print(f"  - {error}")

    return 1 if summary["status"] == "fail" else 0


if __name__ == "__main__":
    sys.exit(main())
