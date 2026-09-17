from sync_regional_data import SHAPE_PROJECT, run


BATCH = SHAPE_PROJECT / "artifacts" / "2026-09-17_03_regional-shape-research"

# 第五批只处理车身结构单一、官方资料可覆盖整个模型键的条目。
RESEARCHED_RULES = [
    {
        "MAKE": "Lexus", "MODEL": "Gs", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://global.toyota/jp/newsroom/lexus/32231442.html",
        "note": "Lexus 官方回顾确认 GS 自 1993 年起四代均是 Grand Touring Sedan。历代车头、座舱与车尾均为常规收窄的现代三厢比例，没有 SD2 要求的极端宽方前部，也不是 SD0 的低矮运动罩体，归 SD1。",
    },
    {
        "MAKE": "Ford USA", "MODEL": "Mustang convertible", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD0",
        "source_url": "https://media.ford.com/content/dam/fordmedia/Europe/documents/en/2022/2022_Mustang_Tech_Spec_EU.pdf",
        "note": "Ford 官方规格将 Mustang Convertible 与 Fastback 对列，两者共用低矮、宽车身和长机舱的运动基本比例；开蓬机构不改变下宽上窄的覆盖边界。该模型键各代均为明确低矮运动轮廓，归 SD0。",
    },
    {
        "MAKE": "Hyundai", "MODEL": "Grandeur", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://org.hyundai.com/worldwide/en/brand-journal/heritage/heritage-series-grandeur",
        "note": "Hyundai 官方车系史确认 Grandeur 从 1986 年旗舰 Sedan 延续多代。早期直线化外形也仍有常规翼子板和座舱收窄，不能仅凭年代或方灯升为 SD2；后续代际更为流线，整体归 SD1。",
    },
    {
        "MAKE": "Audi", "MODEL": "A8", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://www.audi-mediacenter.com/en/publications/more/audi-tradition-anniversary-dates-2024-1484/download",
        "note": "Audi Tradition 官方档案展示 A8 自 1994 年起的旗舰轿车轮廓。各代均为曲面连续的现代三厢车，前角与座舱明显收窄，无证据表明覆盖需求超过 Avalon 参考边界，归 SD1。",
    },
    {
        "MAKE": "Opel", "MODEL": "Senator", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://www.media.stellantis.com/es-es/opel/press/la-progresion-de-opel-del-lutzmann-de-1899-al-nuevo-opel-corsa-e-de-2020",
        "note": "Opel 官方历史资料确认 Senator 是基于 Rekord 的加长旗舰轿车，并描述其更宽前部与收紧的后柱。“更宽”不等于 SD2：可见轮廓仍是标准三厢、座舱及前后端正常收窄，归 SD1。",
    },
    {
        "MAKE": "Volvo", "MODEL": "V60 i", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H2",
        "source_url": "https://www.volvocars.com/us/media/models/v60heritage/2011/",
        "note": "Volvo 官方档案确认第一代 V60 为 premium estate。侧视具有低 CAB、斜前挡和延伸至尾门的长车顶，同时 A/D 柱和车身转角为现代流线设计，符合 Wagon Touring，归 H2。",
    },
    {
        "MAKE": "VW", "MODEL": "Passat b8 variant", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H2",
        "source_url": "https://www.volkswagen-newsroom.com/en/the-new-passat-the-worlds-most-successful-mid-range-model-will-be-the-first-volkswagen-to-offer-partly-automated-driving-at-cruising-speed-4688",
        "note": "Volkswagen 官方 B8 资料展示 Passat Variant 的车身形式。该模型键只包含 Variant，其低 CAB、斜前挡、连续长顶与现代圆顺转角符合 H2；不应沿用三厢版 SD1。",
    },
    {
        "MAKE": "VW", "MODEL": "Passat b8", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://www.volkswagen-newsroom.com/en/the-new-passat-the-worlds-most-successful-mid-range-model-will-be-the-first-volkswagen-to-offer-partly-automated-driving-at-cruising-speed-4688",
        "note": "Volkswagen 官方 B8 资料可区分标准 Passat 三厢车与 Variant。本模型键为现代标准三厢轮廓，前部与座舱均正常收窄，无 SD2 极端方宽或 SD0 低矮收束证据，归 SD1。",
    },
    {
        "MAKE": "Renault", "MODEL": "Clio iv", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H0",
        "source_url": "https://imprensa.renaultgroup.com/historia-do-renault-clio/?lang=por",
        "note": "Renault 官方车系史明确第四代 Clio 有五门 Hatchback 和另行命名的 Sport Tourer。本模型键结构均为 Hatchback，车身低、后顶较早下落且尾悬短，不具 H1 高方 CAB，归 H0。",
    },
    {
        "MAKE": "Honda", "MODEL": "Civic vii hatchback", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H0",
        "source_url": "https://hondanews.eu/eu/en/cars/media/pressreleases/34266/civic-04-specifications-2004",
        "note": "Honda 官方第七代 Civic 规格分列 3-door 和 5-door 车身，并给出低于 1.5 米的整车高度。配合官方图像可见斜前挡、短尾和后顶下落，未达到 H1 高方比例，归 H0。",
    },
    {
        "MAKE": "Porsche", "MODEL": "Cayman", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD0",
        "source_url": "https://newsroom.porsche.com/it/ppdb/2016/04/motore-turbo-a-quattro-cilindri-e-maggiore-potenza-la-nuova-porsche-718-cayman.html",
        "note": "Porsche 官方将 Cayman/718 Cayman 明确为中置双座运动 Coupé。历代均为低机盖、低车顶、宽下车身与明显内收座舱的覆盖比例，具备正向 Low Sport 证据，归 SD0。",
    },
    {
        "MAKE": "Nissan", "MODEL": "Gt-R", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD0",
        "source_url": "https://global.nissannews.com/en/releases/release-d7e4ecd11a3301770049acecdc00031c-nissan-unveils-gt-r-proto-at-tokyo-motor-show",
        "note": "Nissan 官方资料确认 R35 GT-R 首次作为独立车身而非 Sedan 衍生。本模型键只覆盖 R35，其低矮双门、宽翼子板、内收座舱和向后下落车顶构成明确下宽上窄运动轮廓，归 SD0。",
    },
]


if __name__ == "__main__":
    run(BATCH, RESEARCHED_RULES)
