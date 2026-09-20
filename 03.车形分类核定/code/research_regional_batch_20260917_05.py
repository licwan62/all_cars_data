from sync_regional_data import SHAPE_PROJECT, run


BATCH = SHAPE_PROJECT / "artifacts" / "2026-09-17_05_regional-shape-research"

# 第七批：只处理整模型键结构单一、且厂商资料足以支持严格轮廓判定的车型。
RESEARCHED_RULES = [
    {
        "MAKE": "Opel", "MODEL": "Omega a", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://www.media.stellantis.com/it-it/opel/press/35-anni-fa-la-prima-opel-omega",
        "note": "Opel 官方资料将 Omega A 明确描述为四门三厢轿车，并强调其流线化车身、齐平车窗和修长比例。车头、座舱与车尾均有正常收窄，不满足 SD2 的极端方正俯视边界，也不是 SD0 低矮运动轮廓，归 SD1。",
    },
    {
        "MAKE": "Hyundai", "MODEL": "Santa fé ii", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SU1",
        "source_url": "https://www.hyundai.com/worldwide/en/newsroom/detail/0000000692",
        "note": "Hyundai 官方车系史确认第二代 Santa Fe 为 2006 至 2012 年的五座或七座 SUV。其独立机舱、正常宽度座舱及前后收窄属于标准 SUV；没有 SU2 所需的宽高近方盒覆盖边界，归 SU1。",
    },
    {
        "MAKE": "Ford", "MODEL": "Fiesta ii", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H0",
        "source_url": "https://media.ford.com/content/fordmedia/feu/gb/en/news/2016/07/18/1976-2016--ford-fiesta-celebrates-40-years-of-production.html",
        "note": "Ford 官方 Fiesta 历史确认第二代（MkII）于 1983 年推出并采用更具空气动力学的紧凑车身。短尾门、低座舱和较早下落的后车顶符合 Low Sloping Hatch，且没有 H1 的高方座舱，归 H0。",
    },
    {
        "MAKE": "Alfa Romeo", "MODEL": "75", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://www.media.stellantis.com/gr-el/alfa-romeo/press/alfa-romeo-summer-stories-30-chronia-alfa-romeo-155",
        "note": "Alfa Romeo 官方历史将 75 定位为传统中型轿车，并说明其后继车型为 155。75 的三厢比例虽带有年代直线特征，但车头与座舱仍有常规收窄，不满足 SD2 极端方正条件，归 SD1。",
    },
    {
        "MAKE": "Alfa Romeo", "MODEL": "164", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://www.media.stellantis.com/de-de/alfa-romeo/press/100-jahre-alfa-romeo-der-motorsport",
        "note": "Alfa Romeo 官方品牌史收录 164；官方车型图与资料显示其为 Pininfarina 设计的常规四门三厢大型轿车。车头、座舱与尾厢均有正常流线收窄，不属于 SD0 或 SD2，归 SD1。",
    },
    {
        "MAKE": "Alfa Romeo", "MODEL": "155", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://www.media.stellantis.com/em-en/alfa-romeo/press/alfa-romeo-155-v6-ti-dtm-stars-on-the-zandvoort-circuit",
        "note": "Alfa Romeo 官方资料与历史图像确认 155 的量产基础是四门三厢轿车。其楔形、直线化风格不等同于 SD2；车头、座舱和尾厢仍有明确常规收窄，归 SD1。",
    },
    {
        "MAKE": "Opel", "MODEL": "Kadett e cc", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H0",
        "source_url": "https://www.media.stellantis.com/em-en/opel/press/opel-kadett-and-astra-85-years-as-defining-force-of-compact-class",
        "note": "Opel 官方历史明确称 Kadett E 采用全新的 hatchback 车身，并区分另行提供的 notchback 与 station wagon。CC 键对应短尾掀背，座舱较低且后车顶下落，不具 H1 高方边界，归 H0。",
    },
    {
        "MAKE": "Opel", "MODEL": "Astra g cc", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H0",
        "source_url": "https://www.media.stellantis.com/em-en/opel/press/opel-kadett-and-astra-85-years-as-defining-force-of-compact-class",
        "note": "Opel 官方历史确认 Astra G 首发为三门和五门 hatchback，并与 station wagon、notchback、coupé、convertible 分列。CC 键为标准低座舱短尾掀背，不满足 H1 的高方比例，归 H0。",
    },
    {
        "MAKE": "Mitsubishi", "MODEL": "Outlander iii", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SU1",
        "source_url": "https://www.mitsubishi-motors.com/en/corporate/social/pdf/2012e_all.pdf",
        "note": "Mitsubishi 官方 2012 年资料将新一代 Outlander 明确定义为全球投放的 eco-SUV，并给出其标准跨界 SUV 轮廓。独立机舱、正常座舱宽度和前后收窄不符合 SU2 宽高近方盒条件，归 SU1。",
    },
    {
        "MAKE": "Land Rover", "MODEL": "Range rover iv", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SU1",
        "source_url": "https://media.landrover.com/en-us/news/2014/12/land-rover-north-america-continues-support-equestrian-sports-official-vehicle-sponsor",
        "note": "Land Rover 官方资料明确称 2015 Range Rover 为第四代豪华 SUV。尽管车身高大，其机舱独立、车头和船尾均有收窄，侧壁也不是宽高近方盒覆盖，严格按普通 SUV 归 SU1。",
    },
    {
        "MAKE": "Volvo", "MODEL": "S60 iii", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://www.media.volvocars.com/ca/en-ca/media/pressreleases/231035/volvo-cars-expands-global-manufacturing-footprint-with-first-us-factory",
        "note": "Volvo 官方资料确认 2018 年投产的新 S60 是基于 SPA 的中型运动轿车，即第三代 S60。其为流线化四门三厢车，车头、座舱和尾部正常收窄，不满足 SD0 或 SD2，归 SD1。",
    },
    {
        "MAKE": "VW", "MODEL": "Golf v", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H0",
        "source_url": "https://www.volkswagen-newsroom.com/en/golf-5-20032008-19480",
        "note": "Volkswagen 官方档案确认 Golf V 为 2003 至 2008 年的第五代 Golf，并将 Plus、Variant 等衍生车身另列。标准 Golf V 是低座舱、短尾门的紧凑掀背，后车顶较早下落，归 H0。",
    },
    {
        "MAKE": "Toyota", "MODEL": "Rav 4 iii", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SU1",
        "source_url": "https://global.toyota/en/newsroom/toyota/23828263.html",
        "note": "Toyota 官方发布明确称 2005 年新 RAV4 为第三代 SUV，并强调其城市化外形与户外机动性。其独立机舱、标准跨界座舱和常规前后收窄不属于 SU2 方盒边界，归 SU1。",
    },
    {
        "MAKE": "Audi", "MODEL": "A8 d2", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://www.audi-mediacenter.com/en/publications/more/audi-tradition-anniversary-dates-2026-1676/download",
        "note": "Audi Tradition 官方资料确认首代 A8 为铝制车身豪华轿车，并明确称其设计为经典保守的 luxury sedan。它是常规流线化三厢轮廓，不满足 SD2 极端方正证据，也非 SD0，归 SD1。",
    },
    {
        "MAKE": "Mercedes-benz", "MODEL": "Glk-Klasse", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SU1",
        "source_url": "https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/GLK-350-4MATIC-BlueEFFICIENCY-2012---2015-from-042013-GLK-350-4MATIC.xhtml?oid=189873475",
        "note": "Mercedes-Benz 官方档案锁定 X204 GLK。虽然其侧面线条较直，但独立机舱、正常宽度座舱与前后收窄仍是标准紧凑 SUV；不具 SU2 的宽高近方盒覆盖，归 SU1。",
    },
]


if __name__ == "__main__":
    run(BATCH, RESEARCHED_RULES)
