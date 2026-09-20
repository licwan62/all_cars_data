from sync_regional_data import SHAPE_PROJECT, run


BATCH = SHAPE_PROJECT / "artifacts" / "2026-09-16_05_regional-shape-research"

# 继续只写入模型键内轮廓单一、能按参考定义直接判定的对象；不处理同键多车身混合项。
RESEARCHED_RULES = [
    {
        "MAKE": "Saab", "MODEL": "900 i combi coupe", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H0",
        "source_url": "https://www.auto-data.net/en/saab-900-i-combi-coupe-generation-2543",
        "note": "源目录车型页与各年份侧视资料显示该键均为低矮三/五门 Combi Coupé：前挡后倾、车顶向尾门连续下落，且没有 H1 所要求的高方座舱。严格按轮廓归 H0。",
    },
    {
        "MAKE": "Citroën", "MODEL": "Ax", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H0",
        "source_url": "https://www.media.stellantis.com/de-de/citroen/press/vor-30-jahren-weltpremiere-des-citroen-ax",
        "note": "Citroën 官方回顾确认 AX 的紧凑、空气动力学车身与塑料尾门；侧视为低车顶、短尾三/五门两厢，明显不具 H1 高方盒体，归 H0。",
    },
    {
        "MAKE": "Opel", "MODEL": "Vectra c", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://www.auto-data.net/en/opel-vectra-c-facelift-2005-generation-5173",
        "note": "源目录资料对应 Vectra C 四门三厢版；车头、座舱与车尾具有常规现代收窄，不具 SD2 极端宽方条件，也非低矮运动双门轮廓，归 SD1。",
    },
    {
        "MAKE": "Subaru", "MODEL": "Impreza station wagon", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H2",
        "source_url": "https://www.subaru.co.jp/en/news/archives/press/2002/02_01_21_01.htm",
        "note": "Subaru 官方资料明确为 Impreza Sports Wagon，并显示低 CAB、斜前挡和延伸至尾门的长车顶。其紧凑圆角旅行车比例符合 H2，而不是三厢 SD1 或高方 H3。",
    },
    {
        "MAKE": "Alfa Romeo", "MODEL": "Gt", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD0",
        "source_url": "https://www.media.stellantis.com/em-en/alfa-romeo/press/alfa-gt-4",
        "note": "Alfa Romeo 官方资料把 2003 GT 定义为运动 Coupé，车高仅 1.37 m；该模型键的历史 GT 亦均为低矮双门运动轮廓。前挡与车顶强烈后落，符合 SD0。",
    },
    {
        "MAKE": "Lancia", "MODEL": "Delta i", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H0",
        "source_url": "https://www.media.stellantis.com/de-de/lancia/press/78-internationaler-genfer-automobilsalon-weltpremiere-lancia-delta",
        "note": "Lancia 官方历史资料确认第一代 Delta 于 1979 年推出，采用强调功能性紧凑车身的梯形线条。其五门短尾两厢虽较方正，但座舱不高、不属 H1 高盒体，归 H0。",
    },
    {
        "MAKE": "Opel", "MODEL": "Vectra a", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://www.auto-data.net/en/opel-vectra-a-generation-544",
        "note": "源目录侧视资料显示 Vectra A 为标准四门三厢轿车。尽管线条偏直，车头和座舱仍正常收窄，不满足 SD2 的极端宽头、俯视近矩形正向条件，归 SD1。",
    },
    {
        "MAKE": "Opel", "MODEL": "Vectra c cc", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H0",
        "source_url": "https://www.auto-data.net/en/opel-vectra-c-cc-facelift-2005-generation-5171",
        "note": "源目录明确为 Vectra C CC 五门掀背/升降背版本；斜后窗与尾门形成低矮连续快背轮廓，不是独立三厢，也不具 H1 高方座舱，归 H0。",
    },
    {
        "MAKE": "Alfa Romeo", "MODEL": "Gtv", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD0",
        "source_url": "https://www.media.stellantis.com/uk-en/alfa-romeo/press/alfa-spider-and-gtv",
        "note": "Alfa Romeo 官方资料将 GTV 定义为运动 Coupé；历史 Alfetta GTV 与 916 均为低矮、下宽上窄、车顶快速后落的双门轮廓，严格归 SD0。",
    },
    {
        "MAKE": "Audi", "MODEL": "A4 b8", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://press.audi.co.uk/assets/documents/original/13843-AudiUK00000124A4A4allroadandS4Saloon.pdf",
        "note": "Audi 官方资料明确区分 B8 A4 Saloon 与 Avant/allroad；本模型键为四门 Saloon。其现代圆角三厢比例、正常车头与座舱收窄符合 SD1，不满足 SD2 极端方正条件。",
    },
]


if __name__ == "__main__":
    run(BATCH, RESEARCHED_RULES)
