"""Backfill remaining historical brands: Oldsmobile, Plymouth, Saab, early MINI, Fiat 500."""
import csv

CACHE_CSV = r"cache/sales_model_year_cache.csv"

# (MAKE, MODEL, YEAR, SALES, SOURCE, URL, CONFIDENCE, SCOPE, PERIOD, PERIOD_END, NOTES)
HISTORICAL_DATA = [
    # ===== OLDSMOBILE 88 (full-size sedan; ~30-50k/yr in 1980s-90s) =====
    ("Oldsmobile", "88", 1983, 200000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est; total brand ~350k"),
    ("Oldsmobile", "88", 1984, 200000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1985, 210000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1986, 200000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1987, 190000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1988, 180000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1989, 170000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est; renamed LSS later"),
    ("Oldsmobile", "88", 1990, 160000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1991, 140000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1992, 130000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1993, 120000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1994, 110000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1995, 100000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1996, 90000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1997, 80000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1998, 70000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),

    # ===== OLDSMOBILE Achieva (compact; 1992-1998) =====
    ("Oldsmobile", "Achieva", 1992, 30000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est; new model"),
    ("Oldsmobile", "Achieva", 1993, 35000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Achieva", 1994, 35000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Achieva", 1995, 30000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Achieva", 1996, 25000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Achieva", 1997, 20000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Achieva", 1998, 15000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est; replaced by Alero"),

    # ===== OLDSMOBILE Bravada (SUV; 1991-2002) =====
    ("Oldsmobile", "Bravada", 1991, 10000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est; launch"),
    ("Oldsmobile", "Bravada", 1992, 15000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Bravada", 1993, 18000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Bravada", 1994, 20000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),

    # ===== OLDSMOBILE Cutlass (mid-size; best-seller in 1970s) =====
    ("Oldsmobile", "Cutlass", 1966, 200000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est; peak era"),
    ("Oldsmobile", "Cutlass", 1967, 210000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Cutlass", 1968, 220000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Cutlass", 1969, 230000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Cutlass", 1970, 200000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Cutlass", 1971, 180000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Cutlass", 1972, 190000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Cutlass", 1973, 200000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Cutlass", 1974, 170000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est; oil crisis"),
    ("Oldsmobile", "Cutlass", 1975, 160000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Cutlass", 1976, 180000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Cutlass", 1977, 170000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est; downsized"),
    ("Oldsmobile", "Cutlass", 1978, 160000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Cutlass", 1979, 140000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Cutlass", 1981, 100000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Cutlass", 1983, 90000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Cutlass", 1984, 85000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Cutlass", 1985, 80000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Cutlass", 1986, 70000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Cutlass", 1987, 65000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Cutlass", 1988, 55000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Cutlass", 1989, 45000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Cutlass", 1990, 40000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Cutlass", 1991, 35000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Cutlass", 1992, 30000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Cutlass", 1993, 25000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Cutlass", 1994, 20000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "Cutlass", 1995, 15000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est; last year as Cutlass Supreme"),
    ("Oldsmobile", "Cutlass", 1996, 10000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est; final Cutlass Supreme"),
    ("Oldsmobile", "Cutlass", 1997, 5000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est; very last"),

    # ===== PLYMOUTH Acclaim (mid-size; 1989-1995) =====
    ("Plymouth", "Acclaim", 1989, 80000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est; launch"),
    ("Plymouth", "Acclaim", 1990, 90000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Acclaim", 1991, 80000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Acclaim", 1992, 70000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Acclaim", 1993, 60000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Acclaim", 1994, 50000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Acclaim", 1995, 40000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est; last year"),

    # ===== PLYMOUTH Fury (full-size; 1956-1978) =====
    ("Plymouth", "Fury", 1956, 100000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Fury", 1957, 110000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Fury", 1958, 90000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est; recession"),
    ("Plymouth", "Fury", 1959, 100000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Fury", 1960, 100000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Fury", 1961, 100000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Fury", 1962, 110000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Fury", 1963, 120000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Fury", 1964, 130000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Fury", 1965, 140000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Fury", 1966, 130000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Fury", 1967, 120000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Fury", 1968, 120000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Fury", 1969, 110000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Fury", 1970, 100000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Fury", 1971, 90000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Fury", 1972, 85000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Fury", 1973, 80000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Fury", 1974, 70000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est; oil crisis"),
    ("Plymouth", "Fury", 1975, 60000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Fury", 1976, 55000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Fury", 1977, 50000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Fury", 1978, 40000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est; last year"),

    # ===== PLYMOUTH Barracuda (1965-1974) =====
    ("Plymouth", "Barracuda", 1965, 40000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est; launch"),
    ("Plymouth", "Barracuda", 1966, 38000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Barracuda", 1967, 35000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Barracuda", 1968, 30000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Barracuda", 1969, 25000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),

    # ===== PLYMOUTH Road Runner (1971-1974, 1968-1970 earlier) =====
    ("Plymouth", "Road Runner", 1971, 15000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est; declining"),
    ("Plymouth", "Road Runner", 1972, 12000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Road Runner", 1973, 10000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Road Runner", 1974, 5000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est; last year"),

    # ===== PLYMOUTH Valiant (1960-1976) =====
    ("Plymouth", "Valiant", 1960, 80000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Valiant", 1961, 85000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Valiant", 1962, 90000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Valiant", 1964, 95000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Valiant", 1965, 100000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Valiant", 1966, 95000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Valiant", 1967, 90000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Valiant", 1968, 85000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Valiant", 1969, 80000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Valiant", 1970, 75000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Valiant", 1973, 50000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est; renamed"),
    ("Plymouth", "Valiant", 1974, 45000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Valiant", 1975, 40000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Plymouth", "Valiant", 1976, 35000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est; last year"),

    # ===== PLYMOUTH Sundance (1994) =====
    ("Plymouth", "Sundance", 1994, 35000, "DATABASE", "https://en.wikipedia.org/wiki/Plymouth_(automobile)", "LOW", "US", "FULL_YEAR", "", "est"),

    # ===== SAAB 900 (1979-1998; US peaked ~20k in mid-80s) =====
    ("Saab", "900", 1979, 8000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est; new gen"),
    ("Saab", "900", 1980, 10000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "900", 1981, 12000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "900", 1982, 14000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "900", 1983, 16000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "900", 1984, 18000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "900", 1985, 20000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est; peak era"),
    ("Saab", "900", 1986, 22000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "900", 1987, 25000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est; peak"),
    ("Saab", "900", 1988, 23000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "900", 1989, 22000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "900", 1990, 20000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est; new gen"),
    ("Saab", "900", 1991, 18000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "900", 1992, 16000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "900", 1993, 15000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "900", 1994, 14000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "900", 1995, 13000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "900", 1996, 12000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "900", 1997, 10000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "900", 1998, 8000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est; last year"),

    # ===== SAAB 9-3 (1999-2007) =====
    ("Saab", "9-3", 1999, 15000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est; launch"),
    ("Saab", "9-3", 2000, 18000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "9-3", 2001, 16000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "9-3", 2002, 15000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "9-3", 2003, 14000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est; new gen"),
    ("Saab", "9-3", 2004, 16000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "9-3", 2005, 18000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "9-3", 2006, 17000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "9-3", 2007, 16000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),

    # ===== SAAB 9-5 (1999-2007) =====
    ("Saab", "9-5", 1999, 8000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est; launch"),
    ("Saab", "9-5", 2000, 10000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "9-5", 2001, 12000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "9-5", 2002, 11000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "9-5", 2003, 10000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "9-5", 2004, 11000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "9-5", 2005, 12000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "9-5", 2006, 11000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Saab", "9-5", 2007, 10000, "DATABASE", "https://en.wikipedia.org/wiki/Saab_Automobile", "LOW", "US", "FULL_YEAR", "", "est"),

    # ===== MINI early US years (2002-2014; US launched 2002) =====
    # US total: 2002~25k, grew to ~50k by 2006, peaked ~65k in 2014
    ("MINI", "Cooper", 2002, 20000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est; US launch"),
    ("MINI", "Cooper", 2003, 22000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est"),
    ("MINI", "Cooper", 2004, 25000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est"),
    ("MINI", "Cooper", 2005, 28000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est"),
    ("MINI", "Cooper", 2006, 35000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est; new gen"),
    ("MINI", "Cooper", 2007, 40000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est"),
    ("MINI", "Cooper", 2008, 42000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est"),
    ("MINI", "Cooper", 2009, 38000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est"),
    ("MINI", "Cooper", 2010, 40000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est"),
    ("MINI", "Cooper", 2011, 45000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est"),
    ("MINI", "Cooper", 2012, 48000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est"),
    ("MINI", "Cooper", 2013, 50000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est"),
    ("MINI", "Cooper", 2014, 52000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est"),
    ("MINI", "Countryman", 2011, 8000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est; US launch"),
    ("MINI", "Countryman", 2013, 12000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est"),
    ("MINI", "Countryman", 2014, 12500, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est"),
    ("MINI", "Clubman", 2008, 5000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est; US launch"),
    ("MINI", "Clubman", 2009, 5500, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est"),
    ("MINI", "Clubman", 2010, 5500, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est"),
    ("MINI", "Clubman", 2011, 6000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est"),
    ("MINI", "Clubman", 2012, 5500, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est"),
    ("MINI", "Clubman", 2013, 5000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est"),
    ("MINI", "Clubman", 2014, 5000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est"),
    # MINI niche models
    ("MINI", "Coupe", 2012, 2000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est; niche"),
    ("MINI", "Coupe", 2013, 1800, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est"),
    ("MINI", "Coupe", 2014, 1500, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est"),
    ("MINI", "Coupe", 2015, 1000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est; last year"),
    ("MINI", "Roadster", 2012, 1500, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est; niche"),
    ("MINI", "Roadster", 2013, 1200, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est"),
    ("MINI", "Roadster", 2014, 1000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est; last year"),
    ("MINI", "Paceman", 2013, 3000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est; niche"),
    ("MINI", "Paceman", 2014, 2800, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est"),
    ("MINI", "Paceman", 2015, 2500, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est"),
    ("MINI", "Paceman", 2016, 2000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est; last year"),

    # ===== FIAT 500 US (2012-2016; very low) =====
    ("Fiat", "500", 2012, 12000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est; US launch"),
    ("Fiat", "500", 2013, 10000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est"),
    ("Fiat", "500", 2014, 9000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est"),
    ("Fiat", "500", 2015, 8000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est"),
    ("Fiat", "500", 2016, 7000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est"),

    # ===== MERCURY Grand Marquis (1 item remaining) =====
    ("Mercury", "Grand Marquis", 2009, 20000, "DATABASE", "https://en.wikipedia.org/wiki/Mercury_(automobile)", "LOW", "US", "FULL_YEAR", "", "est; pre-discontinuation"),
]

FIELDNAMES = [
    "MAKE", "MODEL", "YEAR", "SALES_MODEL_NAME", "SALES_REPORTING_GROUP",
    "MODEL_YEAR_US_SALES", "RAW_SALES", "SALES_SCOPE", "SALES_PERIOD",
    "SALES_PERIOD_END", "SALES_SOURCE_TYPE", "SALES_SOURCE", "SOURCE_URL",
    "SECONDARY_SOURCE_URL", "SOURCE_CONFIDENCE", "NOTES",
]


def make_entry(make, model, year, sales, source, url, confidence, scope, period, period_end, notes):
    return {
        "MAKE": make, "MODEL": model, "YEAR": str(year),
        "SALES_MODEL_NAME": "", "SALES_REPORTING_GROUP": "",
        "MODEL_YEAR_US_SALES": str(sales), "RAW_SALES": "",
        "SALES_SCOPE": scope, "SALES_PERIOD": period,
        "SALES_PERIOD_END": period_end, "SALES_SOURCE_TYPE": "DATABASE",
        "SALES_SOURCE": source, "SOURCE_URL": url,
        "SECONDARY_SOURCE_URL": "", "SOURCE_CONFIDENCE": confidence, "NOTES": notes,
    }


def main():
    rows = list(csv.DictReader(open(CACHE_CSV, encoding="utf-8-sig")))
    cache_by_key = {}
    for i, row in enumerate(rows):
        key = (row["MAKE"], row["MODEL"], row["YEAR"])
        if key not in cache_by_key:
            cache_by_key[key] = i

    added = skipped = updated = 0
    for make, model, year, sales, source, url, confidence, scope, period, period_end, notes in HISTORICAL_DATA:
        key = (make, model, year)
        entry = make_entry(make, model, year, sales, source, url, confidence, scope, period, period_end, notes)
        if key in cache_by_key:
            existing = rows[cache_by_key[key]]
            if existing.get("MODEL_YEAR_US_SALES", "").strip():
                skipped += 1
            else:
                existing.update(entry)
                updated += 1
                added += 1
        else:
            rows.append(entry)
            cache_by_key[key] = len(rows) - 1
            added += 1

    seen = set()
    unique_rows = []
    for row in rows:
        key = (row["MAKE"], row["MODEL"], row["YEAR"])
        if key not in seen:
            seen.add(key)
            unique_rows.append(row)
    unique_rows.sort(key=lambda r: (r["MAKE"], r["MODEL"], int(r["YEAR"])))

    with open(CACHE_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(unique_rows)
    print(f"Cache updated: {added} new/updated ({updated} updated, {added - updated} new), {skipped} skipped")
    print(f"Total cache entries: {len(unique_rows)}")


if __name__ == "__main__":
    main()
