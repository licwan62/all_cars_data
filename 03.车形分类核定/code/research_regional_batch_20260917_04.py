from sync_regional_data import SHAPE_PROJECT, run


BATCH = SHAPE_PROJECT / "artifacts" / "2026-09-17_04_regional-shape-research"

# 第六批：整模型键结构单一，且厂商资料可支持严格轮廓判定。
RESEARCHED_RULES = [
    {
        "MAKE": "Mitsubishi", "MODEL": "Pajero ii", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SU1",
        "source_url": "https://www.mitsubishi-motors.com/en/newsroom/stories/pajero_history2/index.html",
        "note": "Mitsubishi 官方车系史确认第二代 Pajero 于 1991 年推出，是兼顾越野与公路操控的正统 4WD。官方图像显示较直立前挡、高离地和独立机舱，但座舱并非 SU2 的宽高近方盒边界，归标准 SUV 的 SU1。",
    },
    {
        "MAKE": "Land Rover", "MODEL": "Range rover i", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SU1",
        "source_url": "https://media.landrover.com/news/2021/10/new-range-rover-world-premiere-breathtaking-modernity-peerless-refinement-and-0",
        "note": "Land Rover 官方确认 Range Rover 为延续五十年的原创豪华 SUV。第一代虽线条直，但独立机舱、前后端收窄与普通宽度座舱不满足 SU2 的宽高方盒覆盖要求，归 SU1。",
    },
    {
        "MAKE": "Seat", "MODEL": "Ibiza iv sc", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H0",
        "source_url": "https://www.seat.com/content/dam/public/seat-website/company/annual-report/past-reports/pdf/others-annual_report_2014-info-NA-NA-september-2018.pdf",
        "note": "SEAT 官方年报确认第四代 Ibiza 提供 3-door 车身并采用更运动的几何线条。SC 侧视低矮、尾悬短、车顶较早下落，没有 H1 高 CAB 与平长车顶，归 H0。",
    },
    {
        "MAKE": "Seat", "MODEL": "Ibiza ii", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H0",
        "source_url": "https://www.seat.com/content/dam/public/seat-website/company/annual-report/historical-reports/pdf/others-annual_report_2014-info-NA-NA-september-2018.pdf",
        "note": "SEAT 官方历史资料确认 Ibiza II 于 1993–2002 年生产，外形为圆润紧凑的两厢车。其低车身、斜前挡、短尾与后顶下落符合 Low Sloping Hatch，不具 H1 高方比例，归 H0。",
    },
    {
        "MAKE": "VW", "MODEL": "Passat b3/b4", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://www.volkswagen-newsroom.com/en/passat-b4-19931997-19543",
        "note": "Volkswagen 官方档案明确 B3/B4 均同时提供 Saloon 和 Variant，本模型键只有 Sedan。它们是常规三厢轮廓，前部和座舱均有正常收窄；不因直线化年代外形升为 SD2，归 SD1。",
    },
    {
        "MAKE": "Ford", "MODEL": "Mondeo iv turnier", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H2",
        "source_url": "https://media.ford.com/content/fordmedia/feu/gb/en/news/2014/09/29/all-new-ford-mondeo-pricing-announced--petrol--diesel-and-first-.html",
        "note": "Ford 官方资料将 Mondeo 的四门、五门和 Estate 车身明确分开，源目录资料确认本键为 Turnier/Wagon。其低 CAB、斜前挡、连续长顶和圆顺尾门符合现代 Wagon Touring，归 H2。",
    },
    {
        "MAKE": "Audi", "MODEL": "b2", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD0",
        "source_url": "https://www.audi-mediacenter.com/en/press-releases/powerhouses-five-cylinder-engines-at-audi-14239/download",
        "note": "Audi 官方历史资料确认 quattro 与其基础车 Audi Coupé B2 的车身关系。官方侧视显示低车顶、斜前挡、宽下车身和明显向后下落的双门运动比例，具备正向 Low Sport 证据，归 SD0。",
    },
    {
        "MAKE": "Volvo", "MODEL": "V90 ii", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H2",
        "source_url": "https://www.media.volvocars.com/us/en-us/media/pressreleases/190759/volvo-v90-model-year-2017",
        "note": "Volvo 官方将第二代 V90 定义为五门大型 premium estate。长车顶一直延伸至尾门，同时前挡、D 柱和车身转角均为现代流线设计，符合 H2，不应沿用 Sedan 的 SD1。",
    },
    {
        "MAKE": "Audi", "MODEL": "A4 b7 avant", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H2",
        "source_url": "https://www.audi-mediacenter.com/en/the-audi-a4-major-upgrade-for-the-bestseller-11884/download",
        "note": "Audi 官方资料将 Avant 作为 A4/RS4 旅行车车身延续，源目录则锁定 B7 Avant。该代具有低 CAB、斜前挡、长顶和流线 D 柱，没有 H3 的高直方箱尾部，归 H2。",
    },
    {
        "MAKE": "Skoda", "MODEL": "Fabia ii combi", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H2",
        "source_url": "https://www.skoda-storyboard.com/en/press-releases/20-years-of-the-skoda-fabia-combi-a-real-success-story/",
        "note": "Škoda 官方明确 Fabia II Combi 为 2007–2014 年的 Estate，并给出明显增长的货厢容积。其长顶和尾门是旅行车比例，A/D 柱与前后角为现代流线，归 H2。",
    },
    {
        "MAKE": "Volvo", "MODEL": "V70 ii", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H2",
        "source_url": "https://www.media.volvocars.com/uk/en-gb/media/pressreleases/4888",
        "note": "Volvo 官方 Estate 车史确认第二代 V70 于 2000 年推出，采用更柔和、空气动力化的外形。低 CAB、长车顶与圆顺尾部符合 H2，不是 SD1，也不具 H3 的高方箱边界。",
    },
    {
        "MAKE": "Renault", "MODEL": "Megane iii grandtour", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H2",
        "source_url": "https://be.media.renaultgroup.com/section/renault/vehicules-particuliers/megane-megane-grandtour/",
        "note": "Renault 官方媒体资料将 Mégane Berline 与 Grandtour 分列，源目录资料确认本键为第三代 Grandtour。其低座舱、斜前挡、连续长顶和流线尾门符合 H2，不应按三厢车处理。",
    },
    {
        "MAKE": "Renault", "MODEL": "Laguna ii grandtour", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H2",
        "source_url": "https://be.media.renaultgroup.com/laguna-collection-2013/?lang=bel",
        "note": "Renault 官方资料持续将 Laguna、Laguna Grandtour 和 Coupé 作为独立车身形式，源目录资料锁定第二代 Grandtour。本键的低 CAB、斜前挡、长顶和流线尾部符合 H2，不应保留 SD1。",
    },
]


if __name__ == "__main__":
    run(BATCH, RESEARCHED_RULES)
