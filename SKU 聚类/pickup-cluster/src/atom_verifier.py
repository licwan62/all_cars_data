"""Strict candidate merge gate required by Group 合并逻辑.md."""
from copy import copy
from itertools import product
import pandas as pd

def _s(v):
    return "" if v is None or pd.isna(v) else str(v).strip()

def atom_key(make, model, version, year, cab, bed):
    return "|".join(_s(v) for v in (make, model, version, year, cab, bed))

def _values(row):
    return (_s(row.get("MAKE_NORMALIZED", row.get("MAKE", ""))),
            _s(row.get("MODEL_FAMILY", row.get("MODEL", ""))),
            _s(row.get("版本", "")), _s(row.get("CAB", "")), _s(row.get("BED", "")))

def expand_original_atoms(rows):
    atoms = set()
    for _, row in rows.iterrows():
        make, model, version, cab, bed = _values(row)
        if pd.isna(row.get("YEAR_START")) or pd.isna(row.get("YEAR_END")):
            continue
        for year in range(int(row["YEAR_START"]), int(row["YEAR_END"]) + 1):
            atoms.add(atom_key(make, model, version, year, cab, bed))
    return atoms

def build_atom_map(clusters):
    atom_map = {}
    for cluster in clusters:
        entry = {"CLUSTER_ID": cluster.get("CLUSTER_ID", ""),
                 "PHYSICAL_SKU": cluster.get("自动尺码", "")}
        for key in expand_original_atoms(cluster.get("rows", pd.DataFrame())):
            if entry not in atom_map.setdefault(key, []):
                atom_map[key].append(entry)
    return atom_map

def build_structure_map(atom_map):
    """Index ownership without YEAR, preserving VERSION+CAB+BED relationships."""
    result = {}
    for atom, owners in atom_map.items():
        make, model, version, _year, cab, bed = atom.split("|", 5)
        key = (make, model, version, cab, bed)
        bucket = result.setdefault(key, [])
        for owner in owners:
            if owner not in bucket:
                bucket.append(owner)
    return result

def expand_candidate_atoms(rows, year_ranges=None):
    if rows.empty:
        return set()
    vals = [_values(row) for _, row in rows.iterrows()]
    make_models, versions = sorted({v[:2] for v in vals}), sorted({v[2] for v in vals})
    cabs, beds = sorted({v[3] for v in vals}), sorted({v[4] for v in vals})
    if year_ranges is None:
        from year_parser import merge_year_ranges
        year_ranges = merge_year_ranges([(int(r["YEAR_START"]), int(r["YEAR_END"]))
            for _, r in rows.iterrows() if pd.notna(r.get("YEAR_START")) and pd.notna(r.get("YEAR_END"))])
    atoms = set()
    for (make, model), version, cab, bed in product(make_models, versions, cabs, beds):
        for start, end in year_ranges:
            for year in range(int(start), int(end) + 1):
                atoms.add(atom_key(make, model, version, year, cab, bed))
    return atoms

def verify_candidate(rows, target_sku, atom_map, cluster_id="", year_ranges=None,
                     structure_map=None):
    """Verify only facts that actually exist in ``atom_map``.

    Cartesian combinations produced by a broad consumer name are allowed when
    no source atom exists for them.  A candidate is rejected only when an
    existing atom crosses a physical-SKU boundary or an existing atom already
    has more than one source CLUSTER_ID.
    """
    original = expand_original_atoms(rows)
    expanded = expand_candidate_atoms(rows, year_ranges)
    conflicts = multi = unresolved = inferred = 0
    samples, conflict_atoms, unresolved_samples = [], [], []
    for key in sorted(expanded):
        owners = atom_map.get(key, [])
        if not owners:
            # A generated combination that has no real source fact is allowed.
            # It is diagnostic inference only and cannot create an ownership
            # conflict by itself.
            inferred += 1
            continue
        skus = {o["PHYSICAL_SKU"] for o in owners}
        if skus != {target_sku}:
            conflicts += 1
            conflict_atoms.append(key)
            if len(samples) < 5: samples.append(key)
        elif len({o["CLUSTER_ID"] for o in owners}) > 1:
            multi += 1
    if conflicts:
        status, reason = "REJECT", f"PHYSICAL_SKU conflict: {conflicts} atoms cross SKU boundary"
    elif multi:
        status, reason = "REJECT", f"REAL_ATOM_NON_UNIQUE: {multi} atoms map to multiple CLUSTER_IDs"
    else:
        status, reason = "ACCEPT", ""
    return {
        "ORIGINAL_ATOM_COUNT": len(original), "EXPANDED_ATOM_COUNT": len(expanded),
        "NEW_ATOM_COUNT": len(expanded - original),
        "EXISTING_ATOM_COUNT": len(expanded & set(atom_map)),
        "UNRESOLVED_NEW_ATOM_COUNT": unresolved,
        "INFERRED_NEW_ATOM_COUNT": inferred,
        "INFERRED_CLUSTER_ID": cluster_id if inferred else "",
        "MULTI_CLUSTER_ATOM_COUNT": multi,
        "PHYSICAL_SKU_CONFLICT_ATOM_COUNT": conflicts,
        "TARGET_PHYSICAL_SKU": target_sku, "MERGE_STATUS": status,
        "REJECT_REASON": reason, "CONFLICT_ATOM_SAMPLES": "; ".join(samples),
        "CONFLICT_ATOMS": "; ".join(conflict_atoms),
        "UNRESOLVED_ATOM_SAMPLES": "; ".join(unresolved_samples),
    }


def verify_unique_real_atom_ownership(clusters):
    """Ensure every real source atom is owned by exactly one final cluster.

    Candidate-name Cartesian coverage is deliberately excluded here: generated
    combinations do not remap source facts. Ownership comes only from the
    original rows carried by each final cluster.
    """
    atom_map = build_atom_map(clusters)
    real_atoms = set(atom_map)
    ownership = {
        key: {owner["CLUSTER_ID"] for owner in owners}
        for key, owners in atom_map.items()
    }
    non_unique = {key: cids for key, cids in ownership.items() if len(cids) != 1}
    samples = [f"{key} => {','.join(sorted(cids))}" for key, cids in non_unique.items()]
    status = "REJECT" if non_unique else "ACCEPT"
    reason = (
        f"REAL_ATOM_NON_UNIQUE: {len(non_unique)} atoms do not map to exactly one final CLUSTER_ID"
        if non_unique else ""
    )
    return {
        "ORIGINAL_ATOM_COUNT": len(real_atoms),
        "EXPANDED_ATOM_COUNT": len(real_atoms),
        "NEW_ATOM_COUNT": 0,
        "EXISTING_ATOM_COUNT": len(real_atoms),
        "UNRESOLVED_NEW_ATOM_COUNT": 0,
        "INFERRED_NEW_ATOM_COUNT": 0,
        "INFERRED_CLUSTER_ID": "",
        "MULTI_CLUSTER_ATOM_COUNT": len(non_unique),
        "PHYSICAL_SKU_CONFLICT_ATOM_COUNT": 0,
        "TARGET_PHYSICAL_SKU": "",
        "MERGE_STATUS": status,
        "REJECT_REASON": reason,
        "CONFLICT_ATOM_SAMPLES": "; ".join(samples[:5]),
        "CONFLICT_ATOMS": "; ".join(sorted(non_unique)),
        "UNRESOLVED_ATOM_SAMPLES": "",
    }


def verify_unique_real_atom_title_coverage(clusters):
    """Ensure expanded final titles cover each real atom exactly once."""
    atom_map = build_atom_map(clusters)
    real_atoms = set(atom_map)
    coverage = {key: set() for key in real_atoms}
    expanded_total = 0
    for cluster in clusters:
        cid = cluster.get("CLUSTER_ID", "")
        expanded = expand_candidate_atoms(
            cluster.get("rows", pd.DataFrame()), cluster.get("_optimized_ranges")
        )
        expanded_total += len(expanded)
        for key in expanded & real_atoms:
            coverage[key].add(cid)

    non_unique = {key: cids for key, cids in coverage.items() if len(cids) != 1}
    samples = [f"{key} => {','.join(sorted(cids))}" for key, cids in non_unique.items()]
    status = "REJECT" if non_unique else "ACCEPT"
    reason = (
        f"REAL_ATOM_TITLE_COVERAGE_NON_UNIQUE: {len(non_unique)} atoms are covered by multiple final titles"
        if non_unique else ""
    )
    return {
        "ORIGINAL_ATOM_COUNT": len(real_atoms),
        "EXPANDED_ATOM_COUNT": expanded_total,
        "NEW_ATOM_COUNT": 0,
        "EXISTING_ATOM_COUNT": len(real_atoms),
        "UNRESOLVED_NEW_ATOM_COUNT": 0,
        "INFERRED_NEW_ATOM_COUNT": 0,
        "INFERRED_CLUSTER_ID": "",
        "MULTI_CLUSTER_ATOM_COUNT": len(non_unique),
        "PHYSICAL_SKU_CONFLICT_ATOM_COUNT": 0,
        "TARGET_PHYSICAL_SKU": "",
        "MERGE_STATUS": status,
        "REJECT_REASON": reason,
        "CONFLICT_ATOM_SAMPLES": "; ".join(samples[:5]),
        "CONFLICT_ATOMS": "; ".join(sorted(non_unique)),
        "UNRESOLVED_ATOM_SAMPLES": "",
    }


def _overlapping_real_atoms(groups, real_atoms):
    coverage = {}
    for group_no, rows in enumerate(groups):
        for key in expand_candidate_atoms(rows) & real_atoms:
            coverage.setdefault(key, set()).add(group_no)
    return {key: owners for key, owners in coverage.items() if len(owners) > 1}


def _partition_by_exact_structure(rows):
    """Safe fallback: one group per exact VERSION+CAB+BED relationship."""
    columns = ["MAKE_NORMALIZED", "MODEL_FAMILY", "版本", "CAB", "BED"]
    ordered = rows.sort_values(columns + ["YEAR_START", "YEAR_END"])
    return [group.copy() for _, group in ordered.groupby(columns, dropna=False, sort=True)]

def _refresh(base, rows, cid):
    c = copy(base); c["rows"] = rows.copy(); c["CLUSTER_ID"] = cid
    c["makes"] = sorted(rows["MAKE_NORMALIZED"].dropna().unique())
    c["models"] = sorted(rows["MODEL_FAMILY"].dropna().unique())
    cab_groups = sorted(rows["CAB_GROUP"].dropna().unique())
    bed_groups = sorted(rows["BED_GROUP"].dropna().unique())
    c["CAB_GROUP"] = cab_groups[0] if len(cab_groups) == 1 else "MIXED"
    c["BED_GROUP"] = bed_groups[0] if len(bed_groups) == 1 else "MIXED"
    c["fitment_count"] = len(rows); c["estimated_sales"] = rows["预估销量 的总和"].sum()
    c["year_min"] = int(rows["YEAR_START"].min()); c["year_max"] = int(rows["YEAR_END"].max())
    for p, col in (("l", "L-MM"), ("w", "W-MM"), ("h", "H-MM")):
        c[p+"_min"], c[p+"_max"] = rows[col].min(), rows[col].max()
        c[p+"_spread"] = c[p+"_max"] - c[p+"_min"]
    c["length_margin_min"] = rows["自动长度余量"].min()
    c["length_margin_median"] = rows["自动长度余量"].median()
    for key in ("_split_names", "_split_cluster_map", "_diagnostics", "CONSUMER_NAME",
                "CONSUMER_NAME_OPTIMIZED", "MAIN_PART", "ADDITION_PART"):
        c.pop(key, None)
    return c

def build_verified_candidates(clusters):
    """Merge rows only after candidate expansion passes the P0 gate."""
    atom_map, final, audit = build_atom_map(clusters), [], []
    structure_map = build_structure_map(atom_map)
    for base in clusters:
        groups = []
        ordered = base["rows"].sort_values(
            ["MAKE_NORMALIZED", "MODEL_FAMILY", "YEAR_START", "CAB", "BED"])
        for _, row in ordered.iterrows():
            unit, best = row.to_frame().T, None
            for i, group in enumerate(groups):
                combined = pd.concat([group, unit])
                pairs = set(zip(combined["MAKE_NORMALIZED"], combined["MODEL_FAMILY"]))
                if len(pairs) != 1: continue
                diag = verify_candidate(combined, base["自动尺码"], atom_map,
                                        base["CLUSTER_ID"], structure_map=structure_map)
                audit.append({"BASE_CLUSTER_ID": base["CLUSTER_ID"], "CANDIDATE_ROW_COUNT": len(combined), **diag})
                if diag["MERGE_STATUS"] == "REJECT": continue
                score = (len(expand_candidate_atoms(combined)), -len(group))
                if best is None or score < best[0]: best = (score, i, combined)
            if best is None:
                groups.append(unit)
            else:
                groups[best[1]] = best[2]
        overlaps = _overlapping_real_atoms(groups, set(atom_map))
        if overlaps:
            audit.append({
                "BASE_CLUSTER_ID": base["CLUSTER_ID"],
                "CANDIDATE_TYPE": "REAL_ATOM_COVERAGE_REPARTITION",
                "CANDIDATE_ROW_COUNT": len(base["rows"]),
                "ORIGINAL_ATOM_COUNT": len(expand_original_atoms(base["rows"])),
                "EXPANDED_ATOM_COUNT": sum(len(expand_candidate_atoms(g)) for g in groups),
                "NEW_ATOM_COUNT": 0,
                "EXISTING_ATOM_COUNT": len(expand_original_atoms(base["rows"])),
                "UNRESOLVED_NEW_ATOM_COUNT": 0,
                "INFERRED_NEW_ATOM_COUNT": 0,
                "INFERRED_CLUSTER_ID": "",
                "MULTI_CLUSTER_ATOM_COUNT": len(overlaps),
                "PHYSICAL_SKU_CONFLICT_ATOM_COUNT": 0,
                "TARGET_PHYSICAL_SKU": base["自动尺码"],
                "MERGE_STATUS": "REPARTITION",
                "REJECT_REASON": f"{len(overlaps)} real atoms covered by multiple candidate titles",
                "CONFLICT_ATOM_SAMPLES": "; ".join(sorted(overlaps)[:5]),
                "CONFLICT_ATOMS": "; ".join(sorted(overlaps)),
                "UNRESOLVED_ATOM_SAMPLES": "",
            })
            groups = _partition_by_exact_structure(base["rows"])
        multiple = len(groups) > 1
        for n, rows in enumerate(groups, 1):
            cid = f"{base['CLUSTER_ID']}__M{n:02d}" if multiple else base["CLUSTER_ID"]
            c = _refresh(base, rows, cid)
            c["_diagnostics"] = verify_candidate(rows, base["自动尺码"], atom_map, cid,
                                                  structure_map=structure_map)
            c["MERGE_STATUS"] = c["_diagnostics"]["MERGE_STATUS"]
            final.append(c)
    return final, audit

def verify_all_clusters(clusters):
    atom_map = build_atom_map(clusters)
    for c in clusters:
        d = verify_candidate(c["rows"], c.get("自动尺码", ""), atom_map,
                             c.get("CLUSTER_ID", ""), c.get("_optimized_ranges"))
        c["_diagnostics"], c["MERGE_STATUS"] = d, d["MERGE_STATUS"]
    return clusters
