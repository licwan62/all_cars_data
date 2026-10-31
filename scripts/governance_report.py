"""Generate current naming, ownership and raw SHA inventories without changing node data."""
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from content_store import raw_sha256
from rules_snapshot import rules_snapshot
from pipeline_contract import lifecycle_state


def write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    report = ROOT / "reports/结构优化实施"
    report.mkdir(parents=True, exist_ok=True)
    payload = json.loads((ROOT / "pipeline.json").read_text(encoding="utf-8"))
    rows, naming, duplicate = [], [], defaultdict(list)
    for node in payload["nodes"]:
        project = ROOT / node["path"]
        rule_hashes = {r["file"]: r["sha256"] for r in rules_snapshot(project)}
        naming.append({"节点ID":node["id"], "目录":node["path"], "类型":node.get("kind"),
                       "状态":lifecycle_state(node) or "活跃", "层数":node["layer"],
                       "归属容器":node.get("parent", ""), "命名依据":node["naming_basis"],
                       "上游":",".join(node["upstream"]), "交付物数":len(node["outputs"])})
        folders = node.get("code_dir") or []
        if isinstance(folders, str):
            folders = [folders]
        code = [(p, p.read_text(encoding="utf-8-sig", errors="replace")) for folder in folders for p in (project / folder).rglob("*.py") if "__pycache__" not in p.parts]
        for file, rule_sha in rule_hashes.items():
            path = project / file
            sha = raw_sha256(path)
            relative = path.relative_to(ROOT).as_posix()
            duplicate[sha].append(relative)
            rows.append({"节点ID":node["id"], "维护文件":relative, "原始SHA256":sha,
                         "规则SHA256":rule_sha, "字节数":path.stat().st_size,
                         "代码引用":";".join(p.relative_to(ROOT).as_posix() for p, text in code if path.name in text),
                         "维护状态":"归属已登记；静态引用非完整使用证明"})
    write_csv(report / "节点命名依据.csv", list(naming[0]), naming)
    write_csv(report / "文件归属与SHA.csv", list(rows[0]), rows)
    groups = [{"sha256": sha, "paths":paths, "policy":"工作副本不按内容自动合并资料身份"} for sha, paths in duplicate.items() if len(paths) > 1]
    (report / "相同内容维护文件.json").write_text(json.dumps(groups, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"{len(naming)}个节点；{len(rows)}份维护文件；{len(groups)}组同字节工作资料")


if __name__ == "__main__":
    main()
