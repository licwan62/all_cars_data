"""Run the proposed US additions through active nodes in a disposable sandbox.

This is a preview: it never modifies node data, output, artifacts or release state
in the working repository. Its inputs and results are recorded in a new report.
"""
import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NODE = ROOT / "nodes/01.整理尺寸库"
sys.path[:0] = [str(ROOT / "lib"), str(NODE / "code")]
from us_year_supplements import apply_supplements
from us_dimension_corrections import apply_corrections


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def preview(destination, corrections_only=False):
    pipeline = json.loads((ROOT / "pipeline.json").read_text(encoding="utf-8"))
    by_id = {node["id"]: node for node in pipeline["nodes"]}
    ids = ["structure-review", "sales-estimation", "code-mapping", "shape-classification",
           "size-calculation", "size-compression"]
    rules_path = NODE / "data/us/year_gap_resolutions.json"
    rules = json.loads(rules_path.read_text(encoding="utf-8"))
    fields, current = read_csv(NODE / "output/尺寸库_US.csv")
    if corrections_only:
        correction_path = NODE / "data/us/dimension_corrections.json"
        proposed = apply_corrections(current, json.loads(correction_path.read_text(encoding="utf-8")))
    else:
        proposed, decisions = apply_supplements(current, rules, NODE)
    added = {row["DIMENSION-ID"] for row in proposed} - {row["DIMENSION-ID"] for row in current}
    destination.mkdir(parents=True, exist_ok=False)
    results = {"rules_sha256": digest(rules_path), "input_us_sha256": digest(NODE / "output/尺寸库_US.csv"),
               "input_all_sha256": digest(NODE / "output/尺寸库.csv"), "script_sha256": digest(Path(__file__)),
               "added_count": len(added), "nodes": []}
    if corrections_only:
        results["mode"] = "corrections_only"
        results["corrections_sha256"] = digest(correction_path)
        results["changed_ids"] = [old["DIMENSION-ID"] for old, new in zip(current, proposed) if old != new]
    _, baseline = read_csv(ROOT / by_id["shape-classification"]["path"] / "data/核定车形基线.csv")
    _, shape_decisions = read_csv(ROOT / by_id["shape-classification"]["path"] / "data/US车形补充核定.csv")
    decided = {row["DIMENSION-ID"] for row in shape_decisions}
    results["new_ids_with_shape_decisions"] = len(added & decided)
    shape_queue = []
    for row in proposed:
        if row["DIMENSION-ID"] not in added or row["DIMENSION-ID"] in decided:
            continue
        matches = [old for old in baseline if old["COUNTRY"] == "US" and
                   all(old[k] == row[k] for k in ("MAKE", "MODEL", "结构", "L-IN", "W-IN", "H-IN"))]
        shape_queue.append({"DIMENSION-ID": row["DIMENSION-ID"], "MAKE": row["MAKE"],
            "MODEL": row["MODEL"], "YEAR": row["YEAR"], "结构": row["结构"],
            "尺寸": "/".join(row[k] for k in ("L-IN", "W-IN", "H-IN")),
            "同车型同结构同尺寸线索": "|".join(old["DIMENSION-ID"] + ":" + old["车形"] for old in matches),
            "状态": "待核对年份、代际和轮廓；线索不等于核定"})
    write_csv(destination / "新增身份车形待核.csv", list(shape_queue[0]) if shape_queue else
              ["DIMENSION-ID", "MAKE", "MODEL", "YEAR", "结构", "尺寸", "同车型同结构同尺寸线索", "状态"], shape_queue)
    with tempfile.TemporaryDirectory(prefix="us-supplement-preview-") as temp:
        sandbox = Path(temp)
        shutil.copy2(ROOT / "pipeline.json", sandbox / "pipeline.json")
        shutil.copytree(ROOT / "lib", sandbox / "lib", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(ROOT / "scripts", sandbox / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        for node_id in ["dimension-crawler", "dimension-library"]:
            relative = by_id[node_id]["path"]
            shutil.copytree(ROOT / relative / "output", sandbox / relative / "output")
        for node_id in ids:
            relative = by_id[node_id]["path"]
            source = ROOT / relative
            shutil.copytree(source, sandbox / relative,
                ignore=lambda directory, names: [name for name in names if name == "__pycache__" or
                    (Path(directory) == source and name in {"output", "artifacts", "cache", "work", "logs"})])
        out = sandbox / by_id["dimension-library"]["path"] / "output"
        proposed.sort(key=lambda row: row["DIMENSION-ID"])
        write_csv(out / "尺寸库_US.csv", fields, proposed)
        all_fields, original_all = read_csv(out / "尺寸库.csv")
        all_rows = [row for row in original_all if not row["DIMENSION-ID"].endswith(" US")]
        # Region order matches the production builder: US, EU, RU.
        regions = {suffix: sorted((row for row in all_rows if row["DIMENSION-ID"].endswith(" " + suffix)),
                                  key=lambda row: row["DIMENSION-ID"]) for suffix in ("EU", "RU")}
        if sum(map(len, regions.values())) != len(all_rows):
            raise ValueError("全区域库中有未识别区域")
        write_csv(out / "尺寸库.csv", all_fields, proposed + regions["EU"] + regions["RU"])
        environment = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"}
        failed = set()
        for node_id in ids:
            node = by_id[node_id]
            blockers = sorted(set(node.get("upstream", [])) & failed)
            entry = {"id": node_id, "commands": []}
            results["nodes"].append(entry)
            if blockers:
                entry.update(status="skipped", blockers=blockers)
                failed.add(node_id)
                continue
            for command in node.get("run", []):
                args = [sys.executable, *command.split()[1:]]
                # Registry updates are permitted only in this temporary sandbox.
                if node_id == "code-mapping":
                    args.append("--update-registry")
                completed = subprocess.run(args, cwd=sandbox / node["path"], capture_output=True,
                    text=True, encoding="utf-8", errors="replace", env=environment)
                log = f"{node_id}_{len(entry['commands']) + 1}.log"
                (destination / log).write_text(completed.stdout + "\n" + completed.stderr, encoding="utf-8")
                entry["commands"].append({"command": command, "exit_code": completed.returncode, "log": log})
                if completed.returncode:
                    failed.add(node_id)
                    break
            entry["status"] = "failed" if node_id in failed else "passed"
            if entry["status"] == "passed":
                # A RunBatch publishes files but not a release manifest.  Supply a
                # sandbox-only input inventory, with the hashes of the actual
                # outputs. It never leaves the disposable preview workspace.
                output = sandbox / node["path"] / "output"
                files = [p for p in output.iterdir() if p.is_file() and p.name != "manifest.json"]
                inventory = {"sandbox_only": True, "node": node_id, "path": node["path"],
                    "version": "sandbox", "deliverables": [
                        {"file": p.name, "sha256": digest(p),
                         "artifact_file": p.relative_to(sandbox).as_posix()}
                        for p in sorted(files)]}
                (output / "manifest.json").write_text(json.dumps(inventory, ensure_ascii=False), encoding="utf-8")
            if entry["status"] == "passed" and node_id in {"structure-review", "code-mapping"}:
                name = "车型结构_US.csv" if node_id == "structure-review" else "尺寸编码映射.csv"
                _, downstream = read_csv(sandbox / node["path"] / "output" / name)
                downstream_ids = [row["DIMENSION-ID"] for row in downstream]
                entry["new_ids_missing"] = len(added - set(downstream_ids))
                entry["duplicate_ids"] = len(downstream_ids) - len(set(downstream_ids))
            if entry["status"] == "passed" and node_id == "code-mapping":
                for filename in ("make_mapping.csv", "model_mapping.csv"):
                    relative = Path(node["path"]) / "data/mapping/us" / filename
                    fields, old = read_csv(ROOT / relative)
                    _, new = read_csv(sandbox / relative)
                    before = {tuple(row[field] for field in fields) for row in old}
                    after = {tuple(row[field] for field in fields) for row in new}
                    entry[filename] = {"old_rows": len(old), "new_rows": len(new),
                                       "old_rows_missing_or_changed": len(before - after)}
            if entry["status"] == "passed" and node_id == "sales-estimation":
                _, old = read_csv(ROOT / node["path"] / "output/原子销量.csv")
                _, new = read_csv(sandbox / node["path"] / "output/原子销量.csv")
                before = {row["atom_record_id"]: row["预估销量"] for row in old}
                after = {row["atom_record_id"]: row["预估销量"] for row in new}
                entry["existing_atom_rows_changed"] = sum(after.get(key) != value for key, value in before.items())
                new_atoms = [row for row in new if row["atom_record_id"] not in before]
                _, sales_holdouts = read_csv(ROOT / by_id["sales-estimation"]["path"] /
                    "data/销量依据/model_year_sales_holdouts.csv")
                holdout_keys = {(r["MAKE"].casefold(), r["MODEL"].casefold(), r["YEAR"]) for r in sales_holdouts}
                proposed_by_id = {r["DIMENSION-ID"]: r for r in proposed if r["DIMENSION-ID"] in added}
                valued_new_atoms = [r for r in new_atoms if r["预估销量"].strip() and float(r["预估销量"]) != 0]
                unreviewed_valued_atoms = []
                for atom in valued_new_atoms:
                    dimension_id = atom["atom_record_id"].split("|ATOM_YEAR=", 1)[0]
                    candidate = proposed_by_id[dimension_id]
                    key = candidate["MAKE"].casefold(), candidate["MODEL"].casefold(), candidate["YEAR"]
                    if key not in holdout_keys:
                        unreviewed_valued_atoms.append(atom["atom_record_id"])
                entry["new_atom_rows"] = len(new_atoms)
                entry["new_atom_unallocated_rows"] = sum(not row["预估销量"].strip() for row in new_atoms)
                entry["new_atom_nonzero_rows"] = len(valued_new_atoms)
                entry["new_atom_nonzero_rows_pending_review"] = len(valued_new_atoms) - len(unreviewed_valued_atoms)
                entry["new_atom_ids_missing_evidence_audit"] = len(unreviewed_valued_atoms)
                entry["new_atom_ids_without_evidence_audit"] = bool(unreviewed_valued_atoms)
                write_csv(destination / "新增原子销量待核.csv", ["atom_record_id", "预估销量", "状态"],
                          [{**row, "状态": "沙箱试算结果，来源及分配依据待核"} for row in new_atoms])
        (destination / "summary.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-dir", type=Path, required=True)
    parser.add_argument("--corrections-only", action="store_true", help="只预览现有身份的尺寸修正")
    args = parser.parse_args()
    print(json.dumps(preview(args.report_dir, args.corrections_only), ensure_ascii=False, indent=2))
