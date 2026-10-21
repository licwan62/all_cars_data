"""旧分析脚本的路径与表结构适配（节点已迁入 nodes/，RU 全量表已改为 output/RU/全量/全量表.csv）。"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NODES = ROOT / "nodes"
A0 = NODES / "A0.尺码计算"
RU_RULES = A0 / "data" / "RU" / "规则"
RU_PARAMS = A0 / "data" / "RU" / "参数"
RU_FULL_TABLE = A0 / "output" / "RU" / "全量" / "全量表.csv"
DIMENSION_LIBRARY = NODES / "01.整理尺寸库" / "output" / "尺寸库.csv"
SHAPE_TABLE = NODES / "03.车形分类核定" / "output" / "车形分类.csv"
ATOM_SALES = NODES / "02.销量评估" / "output" / "原子销量.csv"

# 旧版 全量表_RU.csv 的列顺序；脚本按下标读取（row[9] 分类、row[10:14] 长宽高销量、row[20] 自动尺码、
# row[24] 候选、row[25] 原因、row[28] DIMENSION-ID）
LEGACY_RU_HEADER = [
    "MAKE", "MODEL", "TRIM", "版本", "结构", "CAB", "BED", "代际", "YEAR", "分类",
    "L-MM", "W-MM", "H-MM", "销量合计", "车形", "前宽-MM", "后宽-MM", "参考侧高", "插片指数", "等效长",
    "自动尺码", "OZON尺码", "发货尺码", "自动长度余量", "候选", "原因", "相差数值", "DIMENSION-CODE", "DIMENSION-ID",
]
# 旧列 → 现行全量表列；不在此表且现行表也没有的列（TRIM、前宽、后宽、等效长、DIMENSION-CODE）留空
RENAMED = {"销量合计": "尺寸组销量"}


def ru_rule(name: str) -> Path:
    return RU_RULES / name


def ru_param(name: str) -> Path:
    return RU_PARAMS / name


def legacy_ru_rows() -> list[list[str]]:
    """读现行 RU 全量表，按旧版 全量表_RU.csv 的列顺序返回行（不含表头）。"""
    with RU_FULL_TABLE.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return [[row.get(RENAMED.get(name, name)) or "" for name in LEGACY_RU_HEADER] for row in reader]
