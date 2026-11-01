"""Apply evidence-backed corrections without changing vehicle identities."""

import copy
from urllib.parse import urlsplit


def apply_corrections(rows, rules):
    result = copy.deepcopy(rows)
    seen = set()
    for correction in rules["corrections"]:
        identity = correction["DIMENSION-ID"]
        if identity in seen:
            raise ValueError("重复的美国尺寸修正规则")
        seen.add(identity)
        matches = [row for row in result if row["DIMENSION-ID"] == identity]
        if len(matches) != 1:
            raise ValueError("美国尺寸修正规则必须匹配唯一身份")
        row = matches[0]
        if any(row.get(field) != value for field, value in correction["expected"].items()):
            raise ValueError("美国尺寸修正前置条件不匹配，须重新审核")
        changes = correction["changes"]
        if not changes or not set(changes).issubset({"L-IN", "W-IN", "H-IN", "备注"}):
            raise ValueError("美国尺寸修正只允许修改尺寸及备注")
        if not correction.get("reason") or not correction.get("sources"):
            raise ValueError("美国尺寸修正缺少依据")
        for source in correction["sources"]:
            url = urlsplit(source["url"])
            if url.scheme != "https" or not url.netloc:
                raise ValueError("美国尺寸修正来源URL无效")
        row.update(changes)
    return result
