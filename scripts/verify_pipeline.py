#!/usr/bin/env python3
"""验证各节点流水线是否打通（只读：不改动任何节点的 output/、artifacts/ 或 流水线状态.md）。

检查项：
1. 结构：``validate_pipeline_structure`` 全部规则。
2. 追踪：每个节点 output/ 与来源 artifact 一致；上游版本是否已变化（过期）。
3. 依赖：扫描 code_dir 中代码引用的其他节点目录，对照 pipeline.json 声明的上游；
   引用其他节点 artifacts/、或引用不存在的输入路径时给出提示。
4. 代码：code_dir 下所有 .py 能编译；run 命令引用的脚本存在。
5. 测试：运行每个节点登记的 tests 目录与仓库根 tests/。
6. 重建（可选 ``--rebuild``）：把节点目录（不含 artifacts）、上游节点的 output/ 与 lib/ 复制到临时沙箱，
   在沙箱中执行 run 命令，比较产出的交付物与当前 output/ 是否逐字节一致。

    python scripts/verify_pipeline.py                       # 1-5
    python scripts/verify_pipeline.py --skip-tests          # 只做静态检查
    python scripts/verify_pipeline.py --rebuild size-compression,compression-scoring
    python scripts/verify_pipeline.py --report 验证报告.md   # 另存 Markdown 报告
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import trace_pipeline
import validate_pipeline_structure

ROOT = Path(__file__).resolve().parents[1]
CODE_SUFFIXES = {".py", ".ps1", ".psm1"}
# 运行期由脚本自己创建的目录，不算缺失输入
RUNTIME_DIRS = {"output", "artifacts", "work", "cache", "logs", "tmp"}
ROOT_VARIABLES = {"ROOT", "WORKSPACE_ROOT", "WORKSPACE_DIR", "REPO_ROOT", "repo", "root", "workspace_dir"}


@dataclass
class NodeResult:
    node: dict
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    tests: str = "—"
    rebuild: str = "—"

    @property
    def state(self) -> str:
        return "FAIL" if self.errors else ("WARN" if self.warnings else "OK")


def as_list(value: str | list[str] | None) -> list[str]:
    if value is None:
        return []
    return [value] if isinstance(value, str) else list(value)


def code_files(node: dict) -> list[Path]:
    base = ROOT / node["path"]
    files: list[Path] = []
    for name in as_list(node.get("code_dir")):
        for path in sorted((base / name).rglob("*")):
            if path.suffix in CODE_SUFFIXES and "__pycache__" not in path.parts and "artifacts" not in path.relative_to(base).parts:
                files.append(path)
    return files


def _python_references(text: str) -> tuple[list[str], list[str], set[tuple[str, str]]]:
    """返回 (代码中的字符串常量, 以仓库根变量开头的路径首段, 相邻路径段对)；忽略注释和 docstring。"""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return [text], [], set()
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                docstrings.add(id(first.value))
    strings = [
        node.value for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstrings
    ]
    roots = [
        node.right.value for node in ast.walk(tree)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div)
        and isinstance(node.left, ast.Name) and node.left.id in ROOT_VARIABLES
        and isinstance(node.right, ast.Constant) and isinstance(node.right.value, str)
    ]
    # a / "X" / "artifacts" 解析为 BinOp(BinOp(a, "X"), "artifacts")
    pairs = {
        (node.left.right.value, node.right.value) for node in ast.walk(tree)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div)
        and isinstance(node.right, ast.Constant) and isinstance(node.right.value, str)
        and isinstance(node.left, ast.BinOp) and isinstance(node.left.op, ast.Div)
        and isinstance(node.left.right, ast.Constant) and isinstance(node.left.right.value, str)
    }
    return strings, roots, pairs


def check_dependencies(node: dict, nodes: list[dict]) -> tuple[list[str], list[str]]:
    """返回 (错误, 提示)。代码引用的其他节点必须是已声明上游；不得读取其他节点 artifacts/。"""
    errors: list[str] = []
    warnings: list[str] = []
    others = {other["path"]: other for other in nodes if other["id"] != node["id"]}
    declared = set(node.get("upstream", []))
    referenced: dict[str, set[str]] = {}
    missing: set[str] = set()
    base = ROOT / node["path"]
    for path in code_files(node):
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        relative = path.relative_to(base).as_posix()
        strings, roots, pairs = _python_references(text) if path.suffix == ".py" else ([text], [], set())
        for other_path, other in others.items():
            hits = [value.replace("\\", "/") for value in strings if other_path in value]
            if not hits:
                continue
            referenced.setdefault(other["id"], set()).add(relative)
            if (other_path, "artifacts") in pairs or any(f"{other_path}/artifacts" in value for value in hits):
                warnings.append(f"{relative} 读取了 {other_path}/artifacts（正式输入应只来自上游 output/）")
            elif other["id"] in declared:
                for first, second in sorted(pairs):
                    if first == other_path and second in {"data", "code", "src", "scripts", "cache", "work"}:
                        warnings.append(f"{relative} 读取了上游 {other_path}/{second}（正式输入应只来自上游 output/）")
        for literal in roots:
            first = literal.replace("\\", "/").split("/")[0]
            if first in RUNTIME_DIRS or first in others or first == node["path"]:
                continue
            candidates = (ROOT / first, base / first, path.parent / first, path.parent / "artifacts" / first)
            if not any(candidate.exists() for candidate in candidates):
                missing.add(f"{relative}: {first}")
    for other_id, files in sorted(referenced.items()):
        if other_id not in declared:
            other = next(n for n in nodes if n["id"] == other_id)
            downstream = node["id"] in other.get("upstream", [])
            message = f"代码引用了未声明为上游的节点 {other['path']}（{', '.join(sorted(files))}）"
            (warnings if downstream else errors).append(message + ("；对方是本节点下游，存在反向依赖" if downstream else ""))
    for item in sorted(missing):
        warnings.append(f"引用的输入路径不存在：{item}")
    return errors, warnings


def check_compile(node: dict) -> list[str]:
    errors = []
    for path in code_files(node):
        if path.suffix != ".py":
            continue
        try:
            compile(path.read_bytes(), str(path), "exec", dont_inherit=True)
        except (SyntaxError, ValueError) as error:
            errors.append(f"编译失败 {path.relative_to(ROOT)}: {error}")
    return errors


def run_pytest(cwd: Path, target: str) -> tuple[bool, str]:
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", target],
        cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace",
        env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"},
    )
    lines = [line for line in completed.stdout.strip().splitlines() if line.strip()]
    summary = lines[-1].strip("= ") if lines else completed.stderr.strip()[-200:]
    return completed.returncode == 0, summary


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rebuild_node(node: dict, by_id: dict[str, dict], keep: bool = False, loose: bool = False) -> tuple[bool, str]:
    """在沙箱里执行 run 命令，返回 (是否与当前 output 一致, 说明)。

    默认沙箱只提供上游 output/（严格按约定）；loose=True 时复制完整上游节点目录，用于区分
    “违反只读 output/ 约定”与“代码/数据本身不通”。
    """
    commands = [command for command in node.get("run") or [] if command.startswith("python ")]
    if not commands:
        return False, "未登记可自动执行的 python run 命令"
    sandbox = Path(tempfile.mkdtemp(prefix="pipeline-rebuild-"))
    try:
        for name in ("lib", "scripts"):
            shutil.copytree(ROOT / name, sandbox / name, ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copy2(ROOT / "pipeline.json", sandbox / "pipeline.json")
        source = ROOT / node["path"]
        shutil.copytree(source, sandbox / node["path"], ignore=lambda d, names: [n for n in names if n == "__pycache__" or (Path(d) == source and n == "artifacts")])
        (sandbox / node["path"] / "artifacts").mkdir(exist_ok=True)
        for upstream_id in node.get("upstream", []):
            upstream = by_id[upstream_id]
            if loose:
                shutil.copytree(ROOT / upstream["path"], sandbox / upstream["path"], ignore=shutil.ignore_patterns("__pycache__"))
            else:
                shutil.copytree(ROOT / upstream["path"] / "output", sandbox / upstream["path"] / "output")
        before = {name: sha256(ROOT / node["path"] / "output" / name) for name in node.get("outputs", [])}
        for command in commands:
            completed = subprocess.run(
                [sys.executable, *command.split()[1:]], cwd=sandbox / node["path"], capture_output=True, text=True,
                encoding="utf-8", errors="replace", env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"},
            )
            if completed.returncode != 0:
                tail = (completed.stderr or completed.stdout).strip().splitlines()[-1:] or [""]
                return False, f"`{command}` 失败（退出码 {completed.returncode}）：{tail[0][:200]}"
        after_dir = sandbox / node["path"] / "output"
        changed = [name for name, digest in before.items() if not (after_dir / name).is_file() or sha256(after_dir / name) != digest]
        if changed:
            return False, f"重建成功，但与当前 output 不一致：{'、'.join(changed)}"
        return True, f"重建成功，{len(before)} 个交付物与当前 output 逐字节一致"
    finally:
        if keep:
            print(f"  沙箱保留在 {sandbox}")
        else:
            shutil.rmtree(sandbox, ignore_errors=True)


def render_report(results: list[NodeResult], global_errors: list[str], root_tests: str) -> str:
    lines = ["# 流水线打通验证", "", "| 节点 | 状态 | 测试 | 重建 |", "| --- | --- | --- | --- |"]
    for result in results:
        lines.append(f"| {result.node['path']} | {result.state} | {result.tests} | {result.rebuild} |")
    lines += ["", f"仓库级测试 `tests/`：{root_tests}", ""]
    if global_errors:
        lines += ["## 全局问题", "", *[f"- {error}" for error in global_errors], ""]
    details = [result for result in results if result.errors or result.warnings]
    if details:
        lines += ["## 节点问题", ""]
        for result in details:
            lines.append(f"### {result.node['path']}")
            lines.extend(f"- 错误：{error}" for error in result.errors)
            lines.extend(f"- 提示：{warning}" for warning in result.warnings)
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skip-tests", action="store_true", help="不运行测试")
    parser.add_argument("--rebuild", default="", help="在沙箱中重建并比对的节点 id（逗号分隔，all 表示全部登记了 run 的节点）")
    parser.add_argument("--keep-sandbox", action="store_true", help="保留重建沙箱以便排查")
    parser.add_argument("--loose", action="store_true", help="重建时复制完整上游节点目录（默认只复制上游 output/）")
    parser.add_argument("--report", type=Path, help="另存 Markdown 报告（不得指向 流水线状态.md）")
    args = parser.parse_args(argv)

    payload = json.loads((ROOT / "pipeline.json").read_text(encoding="utf-8"))
    nodes = payload["nodes"]
    by_id = {node["id"]: node for node in nodes}
    rebuild_ids = {node["id"] for node in nodes if node.get("run")} if args.rebuild == "all" else {x for x in args.rebuild.split(",") if x}
    unknown = rebuild_ids - by_id.keys()
    if unknown:
        parser.error(f"未知节点：{', '.join(sorted(unknown))}")

    global_errors: list[str] = []
    stderr = sys.stderr
    try:
        import io
        sys.stderr = buffer = io.StringIO()
        if validate_pipeline_structure.main() != 0:
            global_errors.extend(line[2:] for line in buffer.getvalue().splitlines() if line.startswith("- "))
    finally:
        sys.stderr = stderr

    results: list[NodeResult] = []
    for node in nodes:
        result = NodeResult(node)
        errors, stale = trace_pipeline.trace_node(node, by_id)
        result.errors += errors
        result.warnings += [line.split(": ", 1)[-1] for line in stale]
        dep_errors, dep_warnings = check_dependencies(node, nodes)
        result.errors += dep_errors
        result.warnings += dep_warnings
        result.errors += check_compile(node)
        if not args.skip_tests:
            outcomes = [(target, *run_pytest(ROOT / node["path"], target)) for target in as_list(node.get("tests"))]
            if outcomes:
                result.tests = "；".join(summary for _, _, summary in outcomes)
                result.errors += [f"测试失败 {target}: {summary}" for target, ok, summary in outcomes if not ok]
        if node["id"] in rebuild_ids:
            print(f"重建 {node['path']} …", flush=True)
            ok, message = rebuild_node(node, by_id, keep=args.keep_sandbox, loose=args.loose)
            result.rebuild = "一致" if ok else "失败"
            if not ok:
                result.errors.append(f"重建：{message}")
        results.append(result)
        print(f"{node['path']:<20} {result.state:<5} 测试: {result.tests}  重建: {result.rebuild}", flush=True)
        for error in result.errors:
            print(f"    ✗ {error}")
        for warning in result.warnings:
            print(f"    · {warning}")

    root_tests = "未运行"
    if not args.skip_tests:
        ok, root_tests = run_pytest(ROOT, "tests")
        if not ok:
            global_errors.append(f"仓库级测试失败：{root_tests}")
    for error in global_errors:
        print(f"全局 ✗ {error}")

    if args.report:
        if args.report.resolve() == (ROOT / "流水线状态.md").resolve():
            parser.error("流水线状态.md 只由 publish_release.py 写入")
        args.report.write_text(render_report(results, global_errors, root_tests), encoding="utf-8")
        print(f"报告已写入 {args.report}")
    failed = bool(global_errors) or any(result.errors for result in results)
    print("结论：" + ("存在未打通的节点" if failed else "全部节点打通"))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
