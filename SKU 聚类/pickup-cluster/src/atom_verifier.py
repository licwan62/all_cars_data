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
    original = expand_original_atoms(rows)
    expanded = expand_candidate_atoms(rows, year_ranges)
    structure_map = structure_map or build_structure_map(atom_map)
    conflicts = multi = unresolved = inferred = 0
    samples, unresolved_samples = [], []
    for key in expanded:
        owners = atom_map.get(key, [])
        if not owners:
            make, model, version, _year, cab, bed = key.split("|", 5)
            owners = structure_map.get((make, model, version, cab, bed), [])
            if not owners:
                unresolved += 1
                if len(unresolved_samples) < 5: unresolved_samples.append(key)
                continue
            skus = {o["PHYSICAL_SKU"] for o in owners}
            # The exact atom does not exist, so historical ownership of this
            # structure by another SKU is not an atom conflict. If the target
            # SKU has established the structure, the missing year is a safe
            # expansion. Exact atoms owned by another SKU are still rejected
            # in the branch below.
            if target_sku not in skus:
                conflicts += 1
                if len(samples) < 5: samples.append(key)
                continue
            inferred += 1
            target_cids = {o["CLUSTER_ID"] for o in owners
                           if o["PHYSICAL_SKU"] == target_sku}
            if len(target_cids) > 1:
                multi += 1
            continue
        skus = {o["PHYSICAL_SKU"] for o in owners}
        if skus != {target_sku}:
            conflicts += 1
            if len(samples) < 5: samples.append(key)
        elif len({o["CLUSTER_ID"] for o in owners}) > 1:
            multi += 1
    if conflicts:
        status, reason = "REJECT", f"PHYSICAL_SKU conflict: {conflicts} atoms cross SKU boundary"
    elif unresolved:
        status, reason = "REJECT", f"UNRESOLVED_NEW_ATOM: {unresolved} atoms introduce unsupported VERSION/CAB/BED combinations"
    elif multi:
        status, reason = "REVIEW", f"{multi} atoms map to multiple CLUSTER_IDs (same SKU)"
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
        "UNRESOLVED_ATOM_SAMPLES": "; ".join(unresolved_samples),
    }

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
    for key in ("_split_names", "_split_cluster_map", "_diagnostics", "CONSUMER_NAME", "CONSUMER_NAME_OPTIMIZED"):
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
