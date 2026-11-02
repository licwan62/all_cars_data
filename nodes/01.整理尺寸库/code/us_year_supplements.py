"""Apply reviewed US model-year supplements; never interpolate missing dimensions."""
import copy
import hashlib
import math
from pathlib import Path
from urllib.parse import urlsplit

from id_scheme import append_country_code, dimension_id
from model_members import model_key, year_set

# approximate_add: usable but unconfirmed dimensions (conflicting sources, unstated or possibly
# mirror-inclusive width); added with a 待终核 iteration status so it can be rechecked later.
APPROX = "approximate_add"
ADDED = {"verified_add", APPROX}
REVIEW_FIELDS = ["MAKE", "MODEL", "YEAR", "处理结果", "DIMENSION-ID", "依据", "来源URL"]


def apply_supplements(rows, rules, project=None):
    result = copy.deepcopy(rows)
    review = []
    identities = {r["DIMENSION-ID"] for r in rows}
    covered = {(model_key(r["MAKE"]), model_key(r["MODEL"]), y) for r in rows for y in year_set(r["YEAR"])}
    seen = set()
    for item in rules["resolutions"]:
        cell = model_key(item["make"]), model_key(item["model"]), item["year"]
        if cell in seen:
            raise ValueError("补库任务重复")
        seen.add(cell)
        status = item["status"]
        if status not in {"verified_add", APPROX, "excluded_reference_year", "pending"}:
            raise ValueError("无效补库处理状态")
        if status != "pending" and not item.get("sources"):
            raise ValueError("补库/排除结论必须有来源")
        urls = [s["url"] for s in item.get("sources", [])]
        if any(urlsplit(url).scheme != "https" or not urlsplit(url).netloc for url in urls):
            raise ValueError("证据URL无效")
        for source in item.get("sources", []):
            if source.get("file"):
                if project is None:
                    raise ValueError("本地证据需要节点目录以验证SHA")
                data_root = (Path(project) / "data").resolve()
                evidence = (Path(project) / source["file"]).resolve()
                try:
                    evidence.relative_to(data_root)
                except ValueError as exc:
                    raise ValueError("本地证据必须位于节点data目录") from exc
                if hashlib.sha256(evidence.read_bytes()).hexdigest() != source.get("sha256"):
                    raise ValueError("本地证据SHA已变化；需重新核实")
        if status not in ADDED:
            review.append(dict(zip(REVIEW_FIELDS, [item["make"], item["model"], item["year"], status, "", item["reason"], "|".join(urls)])))
            continue
        if cell in covered:
            raise ValueError("补库任务与已有独立车型年重叠")
        spec = item["record"]
        if not spec.get("结构") or not spec.get("参考车型"):
            raise ValueError("补库必须明确车身及对应配置")
        if spec.get("代际") and not any(
            source.get("evidence_type") == "generation_continuity" and source.get("market") == "US"
            and source.get("year") == item["year"] and source.get("generation") == spec["代际"]
            for source in item["sources"]
        ):
            raise ValueError("补库代际缺少同年美国及库内编号依据")
        values = [float(spec[k]) for k in ("L-IN", "W-IN", "H-IN")]
        if any(not math.isfinite(v) or v <= 0 for v in values):
            raise ValueError("补库尺寸无效")
        expected = dict(zip(("L-IN", "W-IN", "H-IN"), values))
        for field, value in expected.items():
            if not any(s.get("market") == "US" and s.get("year") == item["year"]
                and (status == APPROX or s.get("width_basis") == "without_mirrors") and s.get("body") == spec["结构"]
                and field in s.get("dimensions", {}) and float(s["dimensions"][field]) == value
                for s in item["sources"]):
                raise ValueError(f"补库字段缺同年美国同车身证据：{field}")
        row = {key: "" for key in rows[0]}
        row.update(spec)
        if status == APPROX and not str(spec.get("迭代状态", "")).startswith("待终核"):
            raise ValueError("近似补库必须标注待终核迭代状态")
        row.update({"MAKE": item["make"], "MODEL": item["model"], "YEAR": str(item["year"]),
                    "迭代状态": spec["迭代状态"] if status == APPROX else "可入库"})
        row["DIMENSION-ID"] = append_country_code(dimension_id(row), "US")
        if row["DIMENSION-ID"] in identities:
            raise ValueError("补库身份冲突")
        identities.add(row["DIMENSION-ID"])
        covered.add(cell)
        result.append(row)
        review.append(dict(zip(REVIEW_FIELDS, [item["make"], item["model"], item["year"], status, row["DIMENSION-ID"], item["reason"], "|".join(urls)])))
    return result, review
