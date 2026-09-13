"""Regenerate the W-car cluster candidate and its independent link analysis."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run(*args: object, cwd: Path | None = None) -> None:
    subprocess.run([sys.executable, *map(str, args)], cwd=cwd, check=True)


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    cluster_project = repo / "聚类SKU" / "changes" / "W型车"
    cluster_output = cluster_project / "output"
    engine = repo / "链接分析" / "sku_shipment_analysis"
    output = Path(__file__).resolve().parent / "output"

    run(cluster_project / "run_cluster.py")
    run(
        engine / "build_merged_clusters.py",
        "--cluster-dir", cluster_output,
        "--output-dir", output,
        "--publish",
        cwd=engine,
    )
    run(
        engine / "main.py",
        "--cluster-dir", cluster_output,
        "--output-dir", output,
        cwd=engine,
    )


if __name__ == "__main__":
    main()
