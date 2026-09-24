from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SOURCE = REPO / "B0.差评分析" / "output" / "差评分析表.csv"
INPUT = HERE / "list.csv"
OUTPUT = HERE / "美国差评风险分析.csv"
REPORT = HERE / "美国差评风险分析.md"

LEVEL = {"": 0, "低": 1, "中": 2, "高": 3}
SIZE_TERMS = ("尺寸", "太小", "偏小", "太大", "偏大", "太短", "偏短", "短(", "小(", "紧")


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def target_identity(text: str) -> tuple[str, str, str]:
    raw = text.strip()
    low = raw.lower()
    brand_aliases = {
        "chevy": "Chevrolet", "mercedes-benz": "Mercedes-benz",
        "gmc": "GMC", "bmw": "BMW", "ram": "Ram",
    }
    first = low.split()[0]
    brand = brand_aliases.get(first, raw.split()[0].title())

    patterns = [
        (r"silverado", "Silverado"), (r"sierra", "Sierra"),
        (r"f-150", "F-150"), (r"f-100", "F-100"), (r"c10", "C10"),
        (r"grand cherokee", "Grand Cherokee"), (r"wrangler", "Wrangler"),
        (r"corvette", "Corvette"), (r"camaro", "Camaro"),
        (r"challenger", "Challenger"), (r"charger", "Charger"),
        (r"bronco", "Bronco"), (r"mustang mach-e", "Mustang Mach-E"),
        (r"mustang", "Mustang"), (r"civic", "Civic"),
        (r"accord", "Accord"), (r"crv", "CRV"),
        (r"ioniq 5", "IONIQ 5"), (r"350z/370z", "350Z/370Z"),
        (r"rav4", "RAV4"), (r"4runner", "4Runner"),
    ]
    model = ""
    for pattern, canonical in patterns:
        if re.search(pattern, low):
            model = canonical
            break
    if not model:
        # Remove brand and pickup configuration/year suffixes.
        rest = raw[len(raw.split()[0]):].strip()
        rest = re.sub(r"\s+(?:SuperCrew|Regular|SuperCab|Crew|Extended/Double|Extended|Double|Club/Quad|Access/Regular)\b.*$", "", rest, flags=re.I)
        rest = re.sub(r"\s+\d{4}(?:-\d{4})?$", "", rest)
        rest = re.sub(r"\s+(?:sedan|hatchback)$", "", rest, flags=re.I)
        model = rest.strip()

    structure = ""
    if "hatchback" in low:
        structure = "Hatchback"
    elif "sedan" in low:
        structure = "Sedan"
    elif any(x in low for x in ("cab", "silverado", "sierra", "tacoma", "f-100", "f-150", "c10")):
        structure = "Pickup"
    return brand, model, structure


def model_matches(target_model: str, review_model: str) -> bool:
    t, r = norm(target_model), norm(review_model)
    if t == "350z370z":
        return r in {"350z", "370z"}
    if t == "crv":
        return r == "crv"
    return t == r


def size_clues(reason: str) -> int:
    total = 0
    for chunk in (reason or "").split("；"):
        if any(term in chunk for term in SIZE_TERMS):
            match = re.search(r"\((\d+)\)", chunk)
            total += int(match.group(1)) if match else 1
    return total


def size_status(selected: str, recorded: str) -> str:
    tokens = [x.strip() for x in re.split(r"[；;]", recorded) if x.strip()]
    if not tokens:
        return "无已登记尺码可核对"
    if selected == "定制":
        if any(any(k in x for k in ("定制", "重做", "等待")) for x in tokens):
            return "定制方向一致"
        return "历史记录为通用尺码，需核对定制是否已规避"
    if selected in tokens:
        return "与历史记录尺码一致"
    return "尺码口径不一致（需人工核对）"


def main() -> None:
    with INPUT.open(encoding="utf-8-sig", newline="") as f:
        targets = list(csv.DictReader(f))
    with SOURCE.open(encoding="utf-8-sig", newline="") as f:
        reviews = list(csv.DictReader(f))

    results = []
    for target in targets:
        brand, model, structure = target_identity(target["车型"])
        matched = [r for r in reviews if norm(r["品牌"]) == norm(brand) and model_matches(model, r["车型"])]
        if structure:
            matched = [r for r in matched if norm(r["结构"]).startswith(norm(structure))]

        if not matched:
            results.append({
                **target, "匹配状态": "未匹配到B0差评记录", "匹配车型": "", "匹配结构": "",
                "风险等级": "未覆盖", "差评记录数": "0", "尺寸问题线索数_非去重": "0",
                "历史登记尺码": "", "尺码核对": "无法核对", "主要风险原因": "",
                "年份证据": "", "判断": "当前台账无该车型记录，不等于零风险",
            })
            continue

        highest = max(matched, key=lambda r: LEVEL.get(r["严重度评级"], 0))["严重度评级"]
        count = sum(int(r["差评数量"] or 0) for r in matched)
        clues = sum(size_clues(r["主要差评原因"]) for r in matched)
        sizes = "；".join(dict.fromkeys(x for r in matched for x in re.split(r"[；;]", r["尺码"]) if x))
        reasons = " | ".join(dict.fromkeys(r["主要差评原因"] for r in matched if r["主要差评原因"]))
        years = ",".join(dict.fromkeys(x for r in matched for x in r["年份"].split(",") if x))
        size_check = size_status(target["尺码"], sizes)
        judgment = f"有{highest}风险；B0已登记{count}条差评"
        if clues:
            judgment += f"，其中尺寸相关线索{clues}次（原因标签非去重）"
        if "不一致" in size_check or "需核对" in size_check:
            judgment += "；当前匹配尺码需复核"
        results.append({
            **target, "匹配状态": "已匹配", "匹配车型": "；".join(dict.fromkeys(f'{r["品牌"]} {r["车型"]}' for r in matched)),
            "匹配结构": "；".join(dict.fromkeys(r["结构"] for r in matched)), "风险等级": highest,
            "差评记录数": str(count), "尺寸问题线索数_非去重": str(clues), "历史登记尺码": sizes,
            "尺码核对": size_check, "主要风险原因": reasons, "年份证据": years, "判断": judgment,
        })

    fields = list(results[0])
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    counts = Counter(r["风险等级"] for r in results)
    matched = [r for r in results if r["匹配状态"] == "已匹配"]
    conflicts = [r for r in matched if "不一致" in r["尺码核对"] or "需核对" in r["尺码核对"]]
    high = [r for r in matched if r["风险等级"] == "高"]
    medium = [r for r in matched if r["风险等级"] == "中"]
    lines = [
        "# 美国差评风险分析", "", 
        f"- 分析对象：`list.csv` 共 {len(results)} 行。",
        f"- 当前 B0 差评台账匹配 {len(matched)} 行；高风险 {counts['高']} 行，中风险 {counts['中']} 行，低风险 {counts['低']} 行，未覆盖 {counts['未覆盖']} 行。",
        "- 风险等级直接沿用 `B0.差评分析/output/差评分析表.csv` 的现有评级；未匹配表示台账未覆盖，不表示零风险。",
        "- `尺寸问题线索数_非去重` 是原因标签后的次数之和，同一差评可能贡献多个标签，只用于排序，不当作独立差评数。",
        "", "## 优先关注（高风险）", "",
    ]
    lines.extend(f"- {r['车型']} / {r['尺码']}：{r['差评记录数']} 条；{r['主要风险原因']}；{r['尺码核对']}" for r in high)
    lines += ["", "## 次优先（中风险）", ""]
    lines.extend(f"- {r['车型']} / {r['尺码']}：{r['差评记录数']} 条；{r['主要风险原因']}；{r['尺码核对']}" for r in medium)
    lines += ["", "## 尺码需复核", ""]
    lines.extend(f"- {r['车型']}：当前 {r['尺码']}；历史 {r['历史登记尺码'] or '空'}；{r['风险等级']}风险" for r in conflicts)
    lines += ["", "完整逐行证据见 `美国差评风险分析.csv`。", ""]
    REPORT.write_text("\n".join(lines), encoding="utf-8-sig")

    print(f"wrote {OUTPUT.name}: {len(results)} rows")
    print(f"matched={len(matched)} high={counts['高']} medium={counts['中']} low={counts['低']} uncovered={counts['未覆盖']}")
    print(f"size_review={len(conflicts)}")


if __name__ == "__main__":
    main()
