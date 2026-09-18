from sync_regional_data import SHAPE_PROJECT, run


BATCH = SHAPE_PROJECT / "artifacts" / "2026-09-16_02_regional-shape-research"

# 仅覆盖车型键内车身轮廓单一、且厂商一手资料足以支撑跨区域继承的对象。
RESEARCHED_RULES = [
    {
        "MAKE": "Audi", "MODEL": "A7 sportback", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://www.audi-mediacenter.com/en/the-audi-a7-sportback-until-2025-progressive-in-design-and-technology-9831/facts-and-figures-9835",
        "note": "Audi 官方将 A7 Sportback 定义为四门 Gran Turismo，并给出长发动机舱、长轴距、低车高及向后下降的座舱轮廓。它虽为五门掀背，但整体仍是 Sedan/Fastback/Sportback 比例；按定义不因尾门形式转为 H0，归 SD1。",
    },
    {
        "MAKE": "Audi", "MODEL": "A4 b9 avant", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H2",
        "source_url": "https://www.audi-mediacenter.com/en/the-audi-a4-major-upgrade-for-the-bestseller-11884/download",
        "note": "Audi 官方资料将 B9 A4 的 Sedan 与 Avant 明确并列；源记录均为 Avant/Wagon 分支。其低 CAB、斜前挡和延伸至车尾的长车顶属于现代流线 Touring/Wagon，归 H2。",
    },
    {
        "MAKE": "VW", "MODEL": "Tiguan", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SU1",
        "source_url": "https://www.volkswagen-newsroom.com/en/tiguan-6611",
        "note": "Volkswagen 官方将历代 Tiguan 定位为 family SUV；核对官方侧面轮廓，前部和座舱饱满、保留现代圆角，不具备 SU0 的共同明显收窄，也未达到 SU2 的宽方车头，归常规 SUV 的 SU1。",
    },
    {
        "MAKE": "Volkswagen", "MODEL": "Tiguan", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SU1",
        "source_url": "https://www.volkswagen-newsroom.com/en/tiguan-6611",
        "note": "与 EU 的 VW/Tiguan 为同一产品线，仅品牌拼写不同。Volkswagen 官方历代资料显示常规现代 SUV 轮廓，前部与座舱均无 SU0 的显著收窄，也不满足 SU2 的宽方前部，归 SU1。",
    },
    {
        "MAKE": "VW", "MODEL": "Touran", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H1",
        "source_url": "https://www.volkswagen-newsroom.com/en/touran-1-20032015-19719",
        "note": "Volkswagen 官方将 Touran I 定位为 compact van，并给出 4,391 mm 车长、1,635 mm 以上车高和五至七座空间。核对官方侧面轮廓，其高 CAB、短机舱、平直长车顶和直尾更接近 Tall Box Hatch，而非宽体短鼻标准 Minivan，归 H1。",
    },
    {
        "MAKE": "Volkswagen", "MODEL": "Touran", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H1",
        "source_url": "https://www.volkswagen-newsroom.com/en/touran-3529",
        "note": "与 EU 的 VW/Touran 为同一产品线，仅品牌拼写不同。官方资料确认其 compact van、高 CAB 与紧凑车身比例；真实轮廓更接近高方两厢，不按 MPV 字段机械归 V0，归 H1。",
    },
    {
        "MAKE": "Volvo", "MODEL": "V70 iii", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H2",
        "source_url": "https://www.media.volvocars.com/uk/en-gb/media/pressreleases/15088",
        "note": "Volvo 官方第三代 V70 资料确认其为 V70 长顶载物车身。核对官方轮廓，低 CAB、斜前挡、连续长车顶与现代流线转角符合 Wagon Touring，归 H2。",
    },
    {
        "MAKE": "Opel", "MODEL": "Insignia a sports tourer", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H2",
        "source_url": "https://www.media.stellantis.com/em-en/opel/press/ready-for-launch-opel-opens-new-insignia-order-bank",
        "note": "Opel 官方把 Insignia Sports Tourer 明确称为 estate，并与 Grand Sport limousine 区分。源模型键均为 Sports Tourer/Wagon，低 CAB、斜前挡和长顶现代旅行车轮廓符合 H2。",
    },
    {
        "MAKE": "Mitsubishi", "MODEL": "Pajero iv", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SU2",
        "source_url": "https://www.mitsubishi-motors.com/en/company/history/car/",
        "note": "Mitsubishi 官方车型史确认第四代 Pajero 延续以直线为主的强健造型；官方历史图与第四代说明显示宽方车头、直立座舱及较少的侧向收窄。其方正程度超过常规 SU1，但不具备 JP 的外露翼子板和全高度方盒特征，归 SU2。",
    },
]


if __name__ == "__main__":
    run(BATCH, RESEARCHED_RULES)
