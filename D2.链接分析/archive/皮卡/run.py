"""Regenerate the pickup cluster candidate and its independent link analysis."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run(*args: object, cwd: Path | None = None) -> None:
    subprocess.run([sys.executable, *map(str, args)], cwd=cwd, check=True)


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    cluster_project = repo / "D1.聚类SKU" / "artifacts" / "皮卡"
    cluster_output = cluster_project / "output"
    engine = repo / "D2.链接分析" / "sku_shipment_analysis"
    output = Path(__file__).resolve().parent / "artifacts" / "0914"

    run(
        cluster_project / "main.py",
        "--size-input", Path(r"\\NAS8824B4\Public\PQData\pub_all_cars_data") / "全量数据.csv",
        "--sales-input", repo / "02.销量评估" / "output" / "原子销量.csv",
        "--output", cluster_output,
        cwd=cluster_project,
    )
    run(
        engine / "main.py",
        "--cluster-dir", cluster_output,
        "--output-dir", output,
        cwd=engine,
    )


if __name__ == "__main__":
    main()
