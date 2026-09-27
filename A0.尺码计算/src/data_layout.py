"""A0 data/ 的维护资料布局：<国别>/<类别>/。

  当前规则.yaml  各国别当前生效的规则文件、尺码字段、参数文件（换版本只改这里）
  US/规则/    US 尺码匹配规则各版本
  US/参数/    尺码匹配参数
  US/店铺/    货架.yaml（店铺候选尺码与发货尺码）
  US/TRIM/    TrimList、审核、TRIM 值、ID 迁移、联网证据等 TRIM 匹配资料
  EU/规则/ EU/参数/ EU/研究/（当前已审核全量）
  RU/规则/ RU/参数/ RU/参考/（ozon映射）
  参考/       powerquery.md、插片必要性.md、新旧尺码对应等参考资料
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parents[1]
DATA = PROJECT / "data"
CURRENT_CONFIG = DATA / "当前规则.yaml"

US = DATA / "US"
SHELF_CONFIG = US / "店铺" / "货架.yaml"
TRIM_DIR = US / "TRIM"
EU_RESEARCH = DATA / "EU" / "研究" / "当前已审核全量.csv"


@dataclass(frozen=True)
class RegionConfig:
    rules: Path
    size_column: str
    parameters: Path


def current(region: str, config_path: Path = CURRENT_CONFIG) -> RegionConfig:
    """读取 当前规则.yaml 中某国别当前生效的规则、尺码字段与参数；文件缺失时报错。"""
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    entry = config.get(region) or {}
    missing = [key for key in ("规则", "尺码字段", "参数") if not str(entry.get(key) or "").strip()]
    if missing:
        raise ValueError(f"{config_path.name} 的 {region} 缺少 {', '.join(missing)}")
    result = RegionConfig(
        rules=(config_path.parent / str(entry["规则"]).strip()).resolve(),
        size_column=str(entry["尺码字段"]).strip(),
        parameters=(config_path.parent / str(entry["参数"]).strip()).resolve(),
    )
    for path in (result.rules, result.parameters):
        if not path.is_file():
            raise FileNotFoundError(f"{config_path.name} 的 {region} 指向的文件不存在：{path}")
    return result


def us_rules() -> Path:
    """当前 US 尺码规则。"""
    return current("US").rules
