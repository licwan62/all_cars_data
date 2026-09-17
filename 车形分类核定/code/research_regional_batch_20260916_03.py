from sync_regional_data import SHAPE_PROJECT, run


BATCH = SHAPE_PROJECT / "artifacts" / "2026-09-16_03_regional-shape-research"

# 仅覆盖车型键内车身轮廓单一、且官方资料足以支持跨区域继承的对象。
RESEARCHED_RULES = [
    {
        "MAKE": "BMW", "MODEL": "7", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://www.press.bmwgroup.com/global/article/detail/T0380173EN/the-new-bmw-7-series",
        "note": "BMW 官方历代资料把 7 系列作为大型豪华轿车连续谱系展示。各代均为标准三厢比例，车头、翼子板和座舱存在正常收窄；没有 SD2 所要求的极端宽方、近矩形俯视轮廓，也不是 SD0 的低矮运动轮廓，严格归 SD1。",
    },
    {
        "MAKE": "Alfa Romeo", "MODEL": "Spider", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD0",
        "source_url": "https://www.media.stellantis.com/uk-en/alfa-romeo/press/alfa-romeo-roads-of-emotion-at-retromobile-2026",
        "note": "Alfa Romeo 官方回顾确认 Spider 是低矮双座敞篷跑车。长车头、低座舱、明显向后收束的运动轮廓符合低矮运动型 Sedan/Coupe 定义；开顶形式不改变基础外廓，归 SD0。",
    },
    {
        "MAKE": "Ford", "MODEL": "Fiesta vi", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H0",
        "source_url": "https://media.ford.com/content/dam/fordmedia/Europe/en/2016/11/GF3/NEXT_GEN_FIESTA_TECH_SPEC.pdf",
        "note": "Ford 官方技术资料对应五门 Fiesta 两厢车。其低矮紧凑车身、斜前挡、短尾门和较早下落的后车顶符合 Compact/Sloping Hatch；不具备 H1 的高方座舱，归 H0。",
    },
    {
        "MAKE": "Lexus", "MODEL": "Ls", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://global.toyota/en/detail/19202496",
        "note": "Lexus 官方资料显示 LS 为大型四门轿车，采用低车顶、长轴距和流线三厢轮廓。车头与座舱仍有现代圆角和正常收窄，不满足 SD2 极端方正条件，归 SD1。",
    },
    {
        "MAKE": "Peugeot", "MODEL": "205 ii", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H0",
        "source_url": "https://www.media.stellantis.com/uk-en/peugeot/press/the-peugeot-205-is-turning-40-an-alluring-sacred-number",
        "note": "Peugeot 官方将 205 定义为紧凑实用的 hatchback。源模型键为普通 205 II 两厢分支，车身低矮、后悬短且尾门随车顶下落，不是 H1 高方两厢，归 H0。",
    },
    {
        "MAKE": "Lexus", "MODEL": "Es", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://global.toyota/en/newsroom/lexus/35079970.html",
        "note": "Lexus 官方资料显示 ES 为低重心四门轿车，具有流线车顶与常规前后收窄。其轮廓既非 SD0 的低矮双门运动型，也没有 SD2 的极端宽方特征，严格归 SD1。",
    },
]


if __name__ == "__main__":
    run(BATCH, RESEARCHED_RULES)
