"""身份承接检查：下游交付物的业务主键是否完整承接上游当前已发布的身份。

``pipeline.json`` 节点的 ``identity_coverage`` 声明本节点哪些交付物必须承接哪个上游交付物的主键::

    "identity_coverage": [
      {"output": "车型结构_US.csv", "upstream": "dimension-library", "file": "尺寸库_US.csv"},
      {"output": "原子销量.csv", "key": "atom_record_id", "key_split": "|",
       "upstream": "dimension-library", "file": "尺寸库_US.csv"},
      {"output": "US/压缩来源.csv", "upstream": "size-calculation", "file": "US/全量/全量表.csv", "mode": "subset"}
    ]

- ``key``/``upstream_key`` 默认 ``DIMENSION-ID``；``key_split`` 给出时取分隔符之前的部分作为身份（如原子销量的
  ``<DIMENSION-ID>|ATOM_YEAR=2025``）。
- ``mode``：``equal``（默认）要求两边身份集合相同，列出缺失（上游有、本节点没有）与残留（本节点有、上游已无）；
  ``subset`` 只要求本节点身份都仍存在于上游（允许按业务规则只取一部分），只列残留。
- 上游 01 的身份承接资料（拆分、合并、撤回）接入后，在此处按承接关系解释差异；当前所有差异都需处理或说明。

检查只读两边当前 ``output/`` 文件，不读取 artifacts。
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_KEY = "DIMENSION-ID"
MODES = {"equal", "subset"}
EXAMPLES = 5


@dataclass
class CoverageGap:
    output: str
    upstream: str
    upstream_path: str
    file: str
    mode: str
    missing: list[str] = field(default_factory=list)
    residual: list[str] = field(default_factory=list)
    error: str = ""

    @property
    def ok(self) -> bool:
        return not (self.error or self.missing or self.residual)

    def describe(self) -> str:
        source = f"{self.upstream_path}/output/{self.file}"
        if self.error:
            return f"{self.output} 无法核对身份承接（{source}）：{self.error}"
        parts = []
        if self.missing:
            parts.append(f"缺 {len(self.missing)} 个上游当前身份（如 {'；'.join(self.missing[:EXAMPLES])}）")
        if self.residual:
            parts.append(f"保留 {len(self.residual)} 个上游已不存在的身份（如 {'；'.join(self.residual[:EXAMPLES])}）")
        return f"{self.output} 未完整承接 {source}：" + "，".join(parts)

    def to_record(self) -> dict:
        return {
            "output": self.output, "upstream": self.upstream, "file": self.file, "mode": self.mode,
            "missing": len(self.missing), "residual": len(self.residual),
            "missing_examples": self.missing[:EXAMPLES], "residual_examples": self.residual[:EXAMPLES],
            **({"error": self.error} if self.error else {}),
        }


def read_keys(path: Path, key: str, split: str | None = None) -> set[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if key not in (reader.fieldnames or []):
            raise ValueError(f"{path.name} 缺少主键列 {key}")
        values = (row[key] for row in reader)
        return {value.split(split, 1)[0] if split else value for value in values if value}


def check_rule(root: Path, node: dict, rule: dict, by_id: dict[str, dict]) -> CoverageGap:
    upstream = by_id[rule["upstream"]]
    mode = rule.get("mode", "equal")
    gap = CoverageGap(rule["output"], upstream["id"], upstream["path"], rule["file"], mode)
    own = root / node["path"] / "output" / rule["output"]
    source = root / upstream["path"] / "output" / rule["file"]
    try:
        own_keys = read_keys(own, rule.get("key", DEFAULT_KEY), rule.get("key_split"))
        source_keys = read_keys(source, rule.get("upstream_key", DEFAULT_KEY))
    except (OSError, ValueError) as error:
        gap.error = str(error)
        return gap
    if mode == "equal":
        gap.missing = sorted(source_keys - own_keys)
    gap.residual = sorted(own_keys - source_keys)
    return gap


def check_node(root: Path, node: dict, by_id: dict[str, dict]) -> list[CoverageGap]:
    """返回本节点全部承接规则的检查结果（含通过项）。"""
    return [check_rule(root, node, rule, by_id) for rule in node.get("identity_coverage", [])]


def validate_rules(nodes: list[dict]) -> list[str]:
    """结构校验：规则字段完整、上游已声明、output 已登记、模式合法。"""
    errors = []
    for node in nodes:
        for index, rule in enumerate(node.get("identity_coverage", [])):
            label = f"{node['id']}: identity_coverage[{index}]"
            missing = [name for name in ("output", "upstream", "file") if not rule.get(name)]
            if missing:
                errors.append(f"{label} 缺少 {', '.join(missing)}")
                continue
            if rule["upstream"] not in node.get("upstream", []):
                errors.append(f"{label} 的上游 {rule['upstream']} 不是本节点已声明的上游")
            if rule["output"] not in node.get("outputs", []):
                errors.append(f"{label} 的 {rule['output']} 不在本节点 outputs")
            if rule.get("mode", "equal") not in MODES:
                errors.append(f"{label} 的 mode 只能是 {'/'.join(sorted(MODES))}")
    upstream_outputs = {other["id"]: set(other.get("outputs", [])) for other in nodes}
    for node in nodes:
        for index, rule in enumerate(node.get("identity_coverage", [])):
            files = upstream_outputs.get(rule.get("upstream"), set())
            if rule.get("file") and rule.get("upstream") in upstream_outputs and rule["file"] not in files:
                errors.append(f"{node['id']}: identity_coverage[{index}] 引用的 {rule['file']} 不在上游 outputs")
    return errors
