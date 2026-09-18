from sync_regional_data import SHAPE_PROJECT, run


BATCH = SHAPE_PROJECT / "artifacts" / "2026-09-17_01_regional-shape-research"

# 本批只覆盖结构单一、官方资料可确认真实轮廓的区域模型键。
RESEARCHED_RULES = [
    {
        "MAKE": "Audi", "MODEL": "A4 b9", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://www.audi-mediacenter.com/en/the-audi-a4-major-upgrade-for-the-bestseller-2019-11884/download",
        "note": "Audi 官方资料把 B9 A4 的 Sedan 与 Avant 分开列示；本模型键源记录均为 Sedan。其三厢比例、常规座舱高度和前部收窄不满足 SD0 的低矮运动轮廓，也无 SD2 的极端宽方前部证据，归 SD1。",
    },
    {
        "MAKE": "Audi", "MODEL": "A6 c5", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://press.audi.co.uk/assets/documents/original/17212-AudiUK00001916A642quattroTechnicalSpecification.pdf",
        "note": "Audi 官方 C5 A6 Saloon 技术资料用于核对。该模型键均为 Sedan/Saloon，包含的性能版本仍保留常规四门三厢覆盖比例；缺少 SD0 的明确低矮收束或 SD2 的极端宽方前部证据，归 SD1。",
    },
    {
        "MAKE": "Audi", "MODEL": "A6 c6", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://press.audi.co.uk/assets/documents/original/17190-AudiUK00000988A632FSITechnicalData.pdf",
        "note": "Audi 官方 C6 A6 Saloon 技术资料确认标准现代三厢轮廓。车头、翼子板和座舱具有正常收窄，性能型号名称不足以升级为 SD0，且不满足 SD2 正向几何条件，归 SD1。",
    },
    {
        "MAKE": "Audi", "MODEL": "A6 c7", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://press.audi.co.uk/assets/documents/original/17375-AudiUK00000414AudiA6RangeTechnicalData.pdf",
        "note": "Audi 官方 C7 A6 技术资料区分 Saloon 与 Avant；本模型键均为 Sedan。其现代圆角三厢比例不具备 SD0 的低矮下宽上窄特征，也没有 SD2 的宽方车头证据，归 SD1。",
    },
    {
        "MAKE": "Ford", "MODEL": "Focus iii turnier", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H2",
        "source_url": "https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Focus/FordFocus_TechSpecs_EU.pdf",
        "note": "Ford 官方 Focus 技术资料确认 Turnier/Wagon 分支。其低 CAB、斜前挡、从 B 柱后继续延伸的长车顶和现代流线尾门符合 Wagon Touring，归 H2。",
    },
    {
        "MAKE": "VW", "MODEL": "Golf vii variant", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H2",
        "source_url": "https://www.volkswagen-newsroom.com/en/golf-7-variant-20132020-20041",
        "note": "Volkswagen 官方明确将 Golf VII Variant 称为 Golf 的 estate 版本，并说明其加长车身与独立尾部比例。低 CAB、斜前挡和连续长顶符合现代旅行车 H2，而不是 Sedan 或普通 Hatchback。",
    },
    {
        "MAKE": "VW", "MODEL": "Golf viii", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H0",
        "source_url": "https://www.volkswagen-newsroom.com/en/the-new-golf-international-vehicle-presentation-5609",
        "note": "Volkswagen 官方 Golf VIII 资料将标准 Golf 与另列的 Golf Variant 区分。本模型键为 Hatchback，车身较低、前挡倾斜、短尾且后顶较早下降，不满足 H1 高 CAB 方盒比例，归 H0。",
    },
    {
        "MAKE": "VW", "MODEL": "Touareg", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SU1",
        "source_url": "https://www.volkswagen-newsroom.com/en/the-first-21-years-16055",
        "note": "Volkswagen 官方回顾确认三代 Touareg 均为同一大型 SUV 产品线，并展示从越野取向向现代动态全能车型演进。各代前部与座舱较饱满但保留圆角和正常收窄，不达到 SU2 宽方前部，也非 SU0 明显收窄，归 SU1。",
    },
    {
        "MAKE": "Volvo", "MODEL": "Xc60 i", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SU1",
        "source_url": "https://www.media.volvocars.com/global/en-gb/models/volvo-xc60/2011",
        "note": "Volvo 官方把第一代 XC60 描述为肌肉感 crossover，下部车身、宽肩和轮拱饱满，上部采用流动线条。前部与座舱没有共同显著收窄，也未形成 SU2 的方直宽头，归常规 SUV 的 SU1。",
    },
    {
        "MAKE": "Volvo", "MODEL": "Xc60 ii", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SU1",
        "source_url": "https://www.media.volvocars.com/us/en-us/media/pressreleases/218410/all-new-volvo-xc60-named-2018-detroit-free-press-utility-of-the-year",
        "note": "Volvo 官方确认第二代 XC60 是紧凑豪华 SUV，并描述其 athletic stance。官方轮廓显示饱满车头与座舱、现代圆角和适度收窄，不满足 SU0 或 SU2 的升级条件，归 SU1。",
    },
    {
        "MAKE": "Volvo", "MODEL": "Xc90 ii", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SU1",
        "source_url": "https://www.media.volvocars.com/global/en-gb/media/pressreleases/161467/the-all-new-volvo-xc90-model-year-2016",
        "note": "Volvo 官方将第二代 XC90 定位为大型七座 SUV，并说明其大面积发动机舱盖、清晰肩线和自信前脸。其体量饱满但转角仍为现代圆角，未达到 SU2 的宽方近矩形前部，归 SU1。",
    },
]


if __name__ == "__main__":
    run(BATCH, RESEARCHED_RULES)
