"""承接 02 已发布的 US 市场潜力；本节点不计算潜力或读取销售来源。"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from artifact_batch import RunBatch, published_reference, sha256
from node_paths import load_record
COLUMN = "市场潜力"
ADJUSTMENT = "销量潜力调整"
BASE_TABLE = "US/全量/全量表.csv"
TABLES = [BASE_TABLE, *[f"US/店铺/店铺全量_{shop}.csv" for shop in ("HNT", "TM", "TM_拆分")]]
def read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)

def attach(frame: pd.DataFrame, detail: pd.DataFrame) -> pd.DataFrame:
    ids = frame["DIMENSION-ID"]
    columns = [COLUMN, ADJUSTMENT]
    if ids.duplicated().any() or set(ids) != set(detail["DIMENSION-ID"]):
        raise ValueError("US 店铺与潜力表 DIMENSION-ID 不一致")
    result = frame.drop(columns=columns, errors="ignore").copy()
    for offset, column in enumerate(columns, 1):
        values = detail.set_index("DIMENSION-ID")[column]
        result.insert(result.columns.get_loc("车型销量") + offset, column, ids.map(values))
    previous = frame.drop(columns=columns, errors="ignore")
    if not result[previous.columns].equals(previous):
        raise ValueError("市场潜力回填改变原字段")
    return result

def register_base(batch: RunBatch, path: Path, project: Path) -> str:
    """承接基表实际来源；不把当前最新上游冒记为旧基表的输入。"""
    digest = sha256(path)
    reference, _ = published_reference(path, digest)
    manifest_path = project / "output" / "manifest.json"
    if reference and manifest_path.is_file():
        batch.inputs.append(reference)
        manifest = load_record(manifest_path)
        for upstream in manifest.get("upstream", []):
            if upstream.get("basis") != "run":
                continue
            for item in upstream.get("files", []):
                batch.inputs.append({**item, "node": upstream["node"], "version": upstream.get("version")})
        return digest
    name = path.relative_to(project / "output").as_posix()
    for record_path in sorted((project / "artifacts").glob("*/run.json"), reverse=True):
        record = load_record(record_path)
        if record.get("status", {}).get("status") == "passed" and any(
            item["file"] == name and item["sha256"] == digest for item in record.get("outputs", [])
        ):
            batch.inputs.extend(record.get("inputs", []))
            return digest
    # 非发布/非正式生成的基表必须快照，避免无法复现。
    batch.input(path, name=name)
    return digest



def run(project: Path = PROJECT, source_dir: Path | None = None) -> dict:
    source_dir = source_dir or project.parent / "02.销量评估/output"
    path = source_dir / "市场潜力.csv"
    manifest = load_record(source_dir / "manifest.json")
    expected = next((i["sha256"] for i in manifest["deliverables"] if i["file"] == path.name), None)
    if expected != sha256(path):
        raise ValueError("市场潜力与02 manifest sha256不一致，请先发布02")
    with RunBatch.create(project / "artifacts", "us-market-potential", data_dir=project / "data") as batch:
        detail = read(path)
        columns = [COLUMN, ADJUSTMENT]
        if set(["DIMENSION-ID", *columns]) - set(detail) or detail["DIMENSION-ID"].eq("").any() or detail["DIMENSION-ID"].duplicated().any():
            raise ValueError("市场潜力字段或 DIMENSION-ID 非法")
        numbers = detail[columns].apply(pd.to_numeric, errors="raise")
        if not np.isfinite(numbers.to_numpy()).all() or (numbers < 0).any(axis=None) or (numbers[ADJUSTMENT] > numbers[COLUMN]).any():
            raise ValueError("市场潜力数值或调整值非法")
        frames = {name: read(project / "output" / name) for name in TABLES}
        for name in TABLES:
            register_base(batch, project / "output" / name, project)
        batch.input(path)
        batch.inputs = list({json.dumps(item, sort_keys=True): item for item in batch.inputs}.values())
        enriched = {name: attach(frame, detail) for name, frame in frames.items()}
        for name, frame in enriched.items():
            frame.to_csv(batch.output(name), index=False, encoding="utf-8-sig", lineterminator="\n")
        summary = {"rows": len(detail), "tables": TABLES, "source_version": manifest["version"]}
        batch.finish(summary, publish_to=project / "output")
        return {"batch": str(batch.directory), **summary}

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
