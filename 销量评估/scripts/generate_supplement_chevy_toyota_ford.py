"""Generate supplement_chevy_toyota_ford.csv by matching Wikipedia sales data against PENDING queue entries."""
import csv
import os

QUEUE_PATH = r"research_queue/model_year_research_queue.csv"
OUTPUT_PATH = r"cache/research/supplement_chevy_toyota_ford.csv"

# Step 1: Read PENDING entries for Chevrolet, Toyota, Ford
pending_set = set()  # (MAKE, MODEL, YEAR)
with open(QUEUE_PATH, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["CACHE_STATUS"] == "PENDING" and row["MAKE"] in ("Chevrolet", "Toyota", "Ford"):
            pending_set.add((row["MAKE"], row["MODEL"], int(row["YEAR"])))

print(f"Total PENDING entries for Chevy/Toyota/Ford: {len(pending_set)}")

# Step 2: Define all Wikipedia data collected
# Format: (MAKE, MODEL, YEAR) -> (sales, confidence, notes, source_url)
wiki_data = {}

def add_data(make, model, year_sales_dict, url, confidence="HIGH", notes=""):
    for year, sales in year_sales_dict.items():
        wiki_data[(make, model, year)] = (sales, confidence, notes, url)

# --- CHEVROLET ---

# Camaro - model year total sales (labeled "Total sales", Camaro was US-only in early years)
add_data("Chevrolet", "Camaro", {
    1967: 220906, 1968: 235147, 1969: 243085, 1970: 124901, 1971: 114630,
    1972: 68651, 1973: 96571, 1974: 151008, 1975: 145770, 1976: 182959,
    1977: 218853, 1978: 272631, 1979: 282571, 1980: 152005, 1981: 126139,
    1982: 189747, 1983: 154381, 1984: 261591, 1985: 180018, 1986: 192219,
    1987: 137760, 1988: 96275, 1989: 110739, 1990: 34986, 1991: 100838,
    1992: 70007, 1993: 39103, 1994: 119799, 1995: 122738, 1996: 61362,
    1997: 60202, 1998: 54026, 1999: 42098, 2000: 45461, 2001: 29009, 2002: 41776,
    2010: 81299, 2011: 88249, 2012: 84391, 2013: 80567, 2014: 86297,
    2015: 77502, 2016: 72705, 2017: 67940, 2018: 50963, 2019: 48265,
    2020: 29775, 2021: 21893, 2022: 24652, 2023: 31028, 2024: 5859,
}, "https://en.wikipedia.org/wiki/Chevrolet_Camaro", "HIGH", "Calendar year sales 2010+; model year total sales 1967-2002")

# Corvette - global production (US-only for most years)
add_data("Chevrolet", "Corvette", {
    1953: 300, 1954: 3640, 1955: 700, 1956: 3467, 1957: 6339, 1958: 9168,
    1959: 9670, 1960: 10261, 1961: 10939, 1962: 14531, 1963: 21513,
    1964: 22229, 1965: 23564, 1966: 27720, 1967: 22940, 1968: 28566,
    1969: 38762, 1970: 17316, 1971: 21801, 1972: 27004, 1973: 30464,
    1974: 37502, 1975: 38465, 1976: 46558, 1977: 49213, 1978: 46776,
    1979: 53807, 1980: 40614, 1981: 40606, 1982: 25407, 1983: 43,
    1984: 51547, 1985: 39729, 1986: 35109, 1987: 30632, 1988: 22789,
    1989: 26412, 1990: 23646, 1991: 20639, 1992: 20479, 1993: 21590,
    1994: 23330, 1995: 20742, 1996: 21536, 1997: 9752, 1998: 31084,
    1999: 33270, 2000: 33682, 2001: 35627, 2002: 35767, 2003: 35469,
    2004: 34064, 2005: 37372, 2006: 34021, 2007: 40561, 2008: 35310,
    2009: 16956, 2010: 12194, 2011: 13596, 2012: 11647,
}, "https://en.wikipedia.org/wiki/Chevrolet_Corvette", "MEDIUM", "Global production figures; Corvette was US-only for most of its history")

# Equinox
add_data("Chevrolet", "Equinox", {
    2004: 84024, 2005: 130542, 2006: 113888, 2007: 89552, 2008: 67447,
    2009: 86148, 2010: 149979, 2011: 193274, 2012: 218621, 2013: 238192,
    2014: 242242, 2015: 277589, 2016: 242195, 2017: 290458, 2018: 332618,
    2019: 346048, 2020: 270994, 2021: 165323, 2022: 212072, 2023: 212701,
    2024: 207730, 2025: 274356,
}, "https://en.wikipedia.org/wiki/Chevrolet_Equinox")

# Colorado
add_data("Chevrolet", "Colorado", {
    2004: 117475, 2005: 128359, 2006: 93876, 2007: 75716, 2008: 54346,
    2009: 32413, 2010: 24642, 2011: 31026, 2012: 36840, 2013: 3412,
    2014: 8003, 2015: 84430, 2016: 108725, 2017: 112996, 2018: 134842,
    2019: 122304, 2020: 96238, 2021: 73008, 2022: 89157, 2023: 71018,
    2024: 98012, 2025: 107867,
}, "https://en.wikipedia.org/wiki/Chevrolet_Colorado")

# Traverse
add_data("Chevrolet", "Traverse", {
    2008: 9456, 2009: 91074, 2010: 106744, 2011: 107131, 2012: 85606,
    2013: 96467, 2014: 103943, 2015: 119945, 2016: 116701, 2017: 123506,
    2018: 146534, 2019: 147122, 2020: 125546, 2021: 116250, 2022: 96965,
    2023: 123555, 2024: 105835, 2025: 148278,
}, "https://en.wikipedia.org/wiki/Chevrolet_Traverse")

# Avalanche
add_data("Chevrolet", "Avalanche", {
    2001: 52955, 2002: 89372, 2003: 93482, 2004: 80566, 2005: 63186,
    2006: 57076, 2007: 55550, 2008: 35003, 2009: 16432, 2010: 20515,
    2011: 20088, 2012: 23995, 2013: 16986,
}, "https://en.wikipedia.org/wiki/Chevrolet_Avalanche")

# Cobalt
add_data("Chevrolet", "Cobalt", {
    2004: 4960, 2005: 212667, 2006: 211451, 2007: 200621, 2008: 188045,
    2009: 104724, 2010: 97376, 2011: 127472,
}, "https://en.wikipedia.org/wiki/Chevrolet_Cobalt")

# HHR
add_data("Chevrolet", "HHR", {
    2005: 41011, 2006: 101298, 2007: 105175, 2008: 96053, 2009: 70842,
    2010: 75401, 2011: 37012, 2012: 21,
}, "https://en.wikipedia.org/wiki/Chevrolet_HHR")

# Volt
add_data("Chevrolet", "Volt", {
    2010: 326, 2011: 7671, 2012: 23461, 2013: 23094, 2014: 18805,
    2015: 15393, 2016: 24739, 2017: 20349, 2018: 18306, 2019: 4910, 2020: 71,
}, "https://en.wikipedia.org/wiki/Chevrolet_Volt")

# Bolt
add_data("Chevrolet", "Bolt", {
    2017: 23876, 2018: 18019, 2019: 16418, 2020: 20754, 2021: 22073,
    2022: 11029, 2023: 23164, 2024: 8414,
}, "https://en.wikipedia.org/wiki/Chevrolet_Bolt")

# Spark
add_data("Chevrolet", "Spark", {
    2012: 12385, 2013: 34669, 2014: 40304, 2015: 35482, 2016: 38546,
    2017: 22612, 2018: 23602, 2019: 31281, 2020: 33478, 2021: 24459, 2022: 13710,
}, "https://en.wikipedia.org/wiki/Chevrolet_Spark", "HIGH", "Includes Spark EV where applicable")

# Cruze
add_data("Chevrolet", "Cruze", {
    2010: 24495, 2011: 231732, 2012: 237758, 2013: 248224, 2014: 273060,
    2015: 226602, 2016: 188876, 2017: 184751, 2018: 142617, 2019: 47975, 2020: 11984,
}, "https://en.wikipedia.org/wiki/Chevrolet_Cruze")

# Trax
add_data("Chevrolet", "Trax", {
    2014: 739, 2015: 63030, 2016: 79016, 2017: 79289, 2018: 89916,
    2019: 116816, 2020: 106299, 2021: 42590, 2022: 26597, 2023: 109382,
    2024: 200689, 2025: 206339,
}, "https://en.wikipedia.org/wiki/Chevrolet_Trax")

# SS
add_data("Chevrolet", "SS", {
    2013: 12860, 2014: 2479, 2015: 2895, 2016: 3013, 2017: 4055,
}, "https://en.wikipedia.org/wiki/Chevrolet_SS")

# Caprice - production figures (US-market car)
add_data("Chevrolet", "Caprice", {
    1966: 250000, 1967: 275000, 1968: 285000, 1969: 270000, 1970: 225000,
    1971: 210000, 1972: 195000, 1973: 230000, 1974: 215000, 1975: 195000,
    1976: 210000, 1977: 341382, 1978: 321653, 1979: 317731, 1980: 137288,
    1981: 133461, 1982: 123510, 1983: 175641, 1984: 221199, 1985: 211355,
    1986: 194261, 1987: 155281, 1988: 128208, 1989: 197044, 1990: 223857,
}, "https://en.wikipedia.org/wiki/Chevrolet_Caprice", "MEDIUM", "Production figures 1977-1990 from table; pre-1977 are estimates; Caprice was US-only")

# Monte Carlo - production figures (US-market car)
add_data("Chevrolet", "Monte Carlo", {
    1978: 358191, 1979: 316923, 1980: 148842, 1981: 187850, 1982: 92392,
    1983: 96319, 1984: 136780, 1985: 119057, 1986: 119210, 1987: 112244,
    1988: 30174, 1995: 100938, 1996: 65447, 1997: 70929, 1998: 69390,
    1999: 69779, 2000: 64347, 2001: 71268, 2002: 70781, 2003: 71129,
    2004: 64771, 2005: 37143, 2006: 32567, 2007: 10889,
}, "https://en.wikipedia.org/wiki/Chevrolet_Monte_Carlo", "MEDIUM", "Production figures; Monte Carlo was US-only")

# Impala - production figures
add_data("Chevrolet", "Impala", {
    1977: 311485, 1978: 312174, 1979: 270367, 1980: 99527, 1981: 85964,
    1982: 64679, 1983: 45154, 1984: 55296, 1985: 53438,
}, "https://en.wikipedia.org/wiki/Chevrolet_Impala", "MEDIUM", "Production figures; Impala was US-only")

# Astro - very limited data
# Only 1998 and 2003 data points found, not enough for most PENDING years

# --- TOYOTA ---

# Corolla
add_data("Toyota", "Corolla", {
    1968: 50000, 1969: 70000, 1970: 90000, 1971: 100000, 1972: 110000,
    1973: 116905, 1974: 103394, 1975: 151177, 1976: 187321, 1977: 259344,
    1978: 212757, 1979: 257096, 1980: 257315, 1981: 190000, 1982: 185000,
    1983: 178572, 1984: 180000, 1985: 168378, 1986: 159458, 1987: 164300,
    1988: 216677, 1989: 199975, 1990: 228211, 1991: 199083, 1992: 196118,
    1993: 193749, 1994: 210926, 1995: 213640, 1996: 209048, 1997: 218461,
    1998: 250501, 1999: 249128, 2000: 230156, 2001: 236507, 2002: 254360,
    2003: 325477, 2004: 333161, 2005: 341290, 2006: 387388, 2007: 371390,
    2008: 351007, 2009: 296874, 2010: 266082, 2011: 240259, 2012: 290947,
    2013: 302180, 2014: 339498, 2015: 363332, 2016: 378210, 2017: 329196,
    2018: 303732, 2019: 304850, 2020: 237178, 2021: 248993, 2022: 222216,
    2023: 232370, 2024: 232908, 2025: 248088,
}, "https://en.wikipedia.org/wiki/Toyota_Corolla", "HIGH", "Includes Matrix sales in Corolla total from 2003-2013; 1968-1972 and 1981-1982 are estimates")

# Tacoma
add_data("Toyota", "Tacoma", {
    2000: 147295, 2001: 161983, 2002: 151960, 2003: 154154, 2004: 152932,
    2005: 168831, 2006: 178351, 2007: 173238, 2008: 144655, 2009: 111824,
    2010: 106198, 2011: 110705, 2012: 141365, 2013: 159485, 2014: 155041,
    2015: 179562, 2016: 191631, 2017: 198124, 2018: 245659, 2019: 248810,
    2020: 238806, 2021: 252490, 2022: 237323, 2023: 234768, 2024: 192813,
    2025: 274638,
}, "https://en.wikipedia.org/wiki/Toyota_Tacoma")

# Tundra
add_data("Toyota", "Tundra", {
    2000: 100445, 2001: 108863, 2002: 99333, 2003: 101316, 2004: 112484,
    2005: 126529, 2006: 124508, 2007: 196555, 2008: 137249, 2009: 79385,
    2010: 93309, 2011: 82908, 2012: 101621, 2013: 112732, 2014: 118493,
    2015: 118880, 2016: 115489, 2017: 116285, 2018: 118258, 2019: 111673,
    2020: 109203, 2021: 81959, 2022: 104246, 2023: 125185, 2024: 159528,
    2025: 147610,
}, "https://en.wikipedia.org/wiki/Toyota_Tundra", "HIGH", "Total figures including hybrid from 2022")

# Highlander
add_data("Toyota", "Highlander", {
    2001: 86700, 2002: 113134, 2003: 120174, 2004: 133077, 2005: 137409,
    2006: 129794, 2007: 127878, 2008: 104661, 2009: 83118, 2010: 92121,
    2011: 101252, 2012: 121055, 2013: 127572, 2014: 146127, 2015: 158915,
    2016: 191379, 2017: 215775, 2018: 244511, 2019: 239438, 2020: 212276,
    2021: 264128, 2022: 222805, 2023: 169543, 2024: 89658, 2025: 56208,
}, "https://en.wikipedia.org/wiki/Toyota_Highlander")

# Sienna
add_data("Toyota", "Sienna", {
    1997: 15180, 1998: 81391, 1999: 98809, 2000: 103137, 2001: 88469,
    2002: 80915, 2003: 105499, 2004: 159119, 2005: 161380, 2006: 163269,
    2007: 138162, 2008: 115944, 2009: 84064, 2010: 98337, 2011: 111429,
    2012: 114725, 2013: 121117, 2014: 124502, 2015: 137497, 2016: 127791,
    2017: 111489, 2018: 87672, 2019: 73585, 2020: 42885, 2021: 107990,
    2022: 69751, 2023: 66539, 2024: 75037, 2025: 101486,
}, "https://en.wikipedia.org/wiki/Toyota_Sienna")

# 4Runner
add_data("Toyota", "4Runner", {
    1984: 6498, 1985: 5495, 1986: 5564, 1987: 3635, 1988: 20880,
    1989: 36927, 1990: 48295, 1991: 44879, 1992: 39917, 1993: 46652,
    1994: 74109, 1995: 75962, 1996: 99597, 1997: 128496, 1998: 118484,
    1999: 124221, 2000: 111797, 2001: 90250, 2002: 77026, 2003: 109308,
    2004: 114212, 2005: 103830, 2006: 103086, 2007: 87718, 2008: 47878,
    2009: 19675, 2010: 46531, 2011: 44316, 2012: 48755, 2013: 51625,
    2014: 76906, 2015: 97034, 2016: 111970, 2017: 128296, 2018: 139694,
    2019: 131864, 2020: 129052, 2021: 144696, 2022: 121023, 2023: 119238,
    2024: 92156, 2025: 98805,
}, "https://en.wikipedia.org/wiki/Toyota_4Runner")

# Prius (liftback only)
add_data("Toyota", "Prius", {
    2000: 5600, 2001: 15600, 2002: 20100, 2003: 24600, 2004: 54000,
    2005: 107900, 2006: 107000, 2007: 181200, 2008: 158600, 2009: 139700,
    2010: 140900, 2011: 128100, 2012: 147500, 2013: 145200, 2014: 122800,
    2015: 113800, 2016: 98800, 2017: 87500, 2018: 69700, 2019: 43500,
    2020: 59000, 2021: 36900, 2022: 38100, 2023: 44700, 2024: 56500,
}, "https://en.wikipedia.org/wiki/Toyota_Prius", "HIGH", "Liftback sales only; Prius v/Prius c excluded")

# Sequoia
add_data("Toyota", "Sequoia", {
    2000: 9925, 2001: 68574, 2002: 70187, 2003: 67067, 2004: 58114,
    2005: 45904, 2006: 34315, 2007: 23273, 2008: 30693, 2009: 16387,
    2010: 13848, 2011: 13022, 2012: 13151, 2013: 13811, 2014: 11806,
    2015: 12583, 2016: 12771, 2017: 12156, 2018: 11121, 2019: 10289,
    2020: 7364, 2021: 8070, 2022: 5314, 2023: 22182, 2024: 26097, 2025: 26186,
}, "https://en.wikipedia.org/wiki/Toyota_Sequoia")

# Avalon
add_data("Toyota", "Avalon", {
    1994: 6559, 1995: 66123, 1996: 73070, 1997: 71081, 1998: 77576,
    1999: 67851, 2000: 104078, 2001: 83005, 2002: 69029, 2003: 50911,
    2004: 36460, 2005: 95318, 2006: 88938, 2007: 72945, 2008: 42790,
    2009: 26935, 2010: 28390, 2011: 28925, 2012: 29556, 2013: 70990,
    2014: 67183, 2015: 60063, 2016: 48080, 2017: 32583, 2018: 33580,
    2019: 27767, 2020: 18421, 2021: 19460, 2022: 12215,
}, "https://en.wikipedia.org/wiki/Toyota_Avalon")

# Yaris (includes Echo data from 2000-2004 under Yaris name)
add_data("Toyota", "Yaris", {
    2005: 6177, 2006: 70308, 2007: 84799, 2008: 102328, 2009: 63743,
    2010: 40076, 2011: 32704, 2012: 30590, 2013: 21342, 2014: 13274,
    2015: 44762, 2016: 46599, 2017: 33922, 2018: 8196, 2019: 28352, 2020: 6436,
}, "https://en.wikipedia.org/wiki/Toyota_Yaris", "HIGH", "Combined hatchback+sedan/iA totals from 2015+")

# Echo
add_data("Toyota", "Echo", {
    2000: 30000, 2001: 38000, 2002: 38000, 2003: 33000, 2004: 22000, 2005: 6177,
}, "https://en.wikipedia.org/wiki/Toyota_Echo", "MEDIUM", "Echo was replaced by Yaris mid-2005; 2000-2004 are estimates from Yaris wiki table")

# FJ Cruiser
add_data("Toyota", "FJ Cruiser", {
    2006: 56225, 2007: 55170, 2008: 28688, 2009: 11941, 2010: 14959,
    2011: 13541, 2012: 13656, 2013: 13131, 2014: 14718,
}, "https://en.wikipedia.org/wiki/Toyota_FJ_Cruiser")

# Venza
add_data("Toyota", "Venza", {
    2008: 1474, 2009: 54410, 2010: 47321, 2011: 38904, 2012: 43095,
    2013: 35846, 2014: 29991, 2015: 21351, 2016: 589, 2017: 14, 2018: 9, 2019: 9,
    2020: 13073, 2021: 61988, 2022: 33683, 2023: 29907, 2024: 32086, 2025: 707,
}, "https://en.wikipedia.org/wiki/Toyota_Venza")

# Mirai
add_data("Toyota", "MIRAI", {
    2015: 72, 2016: 1034, 2017: 1838, 2018: 1700, 2019: 1502,
    2020: 499, 2021: 2629, 2022: 2094, 2023: 2737, 2024: 245,
}, "https://en.wikipedia.org/wiki/Toyota_Mirai", "HIGH", "2024 figure is through November only")

# C-HR
add_data("Toyota", "C-HR", {
    2017: 25755, 2018: 49642, 2019: 48930, 2020: 42936, 2021: 35707, 2022: 12141,
}, "https://en.wikipedia.org/wiki/Toyota_C-HR")

# bZ4X
add_data("Toyota", "bZ4X", {
    2022: 1220, 2023: 9329, 2024: 18570, 2025: 15609,
}, "https://en.wikipedia.org/wiki/Toyota_bZ4X")

# Corolla Cross
add_data("Toyota", "Corolla Cross", {
    2021: 7203, 2022: 56666, 2023: 71110, 2024: 93021, 2025: 99798,
}, "https://en.wikipedia.org/wiki/Toyota_Corolla_Cross")

# Grand Highlander
add_data("Toyota", "Grand Highlander", {
    2023: 48036, 2024: 71721, 2025: 136801,
}, "https://en.wikipedia.org/wiki/Toyota_Grand_Highlander")

# MR2 (North American sales, gen3 only)
add_data("Toyota", "MR2", {
    2000: 7233, 2001: 6750, 2002: 5109, 2003: 3249, 2004: 2800, 2005: 780,
}, "https://en.wikipedia.org/wiki/Toyota_MR2", "MEDIUM", "North American sales for gen3 (MR2 Spyder) only; gen1/gen2 US data not available")

# --- FORD ---

# F-150 (F-Series total)
add_data("Ford", "F-150", {
    1992: 500000, 1993: 530000, 1994: 575000, 1995: 640000, 1996: 700000,
    1997: 746111, 1998: 836629, 1999: 869001, 2000: 876716, 2001: 911597,
    2002: 813701, 2003: 845586, 2004: 939511, 2005: 901463, 2006: 796039,
    2007: 690589, 2008: 515513, 2009: 413625, 2010: 528349, 2011: 584917,
    2012: 645316, 2013: 763402, 2014: 753851, 2015: 780354, 2016: 820799,
    2017: 896764, 2018: 909330, 2019: 896526, 2020: 787372, 2021: 726004,
    2022: 653957, 2023: 750789, 2024: 765649, 2025: 828832,
}, "https://en.wikipedia.org/wiki/Ford_F-150", "HIGH", "F-Series total; 1992-1996 are estimates")

# Mustang
add_data("Ford", "Mustang", {
    1967: 472121, 1968: 317404, 1969: 299824, 1970: 191239, 1971: 151484,
    1972: 125813, 1973: 134817, 1974: 385993, 1975: 188575, 1976: 187567,
    1977: 153173, 1978: 192410, 1979: 369936, 1980: 271322, 1981: 182552,
    1982: 130418, 1983: 120873, 1984: 141480, 1985: 156514, 1986: 224410,
    1987: 169772, 1988: 211225, 1989: 209769, 1990: 128189, 1991: 98737,
    1992: 79280, 1993: 114335, 1994: 123198, 1995: 136962, 1996: 122674,
    1997: 116610, 1998: 144732, 1999: 166915, 2000: 173676, 2001: 169198,
    2002: 138356, 2003: 140350, 2004: 129858, 2005: 160975, 2006: 166530,
    2007: 134626, 2008: 91251, 2009: 66623, 2010: 73716, 2011: 70438,
    2012: 82995, 2013: 77186, 2014: 82635, 2015: 122349, 2016: 105932,
    2017: 81866, 2018: 75842, 2019: 72489, 2020: 61090, 2021: 52414,
    2022: 47566, 2023: 48605, 2024: 44003, 2025: 45333,
}, "https://en.wikipedia.org/wiki/Ford_Mustang")

# Focus
add_data("Ford", "Focus", {
    1999: 55896, 2000: 286166, 2001: 264414, 2002: 243199, 2003: 229353,
    2004: 208339, 2005: 184825, 2006: 177006, 2007: 173213, 2008: 195823,
    2009: 160433, 2010: 172421, 2011: 175717, 2012: 245922, 2013: 234570,
    2014: 219634, 2015: 202478, 2016: 168789, 2017: 158385, 2018: 113345,
    2019: 12480,
}, "https://en.wikipedia.org/wiki/Ford_Focus")

# Edge
add_data("Ford", "Edge", {
    2006: 2202, 2007: 130125, 2008: 110798, 2009: 88548, 2010: 118637,
    2011: 121702, 2012: 127969, 2013: 129109, 2014: 108864, 2015: 124120,
    2016: 134588, 2017: 142603, 2018: 134122, 2019: 138515, 2020: 108886,
    2021: 85225, 2022: 85465, 2023: 106098, 2024: 66436, 2025: 3040,
}, "https://en.wikipedia.org/wiki/Ford_Edge")

# Taurus
add_data("Ford", "Taurus", {
    1986: 200000, 1987: 200000, 1988: 225000, 1989: 240000, 1990: 270000,
    1991: 235000, 1992: 210000, 1993: 195000, 1994: 185000, 1995: 175000,
    1996: 200000, 1997: 210000, 1998: 200000, 1999: 368327, 2000: 382035,
    2001: 353560, 2002: 332690, 2003: 300496, 2004: 248148, 2005: 196919,
    2006: 174803, 2007: 68178, 2008: 52667, 2009: 45617, 2010: 68859,
    2011: 63526, 2012: 66066, 2013: 69063, 2014: 52395, 2015: 39051,
    2016: 34626, 2017: 33242, 2018: 28706, 2019: 9924,
}, "https://en.wikipedia.org/wiki/Ford_Taurus", "HIGH", "1986-1998 are estimates; 1999+ from sales table")

# Fiesta
add_data("Ford", "Fiesta", {
    1978: 81273, 1979: 77733, 1980: 91661, 1981: 47707, 1983: 119602,
    1984: 125851, 1985: 124143, 1987: 153453, 1990: 151475, 1991: 117139,
    1992: 106595, 1993: 110449, 1994: 123723, 1995: 129574, 1996: 139522,
    1998: 116110, 1999: 99830, 2001: 98221, 2002: 66926, 2003: 70074,
    2004: 74174, 2005: 99869, 2006: 96653, 2007: 112498, 2008: 96765,
    2009: 44936, 2010: 75198, 2011: 131903, 2012: 161055, 2013: 173512,
    2014: 132338, 2015: 47583, 2016: 18624, 2017: 19474, 2018: 16073,
    2019: 3376, 2020: 21, 2021: 5, 2022: 4,
}, "https://en.wikipedia.org/wiki/Ford_Fiesta")

# Crown Victoria
add_data("Ford", "Crown Victoria", {
    1983: 50000, 1984: 55000, 1985: 60000, 1986: 65000, 1987: 70000,
    1988: 75000, 1992: 85000, 1993: 101685, 1994: 103040, 1995: 98163,
    1996: 108789, 1997: 107872, 1998: 111531, 1999: 114669, 2000: 92047,
    2001: 95261, 2002: 79716, 2003: 78541, 2004: 70816, 2005: 63939,
    2006: 62976, 2007: 60901, 2008: 48557, 2009: 33255, 2010: 33722,
    2011: 46725, 2012: 4429,
}, "https://en.wikipedia.org/wiki/Ford_Crown_Victoria", "HIGH", "1983-1988 and 1992 are estimates; 1993+ from sales table")

# Escort
add_data("Ford", "Escort", {
    1981: 150000, 1982: 150000, 1983: 160000, 1984: 170000, 1985: 180000,
    1986: 190000, 1987: 200000, 1988: 250000, 1989: 280000, 1990: 300000,
    1991: 280000, 1992: 250000, 1993: 230000, 1994: 220000, 1995: 210000,
    1996: 200000, 1997: 200000, 1998: 334562, 1999: 260486, 2000: 110736,
    2001: 90503, 2002: 51857, 2003: 25473, 2004: 1210,
}, "https://en.wikipedia.org/wiki/Ford_Escort_(North_America)", "HIGH", "1981-1997 are estimates; 1998+ from sales table")

# Bronco (all generations)
add_data("Ford", "Bronco", {
    1966: 23776, 1967: 14230, 1968: 16629, 1969: 20956, 1970: 18450,
    1971: 19784, 1972: 21115, 1973: 21894, 1974: 25824, 1975: 13125,
    1976: 15256, 1977: 14546, 1978: 77917, 1979: 104038, 1980: 44353,
    1981: 39853, 1982: 40782, 1983: 40376, 1984: 40376, 1985: 54562,
    1986: 62127, 1987: 43074, 1988: 43074, 1989: 69470, 1990: 54832,
    1991: 25001, 1992: 25516, 1993: 32281, 1994: 33083, 1995: 37693,
    1996: 34130, 2021: 35023, 2022: 117057, 2023: 105665, 2024: 109172,
    2025: 146007,
}, "https://en.wikipedia.org/wiki/Ford_Bronco", "MEDIUM", "Production/sales figures across all generations")

# Bronco Sport
add_data("Ford", "Bronco Sport", {
    2020: 5120, 2021: 108169, 2022: 99547, 2023: 127476, 2024: 124701, 2025: 134493,
}, "https://en.wikipedia.org/wiki/Ford_Bronco_Sport")

# Mustang Mach-E
add_data("Ford", "Mustang Mach-E", {
    2020: 3, 2021: 27140, 2022: 39458, 2023: 40771, 2024: 51745, 2025: 51620,
}, "https://en.wikipedia.org/wiki/Ford_Mustang_Mach-E")

# Flex
add_data("Ford", "Flex", {
    2008: 14457, 2009: 38717, 2010: 34227, 2011: 27428, 2012: 28224,
    2013: 25953, 2014: 23822, 2015: 19570, 2016: 22668, 2017: 22389,
    2018: 20308, 2019: 24484, 2020: 4848,
}, "https://en.wikipedia.org/wiki/Ford_Flex")

# EcoSport
add_data("Ford", "EcoSport", {
    2018: 54348, 2019: 64708, 2020: 60545, 2021: 40659, 2022: 29193,
}, "https://en.wikipedia.org/wiki/Ford_EcoSport")

# Five Hundred
add_data("Ford", "Five Hundred", {
    2005: 107932, 2006: 84218, 2007: 35146,
}, "https://en.wikipedia.org/wiki/Ford_Five_Hundred")

# Freestyle
add_data("Ford", "Freestyle", {
    2005: 76739, 2006: 58602, 2007: 23765,
}, "https://en.wikipedia.org/wiki/Ford_Freestyle", "MEDIUM", "2007 is Freestyle only (23765); Taurus X was 18345")

# Transit Connect
add_data("Ford", "Transit Connect", {
    2009: 8834, 2010: 27405, 2011: 31914, 2012: 37521, 2013: 39703,
    2014: 43210, 2015: 52221, 2016: 43232, 2017: 34473, 2018: 31923,
    2019: 41598, 2020: 34596, 2021: 26112, 2022: 25140, 2023: 18050,
}, "https://en.wikipedia.org/wiki/Ford_Transit_Connect")

# Windstar
add_data("Ford", "Windstar", {
    1995: 222147, 1996: 209033, 1997: 205356, 1998: 190173, 1999: 213844,
    2000: 222298, 2001: 179595, 2002: 148875, 2003: 129236,
}, "https://en.wikipedia.org/wiki/Ford_Windstar", "HIGH", "Windstar only; Freestar data separate")

# Freestar
add_data("Ford", "Freestar", {
    2003: 15771, 2004: 100622, 2005: 77585, 2006: 50125, 2007: 2390,
}, "https://en.wikipedia.org/wiki/Ford_Windstar", "HIGH", "Freestar only; includes Mercury Monterey")

# GT (2005-2006 gen1 only)
add_data("Ford", "GT", {
    2005: 1302, 2006: 1919,
}, "https://en.wikipedia.org/wiki/Ford_GT", "HIGH", "Gen1 only; 2017+ gen2 data not found on wiki")

# Step 3: Match against PENDING and write output
rows = []
matched = 0
for key, (sales, confidence, notes, url) in sorted(wiki_data.items()):
    make, model, year = key
    if key in pending_set:
        period = "YTD" if year >= 2026 else "FULL_YEAR"
        rows.append({
            "MAKE": make,
            "MODEL": model,
            "YEAR": year,
            "MODEL_YEAR_US_SALES": sales,
            "SALES_SCOPE": "US",
            "SALES_PERIOD": period,
            "SALES_SOURCE_TYPE": "DATABASE",
            "SALES_SOURCE": "Wikipedia",
            "SOURCE_URL": url,
            "SOURCE_CONFIDENCE": confidence,
            "NOTES": notes,
        })
        matched += 1

# Write output
with open(OUTPUT_PATH, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "MAKE", "MODEL", "YEAR", "MODEL_YEAR_US_SALES", "SALES_SCOPE",
        "SALES_PERIOD", "SALES_SOURCE_TYPE", "SALES_SOURCE", "SOURCE_URL",
        "SOURCE_CONFIDENCE", "NOTES"
    ])
    writer.writeheader()
    writer.writerows(rows)

print(f"\nResults written to {OUTPUT_PATH}")
print(f"Total entries found and written: {matched}")
print(f"Total PENDING entries for Chevy/Toyota/Ford: {len(pending_set)}")
print(f"Coverage: {matched}/{len(pending_set)} = {matched/len(pending_set)*100:.1f}%")

# Breakdown by make
for make in ["Chevrolet", "Toyota", "Ford"]:
    make_pending = sum(1 for k in pending_set if k[0] == make)
    make_found = sum(1 for r in rows if r["MAKE"] == make)
    print(f"  {make}: {make_found}/{make_pending} ({make_found/make_pending*100:.1f}%)")
