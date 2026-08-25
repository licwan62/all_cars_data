"""Persistent ecommerce-link identity registry for consumer fitment clusters."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pandas as pd

from atom_verifier import expand_original_atoms


REGISTRY_COLUMNS = [
    "LINK_ID",
    "STATUS",
    "PHYSICAL_SKU",
    "CLUSTER_KEY",
    "ATOM_COUNT",
    "ATOM_KEYS_JSON",
    "MERGED_INTO",
]


def _slug(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9]+", "-", str(value)).strip("-")
    return value or "FITMENT"


def _atom_set(cluster: dict) -> set[str]:
    return expand_original_atoms(cluster.get("rows", pd.DataFrame()))


def generate_cluster_key(cluster: dict) -> str:
    """Generate a current-content fingerprint; this is not the persistent ID."""
    rows = cluster.get("rows", pd.DataFrame())
    if rows.empty:
        return "FIT-EMPTY"
    pairs = sorted({
        (str(r.get("MAKE_NORMALIZED", "")).strip(), str(r.get("MODEL_FAMILY", "")).strip())
        for _, r in rows.iterrows()
    })
    label = _slug("-".join(f"{make}-{model}" for make, model in pairs))[:56]
    payload = "\n".join(sorted(_atom_set(cluster)))
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12].upper()
    return f"FIT-{label}-{digest}"


def _empty_registry() -> pd.DataFrame:
    return pd.DataFrame(columns=REGISTRY_COLUMNS)


def load_link_registry(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        return _empty_registry()
    registry = pd.read_csv(path, dtype=str).fillna("")
    for column in REGISTRY_COLUMNS:
        if column not in registry.columns:
            registry[column] = ""
    return registry[REGISTRY_COLUMNS].copy()


def _decode_atoms(value: str) -> set[str]:
    if not value:
        return set()
    try:
        return set(json.loads(value))
    except (TypeError, ValueError, json.JSONDecodeError):
        return set()


def _next_link_number(registry: pd.DataFrame) -> int:
    numbers = []
    for value in registry.get("LINK_ID", pd.Series(dtype=str)):
        match = re.fullmatch(r"LINK-(\d+)", str(value))
        if match:
            numbers.append(int(match.group(1)))
    return max(numbers, default=0) + 1


def assign_persistent_link_ids(
    clusters: list[dict], registry_path: str | Path
) -> pd.DataFrame:
    """Assign stable LINK IDs by matching real-atom membership to the registry.

    Matching is independent of PHYSICAL_SKU so a corrected size assignment does
    not rename an existing ecommerce link. Splits keep the old ID on the child
    with the strongest overlap; merges retain one prior ID and retire the rest.
    The returned registry is saved only after final pipeline validation.
    """
    registry = load_link_registry(registry_path)
    candidates = []
    for cluster in clusters:
        atoms = _atom_set(cluster)
        key = generate_cluster_key(cluster)
        candidates.append({
            "cluster": cluster,
            "atoms": atoms,
            "key": key,
            "atom_digest": hashlib.sha256("\n".join(sorted(atoms)).encode("utf-8")).hexdigest(),
        })

    active = []
    for _, row in registry[registry["STATUS"] == "ACTIVE"].iterrows():
        active.append({"link_id": row["LINK_ID"], "atoms": _decode_atoms(row["ATOM_KEYS_JSON"])})

    pairs = []
    for candidate_no, candidate in enumerate(candidates):
        for old_no, old in enumerate(active):
            intersection = len(candidate["atoms"] & old["atoms"])
            if not intersection:
                continue
            minimum = min(len(candidate["atoms"]), len(old["atoms"])) or 1
            union = len(candidate["atoms"] | old["atoms"]) or 1
            containment = intersection / minimum
            jaccard = intersection / union
            if containment >= 0.60:
                pairs.append((containment, jaccard, intersection, candidate_no, old_no))

    pairs.sort(
        key=lambda item: (
            -item[0], -item[1], -item[2],
            candidates[item[3]]["key"], candidates[item[3]]["atom_digest"],
            active[item[4]]["link_id"],
        )
    )
    candidate_match, old_match = {}, {}
    for _containment, _jaccard, _intersection, candidate_no, old_no in pairs:
        if candidate_no in candidate_match or old_no in old_match:
            continue
        candidate_match[candidate_no] = active[old_no]["link_id"]
        old_match[old_no] = candidate_no

    next_number = _next_link_number(registry)
    for candidate_no in sorted(
        range(len(candidates)),
        key=lambda i: (candidates[i]["key"], candidates[i]["atom_digest"]),
    ):
        if candidate_no not in candidate_match:
            candidate_match[candidate_no] = f"LINK-{next_number:06d}"
            next_number += 1

    current_rows = []
    for candidate_no, candidate in enumerate(candidates):
        cluster = candidate["cluster"]
        link_id = candidate_match[candidate_no]
        cluster["PROVISIONAL_CLUSTER_ID"] = cluster.get("CLUSTER_ID", "")
        cluster["CLUSTER_KEY"] = candidate["key"]
        cluster["LINK_ID"] = link_id
        cluster["CLUSTER_ID"] = link_id
        current_rows.append({
            "LINK_ID": link_id,
            "STATUS": "ACTIVE",
            "PHYSICAL_SKU": cluster.get("自动尺码", ""),
            "CLUSTER_KEY": candidate["key"],
            "ATOM_COUNT": str(len(candidate["atoms"])),
            "ATOM_KEYS_JSON": json.dumps(sorted(candidate["atoms"]), ensure_ascii=False),
            "MERGED_INTO": "",
        })

    current_ids = {row["LINK_ID"] for row in current_rows}
    historical_rows = []
    for _, row in registry.iterrows():
        if row["LINK_ID"] in current_ids:
            continue
        historical = row.to_dict()
        if historical.get("STATUS") == "ACTIVE":
            historical["STATUS"] = "RETIRED"
            old_atoms = _decode_atoms(historical.get("ATOM_KEYS_JSON", ""))
            best = None
            for candidate_no, candidate in enumerate(candidates):
                overlap = len(old_atoms & candidate["atoms"])
                if overlap and (best is None or overlap > best[0]):
                    best = (overlap, candidate_match[candidate_no])
            historical["MERGED_INTO"] = best[1] if best else ""
        historical_rows.append(historical)

    result = pd.DataFrame(current_rows + historical_rows, columns=REGISTRY_COLUMNS)
    return result.sort_values(["STATUS", "LINK_ID"], ascending=[True, True]).reset_index(drop=True)


def save_link_registry(registry: pd.DataFrame, path: str | Path) -> str:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    registry.to_csv(path, index=False, encoding="utf-8-sig")
    return str(path)
