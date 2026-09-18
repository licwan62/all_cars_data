from sync_regional_sales import PROJECT, run


BATCH = PROJECT / "artifacts" / "2026-09-16_02_regional-sales-research"
NISSAN_SOURCE = "https://www2.nissan-global.com/JP/IR/PERFORMANCE/ASSETS/2025/PDF/Nissan_Sales_202512.pdf"
VW_SOURCE = "https://www.volkswagen-newsroom.com/en/press-releases/volkswagen-delivers-473-million-vehicles-worldwide-and-further-consolidates-its-market-leadership-in-europe-20063"
AUTOSTAT_SOURCE = "https://eng.autostat.ru/news/27216/"


def us_fact(make: str, model: str, value: int, note: str = "") -> dict[str, str]:
    return {
        "REGION": "US", "COUNTRY_SCOPE": "US", "MAKE": make, "MODEL": model,
        "YEAR": "2025", "SALES_VALUE": str(value), "SALES_METRIC": "NEW_VEHICLE_SALES",
        "SALES_PERIOD": "FULL_YEAR", "SALES_PERIOD_END": "2025-12-31",
        "SOURCE_TYPE": "OEM_SALES_REPORT", "SOURCE_URL": NISSAN_SOURCE,
        "SOURCE_SCOPE": "US", "SOURCE_CONFIDENCE": "HIGH",
        "STATUS": "RESEARCHED_ALLOCATION_PENDING",
        "NOTES": note or "Nissan 官方 Retail Sales in the U.S. by Model，CYTD January–December 2025；仅限 US。",
    }


def ru_fact(model: str, value: int, note: str) -> dict[str, str]:
    return {
        "REGION": "RU", "COUNTRY_SCOPE": "RU", "MAKE": "Lada (ВАЗ)", "MODEL": model,
        "YEAR": "2025", "SALES_VALUE": str(value), "SALES_METRIC": "NEW_VEHICLE_SALES",
        "SALES_PERIOD": "FULL_YEAR", "SALES_PERIOD_END": "2025-12-31",
        "SOURCE_TYPE": "INDUSTRY_REPORT_CITING_OEM", "SOURCE_URL": AUTOSTAT_SOURCE,
        "SOURCE_SCOPE": "RU", "SOURCE_CONFIDENCE": "MEDIUM",
        "STATUS": "RESEARCHED_ALLOCATION_PENDING", "NOTES": f"{note}；仅限 RU。",
    }


RESEARCHED_FACTS = [
    us_fact("Nissan", "Versa", 51310),
    us_fact("Nissan", "Altima", 93268),
    us_fact("Nissan", "Maxima", 14),
    us_fact("Nissan", "Z", 5487),
    us_fact("Nissan", "GT-R", 39),
    us_fact("Nissan", "Leaf", 5149, "Nissan 官方 2025 US 表中 Leaf 4,690 + New Leaf 459，按区域缓存的 Leaf 模型族合计；仅限 US。"),
    us_fact("Nissan", "Frontier", 65232),
    us_fact("Nissan", "Pathfinder", 101598),
    us_fact("Nissan", "Kicks", 103575),
    us_fact("Nissan", "Murano", 42747),
    us_fact("Nissan", "Rogue", 217895),
    us_fact("Nissan", "Rogue Sport", 1),
    us_fact("Nissan", "Armada", 17465),
    us_fact("Nissan", "Ariya", 14906),
    us_fact("Infiniti", "Q50", 529),
    us_fact("Infiniti", "Q60", 0),
    us_fact("Infiniti", "QX50", 5901),
    us_fact("Infiniti", "QX55", 2288),
    us_fact("Infiniti", "QX60", 30538),
    us_fact("Infiniti", "QX80", 13590),
    {
        "REGION": "EU", "COUNTRY_SCOPE": "EU", "MAKE": "VW", "MODEL": "T-Roc",
        "YEAR": "2025", "SALES_VALUE": "201995", "SALES_METRIC": "VEHICLE_DELIVERIES",
        "SALES_PERIOD": "FULL_YEAR", "SALES_PERIOD_END": "2025-12-31",
        "SOURCE_TYPE": "OEM_PRESS_RELEASE", "SOURCE_URL": VW_SOURCE,
        "SOURCE_SCOPE": "EUROPE", "SOURCE_CONFIDENCE": "HIGH",
        "STATUS": "RESEARCHED_ALLOCATION_PENDING",
        "NOTES": "Volkswagen 官方称其为 2025 年欧洲最畅销的品牌 SUV；保留 EUROPE deliveries 口径，不外推至 US/RU。",
    },
    ru_fact("Vesta", 75099, "AUTOSTAT 引述 AVTOVAZ 的 2025 经销网络销量"),
    ru_fact("Niva Legend", 34422, "AUTOSTAT 引述 AVTOVAZ：乘用 33,968 + 商用皮卡 454"),
    ru_fact("Niva Travel", 35608, "AUTOSTAT 引述 AVTOVAZ 的 2025 经销网络销量"),
    ru_fact("Largus", 35925, "AUTOSTAT 引述 AVTOVAZ 的乘用及客货两用车型销量"),
    ru_fact("Iskra", 6796, "AUTOSTAT 引述 AVTOVAZ 的 2025 经销网络销量"),
]


if __name__ == "__main__":
    run(BATCH, RESEARCHED_FACTS)
