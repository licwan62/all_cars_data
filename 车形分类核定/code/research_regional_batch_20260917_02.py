from sync_regional_data import SHAPE_PROJECT, run


BATCH = SHAPE_PROJECT / "artifacts" / "2026-09-17_02_regional-shape-research"

# 本批只覆盖结构单一且官方资料可确认轮廓边界的区域模型键。
RESEARCHED_RULES = [
    {
        "MAKE": "Mitsubishi", "MODEL": "Colt vi", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H1",
        "source_url": "https://www.mitsubishi-motors.com/en/company/history/car/?MID=21",
        "note": "Mitsubishi 官方车型史将该代 Colt 标为 Hatchback，并强调 one-motion form；官方尺寸与侧视显示高 CAB、短机舱、较平长车顶和接近直立的尾门。其轮廓不符合 H0 的低矮早落顶，更接近 Tall Box Hatch，归 H1。",
    },
    {
        "MAKE": "Opel", "MODEL": "Corsa a cc", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H0",
        "source_url": "https://www.media.stellantis.com/em-en/opel/press/40-years-of-opel-corsa-a-success-story-in-six-acts",
        "note": "Opel 官方回顾确认 Corsa A 的两门和五门 Hatchback，并给出 3.62 米紧凑车长、低风阻和紧凑比例。其低 CAB、短尾与后顶下落不具 H1 高方盒体，归 H0。",
    },
    {
        "MAKE": "Renault", "MODEL": "Super 5", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H0",
        "source_url": "https://www.renaultgroup.com/en/magazine/our-group-news/renault-5-gt-turbo-30-years-really/",
        "note": "Renault 官方资料确认 1984 Supercinq 延续 Renault 5 的紧凑两厢轮廓，普通版与 GT Turbo 共用基本车身。侧视为低矮短尾 Hatchback，不满足 H1 的高 CAB、平顶直尾条件，归 H0。",
    },
    {
        "MAKE": "Audi", "MODEL": "90", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://www.audi-mediacenter.com/en/publications/more/audi-anniversary-dates-2021-1016/download",
        "note": "Audi Tradition 资料确认 Audi 90 是 Audi 80 B2/B3/B4 体系中的高配三厢姊妹车型。虽具有年代化直线造型，但车头与座舱仍正常收窄，缺少 SD2 极端宽方前部证据，也不属于低矮运动型，归 SD1。",
    },
    {
        "MAKE": "BMW", "MODEL": "7 серии", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://www.press.bmwgroup.com/global/article/detail/T0380173EN/the-new-bmw-7-series",
        "note": "该俄文模型键与已核定的 BMW 7 产品线相同。BMW 官方历代资料展示连续的大型豪华四门轿车谱系；各代均为标准三厢覆盖比例，没有 SD0 或 SD2 所需的正向几何证据，归 SD1。",
    },
    {
        "MAKE": "Honda", "MODEL": "Prelude", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD0",
        "source_url": "https://global.honda/en/newsroom/news/2025/4250731eng.html",
        "note": "Honda 官方确认 Prelude 自 1978 年起一直是 specialty sports model，并延续至第六代；新一代同样采用低尖车头、低宽姿态和流畅收束车身。跨代均为低矮双门运动比例，归 SD0。",
    },
    {
        "MAKE": "Renault", "MODEL": "Clio i", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H0",
        "source_url": "https://www.renaultgroup.com/en/magazine/our-group-news/new-clio-the-legend-enters-its-sixth-chapter/",
        "note": "Renault 官方将第一代 Clio 明确称为 small hatch，并确认其于 1990 年接替 Supercinq。该代为低矮紧凑、斜前挡和短尾两厢比例，不具 H1 高方座舱，归 H0。",
    },
    {
        "MAKE": "VW", "MODEL": "Jetta ii", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://www.volkswagen-newsroom.com/en/jetta-2-19841992-19643",
        "note": "Volkswagen 官方将 Jetta II 定义为 Saloon，并明确其拥有区别于 Golf 尾门的独立行李厢。车身虽线条较直，但没有 SD2 所需的极端宽头和近矩形俯视证据，归标准三厢 SD1。",
    },
    {
        "MAKE": "VW", "MODEL": "Passat b3/b4 variant", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H2",
        "source_url": "https://www.volkswagen-newsroom.com/en/passat-b3-19881993-19540",
        "note": "Volkswagen 官方确认 Passat B3/B4 均提供 Saloon 与 Variant/Estate，本模型键只含 Variant。其低 CAB、斜前挡和延伸至尾门的长车顶符合 Wagon Touring；相较 H3 参考车型，前后柱和转角更流线，归 H2。",
    },
    {
        "MAKE": "VW", "MODEL": "Golf ii", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H0",
        "source_url": "https://www.volkswagen-newsroom.com/en/golf-2-19831991-19470",
        "note": "Volkswagen 官方 Golf II 档案确认标准紧凑两厢车身；虽然线条较方，但车身较低、机舱和尾悬短，座舱未达到 H1 的高 CAB 方盒比例，归 H0。",
    },
    {
        "MAKE": "Peugeot", "MODEL": "605", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://www.media.stellantis.com/it-it/peugeot/press-category/heritage-605",
        "note": "Peugeot 官方历史资料确认 605 是 1989 年推出的大型旗舰轿车。本模型键均为标准三厢版本；车头、座舱和尾部具有正常收窄，不满足 SD2 极端方正条件，也非 SD0 低矮运动轮廓，归 SD1。",
    },
]


if __name__ == "__main__":
    run(BATCH, RESEARCHED_RULES)
