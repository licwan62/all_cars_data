from __future__ import annotations

import argparse
import json
from decimal import Decimal
from pathlib import Path

from common import load_config, read_csv


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "research_queue" / "allocation_weight_queue.csv"


def atom_prior(atom_key: str, policy: dict) -> Decimal:
    _, _, trim, cab, bed, _, _ = atom_key.split("|", 6)
    value = Decimal(str(policy["base_trim_prior"] if not trim else policy["named_trim_prior"]))
    lowered_cab = cab.casefold()
    for name, prior in policy["cab_priors"].items():
        if name in lowered_cab:
            value *= Decimal(str(prior))
            break
    for name, prior in policy["bed_priors"].items():
        if bed == name:
            value *= Decimal(str(prior))
            break
    return value


def build(worker: str, destination: Path, config_path: str = "config.json") -> int:
    load_config(config_path)  # Validate the project configuration before touching a review batch.
    policy = json.loads((ROOT / "data" / "modeled_config_share_policy.json").read_text(encoding="utf-8"))
    _, queue = read_csv(QUEUE)
    claimed = [row for row in queue if row["status"] == "in_progress" and row["worker"] == worker]
    items = []
    for row in claimed:
        keys = row["ATOM_KEYS"].split(";")
        priors = [atom_prior(key, policy) for key in keys]
        total = sum(priors)
        items.append({
            "queue_key": row["queue_key"], "outcome": "allocated",
            "ALLOCATION_METHOD": policy["method"], "SALES_CONFIDENCE": policy["confidence"],
            "SOURCE_URL": policy["source_url"], "review_note": policy["notes"],
            "allocations": [
                {"SALES_ATOM_KEY": key, "ALLOCATION_WEIGHT": str(prior / total)}
                for key, prior in zip(keys, priors)
            ],
        })
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(items)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--config", default="config.json")
    args = parser.parse_args()
    print({"groups": build(args.worker, args.output, args.config)})
