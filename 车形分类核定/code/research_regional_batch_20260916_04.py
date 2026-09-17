from sync_regional_data import SHAPE_PROJECT, run


BATCH = SHAPE_PROJECT / "artifacts" / "2026-09-16_04_regional-shape-research"

# 仅覆盖车型键内车身轮廓单一、且厂商资料足以支持跨区域继承的对象。
RESEARCHED_RULES = [
    {
        "MAKE": "Audi", "MODEL": "A6 c5 avant", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H2",
        "source_url": "https://press.audi.co.uk/assets/documents/original/17205-AudiUK00001041AudiA6Avant20Technical.pdf",
        "note": "Audi 官方技术资料确认 C5 A6 Avant 为长顶五门旅行车。其低 CAB、斜前挡、连续延伸到尾门的长车顶与现代圆角轮廓直接符合参考定义中的 A6 Avant / Wagon Touring，归 H2。",
    },
    {
        "MAKE": "Audi", "MODEL": "A6 c6 avant", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H2",
        "source_url": "https://press.audi.co.uk/assets/documents/original/18179-AudiUK00000889A6Avant20TDITechnical.pdf",
        "note": "Audi 官方 C6 A6 Avant 技术资料显示低座舱、斜前挡和完整长车顶旅行车比例。该模型键不含 Saloon，轮廓符合 H2，而不是按当前默认轿车形态归 SD1。",
    },
    {
        "MAKE": "Audi", "MODEL": "A6 c7 avant", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H2",
        "source_url": "https://press.audi.co.uk/assets/documents/original/18291-AudiUK00000123A6SaloonandAvantPricing.pdf",
        "note": "Audi 官方资料明确区分 C7 A6 Saloon 与 Avant；本模型键全部为 Avant。其低 CAB、流线前挡和连续长车顶符合 H2 Wagon Touring，不能沿用 SD1。",
    },
    {
        "MAKE": "VW", "MODEL": "Sharan", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "V0",
        "source_url": "https://www.volkswagen-newsroom.com/en/sharan-1-19952010-19713",
        "note": "Volkswagen 官方把 Sharan 定义为大型 MPV，并确认五至七座、短车头、高且宽的座舱和连续空间型车身。其前部到车顶宽度变化小，符合标准 Minivan 的 V0；不是常规 SUV 的 SU1。",
    },
    {
        "MAKE": "Seat", "MODEL": "Alhambra", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "V0",
        "source_url": "https://www.seat.com/content/dam/public/seat-website/car-shopping-tools/brochure-download/brochures/alhambra/cars-specs-brochure-711-NA-december-2018.pdf",
        "note": "SEAT 官方规格把 Alhambra 标注为 MPV，并给出 1,904 mm 宽、1,720 mm 高及七座大空间。核对其短车头、宽前挡根部和宽车顶轮廓，符合 V0 标准 Minivan，而非 SU1。",
    },
    {
        "MAKE": "Volvo", "MODEL": "S60 ii", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://www.volvocars.com/uk/media/press-releases/7045C3828F4779AF/",
        "note": "Volvo 官方资料确认第二代 S60 为四门轿车，并采用流线、轿跑式车顶。车头与座舱仍有正常现代收窄，不满足 SD2 的极端宽方条件，也不是 SD0 的低矮双门运动外廓，归 SD1。",
    },
    {
        "MAKE": "Volvo", "MODEL": "S80 i", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://www.volvocars.com/us/media/models/s80/1998/",
        "note": "Volvo 官方车型档案确认第一代 S80 是纯四门大型轿车。其圆润肩线、常规三厢比例和前后正常收窄不满足 SD2 极端方正宽头条件，严格归 SD1。",
    },
]


if __name__ == "__main__":
    run(BATCH, RESEARCHED_RULES)
