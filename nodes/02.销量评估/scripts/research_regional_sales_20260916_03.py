from sync_regional_sales import PROJECT, run


BATCH = PROJECT / "artifacts" / "2026-09-16_03_regional-sales-research"
TOYOTA_SOURCE = "https://pressroom.toyota.com/toyota-motor-north-america-reports-2025-u-s-sales-results/"
RENAULT_SOURCE = "https://www.renaultgroup.com/en/magazine/our-group-news/new-clio-the-legend-enters-its-sixth-chapter/"
SKODA_SOURCE = "https://cdn.skoda-storyboard.com/2026/03/260323_Elroq_and_Enyaq_Model_year_updates_for_both_Skoda_electric_bestsellers_3ef1c7b1.pdf"
AUTOSTAT_SOURCE = "https://eng.autostat.ru/news/25672/"


def us_fact(make: str, model: str, value: int, note: str = "") -> dict[str, str]:
    return {
        "REGION": "US", "COUNTRY_SCOPE": "US", "MAKE": make, "MODEL": model,
        "YEAR": "2025", "SALES_VALUE": str(value), "SALES_METRIC": "NEW_VEHICLE_SALES",
        "SALES_PERIOD": "FULL_YEAR", "SALES_PERIOD_END": "2025-12-31",
        "SOURCE_TYPE": "OEM_SALES_REPORT", "SOURCE_URL": TOYOTA_SOURCE,
        "SOURCE_SCOPE": "US", "SOURCE_CONFIDENCE": "HIGH",
        "STATUS": "RESEARCHED_ALLOCATION_PENDING",
        "NOTES": note or "Toyota Motor North America 官方 U.S. Sales Summary，CYTD 2025；仅限 US。",
    }


def ru_2024_fact(make: str, model: str, value: int) -> dict[str, str]:
    return {
        "REGION": "RU", "COUNTRY_SCOPE": "RU", "MAKE": make, "MODEL": model,
        "YEAR": "2024", "SALES_VALUE": str(value), "SALES_METRIC": "NEW_PASSENGER_CAR_SALES_ROUNDED",
        "SALES_PERIOD": "FULL_YEAR", "SALES_PERIOD_END": "2024-12-31",
        "SOURCE_TYPE": "INDUSTRY_MARKET_REPORT", "SOURCE_URL": AUTOSTAT_SOURCE,
        "SOURCE_SCOPE": "RU", "SOURCE_CONFIDENCE": "MEDIUM",
        "STATUS": "RESEARCHED_ALLOCATION_PENDING",
        "NOTES": "AUTOSTAT 俄罗斯 2024 全年新乘用车市场排名；网页按千辆保留一位小数，缓存值为公布值换算，不能视为个位精确；仅限 RU。",
    }


RESEARCHED_FACTS = [
    us_fact("Toyota", "Supra", 2953),
    us_fact("Toyota", "86", 9940, "Toyota 官方表列 GR86（含 FR-S）9,940；区域数据模型键为 86；仅限 US。"),
    us_fact("Toyota", "MIRAI", 210),
    us_fact("Toyota", "Crown", 12309),
    us_fact("Toyota", "Prius", 40985, "Toyota 官方电气化分表的 Prius Hybrid 2025 CYTD；不含另列 Prius Plug-in Hybrid；仅限 US。"),
    us_fact("Toyota", "Prius Prime", 15503, "Toyota 官方电气化分表的 Prius Plug-in Hybrid 2025 CYTD；映射到区域模型键 Prius Prime；仅限 US。"),
    us_fact("Toyota", "Camry", 316185),
    us_fact("Lexus", "IS", 19714),
    us_fact("Lexus", "RC", 1349),
    us_fact("Lexus", "ES", 39926),
    us_fact("Lexus", "LS", 1082),
    us_fact("Lexus", "LC", 1286),
    us_fact("Toyota", "RAV4", 479288),
    us_fact("Toyota", "Corolla Cross", 99798),
    us_fact("Toyota", "Crown Signia", 20550),
    us_fact("Toyota", "Venza", 707),
    us_fact("Toyota", "Highlander", 56208),
    us_fact("Toyota", "Grand Highlander", 136801),
    us_fact("Toyota", "4Runner", 98805),
    us_fact("Toyota", "Sequoia", 26186),
    us_fact("Toyota", "Land Cruiser", 43946),
    us_fact("Toyota", "Sienna", 101486),
    us_fact("Toyota", "Tacoma", 274638),
    us_fact("Toyota", "Tundra", 147610),
    us_fact("Lexus", "UX", 8421),
    us_fact("Lexus", "NX", 76836),
    us_fact("Lexus", "RZ", 6400),
    us_fact("Lexus", "RX", 113256),
    us_fact("Lexus", "TX", 57346),
    us_fact("Lexus", "GX", 37180),
    us_fact("Lexus", "LX", 7464),
    {
        "REGION": "EU", "COUNTRY_SCOPE": "EU", "MAKE": "Renault", "MODEL": "Clio v",
        "YEAR": "2025", "SALES_VALUE": "130000", "SALES_METRIC": "NEW_VEHICLE_SALES_ROUNDED",
        "SALES_PERIOD": "H1", "SALES_PERIOD_END": "2025-06-30",
        "SOURCE_TYPE": "OEM_MODEL_HISTORY", "SOURCE_URL": RENAULT_SOURCE,
        "SOURCE_SCOPE": "EUROPE", "SOURCE_CONFIDENCE": "MEDIUM",
        "STATUS": "RESEARCHED_ALLOCATION_PENDING",
        "NOTES": "Renault 官方称 Clio 2025 上半年欧洲销量 130,000；当期在售代际为 Clio V，按代际键记录，且不外推全年或其他区域。",
    },
    {
        "REGION": "EU", "COUNTRY_SCOPE": "EU", "MAKE": "Skoda", "MODEL": "Elroq",
        "YEAR": "2025", "SALES_VALUE": "95300", "SALES_METRIC": "VEHICLE_DELIVERIES_MINIMUM",
        "SALES_PERIOD": "FULL_YEAR", "SALES_PERIOD_END": "2025-12-31",
        "SOURCE_TYPE": "OEM_PRESS_RELEASE", "SOURCE_URL": SKODA_SOURCE,
        "SOURCE_SCOPE": "EUROPE", "SOURCE_CONFIDENCE": "HIGH",
        "STATUS": "RESEARCHED_ALLOCATION_PENDING",
        "NOTES": "Škoda 官方称 Elroq 2025 年在欧洲交付超过 95,300 辆；数值按公开下限保存，不冒充精确值，也不向 US/RU 继承。",
    },
    ru_2024_fact("Lada (ВАЗ)", "Granta", 201500),
    ru_2024_fact("Lada (ВАЗ)", "Vesta", 123200),
    ru_2024_fact("Haval", "Jolion", 83800),
    ru_2024_fact("Chery", "Tiggo 7 Pro Max", 64800),
    ru_2024_fact("Chery", "Tiggo 4 Pro", 52700),
]


if __name__ == "__main__":
    run(BATCH, RESEARCHED_FACTS)
