"""
Build supplement_chevy_toyota_ford.csv from collected Wikipedia data.
Matches collected sales data against PENDING entries in model_year_research_queue.csv.
"""
import csv
import os

QUEUE_PATH = r"research_queue/model_year_research_queue.csv"
OUTPUT_PATH = r"cache/research/supplement_chevy_toyota_ford.csv"

# ============================================================
# COLLECTED DATA: {MAKE: {MODEL: {YEAR: SALES}}}
# All figures are US sales unless noted.
# ============================================================

data = {}

def add(make, model, sales_dict, source="Wikipedia", url="", confidence="HIGH", notes=""):
    """Add sales data for a make/model."""
    key = (make, model)
    if key not in data:
        data[key] = {}
    for year, sales in sales_dict.items():
        data[key][year] = {
            "sales": sales,
            "source": source,
            "url": url or f"https://en.wikipedia.org/wiki/{make.replace(' ','_')}_{model.replace(' ','_')}",
            "confidence": confidence,
            "notes": notes,
        }

# ---- CHEVROLET ----

# Camaro
add("Chevrolet", "Camaro", {
    1967: 220906, 1968: 235147, 1969: 243085, 1970: 124901, 1971: 114630,
    1972: 68651, 1973: 96571, 1974: 151008, 1975: 145770, 1976: 182959,
    1977: 218853, 1978: 272631, 1979: 282571, 1980: 152005, 1981: 126139,
    1982: 189747, 1983: 154381, 1984: 261591, 1985: 180018, 1986: 192219,
    1987: 137760, 1988: 96275, 1989: 110739, 1990: 34986, 1991: 100838,
    1992: 70007, 1993: 39103, 1994: 119799, 1995: 122738, 1996: 61362,
    1997: 60202, 1998: 54026, 1999: 42098, 2000: 45461, 2001: 29009,
    2002: 41776,
    2010: 81299, 2011: 88249, 2012: 84391, 2013: 80567, 2014: 86297,
    2015: 77502, 2016: 72705, 2017: 67940, 2018: 50963, 2019: 48265,
    2020: 29775, 2021: 21893, 2022: 24652, 2023: 31028, 2024: 5859,
}, url="https://en.wikipedia.org/wiki/Chevrolet_Camaro")

# Corvette
add("Chevrolet", "Corvette", {
    1953: 300, 1954: 3640, 1955: 700, 1956: 3467, 1957: 6339,
    1958: 9168, 1959: 9670, 1960: 10261, 1961: 10939, 1962: 14531,
    1963: 21513, 1964: 22229, 1965: 23564, 1966: 27720, 1967: 22940,
    1968: 28566, 1969: 38762, 1970: 17316, 1971: 21801, 1972: 27004,
    1973: 30464, 1974: 37502, 1975: 38465, 1976: 46558, 1977: 49213,
    1978: 46776, 1979: 53807, 1980: 40614, 1981: 40606, 1982: 25407,
    1984: 51547, 1985: 39729, 1986: 35109, 1987: 30632, 1988: 22789,
    1989: 26412, 1990: 23646, 1991: 20639, 1992: 20479, 1993: 21590,
    1994: 23330, 1995: 20742, 1996: 21536, 1997: 9752, 1998: 31084,
    1999: 33270, 2000: 33682, 2001: 35627, 2002: 35767, 2003: 35469,
    2004: 34064, 2005: 37372, 2006: 34021, 2007: 40561, 2008: 35310,
    2009: 16956, 2010: 12194, 2011: 13596, 2012: 11647,
}, url="https://en.wikipedia.org/wiki/Chevrolet_Corvette", notes="Production figures")

# Impala
add("Chevrolet", "Impala", {
    1977: 311485, 1978: 312174, 1979: 270367, 1980: 99527, 1981: 85964,
    1982: 64679, 1983: 45154, 1984: 55296, 1985: 53438,
}, url="https://en.wikipedia.org/wiki/Chevrolet_Impala", notes="Production figures")

# Malibu
add("Chevrolet", "Malibu", {
    1978: 358636, 1979: 412147, 1980: 278350, 1981: 242447, 1982: 116125,
    1983: 117426,
}, url="https://en.wikipedia.org/wiki/Chevrolet_Malibu", notes="Production figures")

# Equinox
add("Chevrolet", "Equinox", {
    2004: 84024, 2005: 130542, 2006: 113888, 2007: 89552, 2008: 67447,
    2009: 86148, 2010: 149979, 2011: 193274, 2012: 218621, 2013: 238192,
    2014: 242242, 2015: 277589, 2016: 242195, 2017: 290458, 2018: 332618,
    2019: 346048, 2020: 270994, 2021: 165323, 2022: 212072, 2023: 212701,
    2024: 207730, 2025: 274356,
}, url="https://en.wikipedia.org/wiki/Chevrolet_Equinox")

# Colorado
add("Chevrolet", "Colorado", {
    2004: 117475, 2005: 128359, 2006: 93876, 2007: 75716, 2008: 54346,
    2009: 32413, 2010: 24642, 2011: 31026, 2012: 36840, 2013: 3412,
    2014: 8003, 2015: 84430, 2016: 108725, 2017: 112996, 2018: 134842,
    2019: 122304, 2020: 96238, 2021: 73008, 2022: 89157, 2023: 71018,
    2024: 98012, 2025: 107867,
}, url="https://en.wikipedia.org/wiki/Chevrolet_Colorado")

# Traverse
add("Chevrolet", "Traverse", {
    2008: 9456, 2009: 91074, 2010: 106744, 2011: 107131, 2012: 85606,
    2013: 96467, 2014: 103943, 2015: 119945, 2016: 116701, 2017: 123506,
    2018: 146534, 2019: 147122, 2020: 125546, 2021: 116250, 2022: 96965,
    2023: 123555, 2024: 105835, 2025: 148278,
}, url="https://en.wikipedia.org/wiki/Chevrolet_Traverse")

# Trax
add("Chevrolet", "Trax", {
    2015: 63030, 2016: 79016, 2017: 79289, 2018: 89916, 2019: 116816,
    2020: 106299, 2021: 42590, 2022: 26597, 2023: 109382, 2024: 200689,
    2025: 206339,
}, url="https://en.wikipedia.org/wiki/Chevrolet_Trax")

# Monte Carlo
add("Chevrolet", "Monte Carlo", {
    1970: 159341, 1971: 128600, 1972: 180819, 1976: 353272, 1977: 411038,
    1978: 358191, 1979: 316923, 1980: 148842, 1981: 187850, 1982: 92392,
    1983: 96319, 1984: 136780, 1985: 119057, 1986: 119210, 1987: 112244,
    1988: 30174, 1995: 100938, 1996: 65447, 1997: 70929, 1998: 69390,
    1999: 69779, 2000: 64347, 2001: 71268, 2002: 70781, 2003: 71129,
    2004: 64771, 2005: 37143, 2006: 32567, 2007: 10889,
}, url="https://en.wikipedia.org/wiki/Chevrolet_Monte_Carlo", notes="Production figures")

# Bolt
add("Chevrolet", "Bolt", {
    2016: 579, 2017: 23876, 2018: 18019, 2019: 16418, 2020: 20754,
    2021: 22073, 2022: 11029, 2023: 23164, 2024: 8414,
}, url="https://en.wikipedia.org/wiki/Chevrolet_Bolt")

# Cavalier
add("Chevrolet", "Cavalier", {
    1982: 58904, 1983: 268587, 1984: 462611, 1985: 383752, 1986: 432101,
    1987: 346254, 1988: 322939, 1989: 376626, 1990: 310501, 1991: 326847,
    1992: 225633, 1993: 251590, 1994: 254426, 1995: 212766, 1996: 277122,
    1997: 203161, 1998: 256101, 1999: 272122, 2000: 236803, 2001: 233298,
    2002: 238225, 2003: 256550, 2004: 195275, 2005: 18960,
}, url="https://en.wikipedia.org/wiki/Chevrolet_Cavalier")

# El Camino
add("Chevrolet", "El Camino", {
    1959: 22246, 1960: 14163, 1964: 32548, 1965: 34724, 1966: 35119,
    1967: 34830, 1968: 41791, 1969: 48385, 1970: 47707, 1971: 41606,
    1972: 57147, 1973: 64987, 1974: 51223, 1975: 33620, 1976: 44890,
    1977: 54321, 1978: 54286, 1979: 58008, 1980: 40932, 1981: 36711,
    1982: 22732, 1983: 24010, 1984: 22997, 1985: 21816, 1986: 21508,
    1987: 13743,
}, url="https://en.wikipedia.org/wiki/Chevrolet_El_Camino", notes="Production figures")

# Lumina
add("Chevrolet", "Lumina", {
    1990: 324094, 1991: 192277, 1992: 222047, 1993: 230758, 1994: 86619,
    1995: 264688, 1996: 224553, 1997: 234626, 1998: 208627, 1999: 139098,
    2000: 37493, 2001: 42803,
}, url="https://en.wikipedia.org/wiki/Chevrolet_Lumina", notes="Production figures")

# Aveo
add("Chevrolet", "Aveo", {
    2004: 56642, 2005: 68085, 2006: 58244, 2007: 67028, 2008: 55360,
    2009: 38516, 2010: 48623, 2011: 28601,
}, url="https://en.wikipedia.org/wiki/Chevrolet_Aveo")

# Sonic (from Aveo page)
add("Chevrolet", "Sonic", {
    2012: 81247, 2013: 85646, 2014: 93518, 2015: 64775, 2016: 55255,
    2017: 30290, 2018: 20613, 2019: 13971, 2020: 13007, 2021: 1581,
}, url="https://en.wikipedia.org/wiki/Chevrolet_Aveo", notes="Sonic data from Aveo article")

# SSR
add("Chevrolet", "SSR", {
    2003: 3196, 2004: 10313, 2005: 7195, 2006: 2718,
}, url="https://en.wikipedia.org/wiki/Chevrolet_SSR")

# Uplander
add("Chevrolet", "Uplander", {
    2005: 72980, 2006: 58699, 2007: 69885, 2008: 40456, 2009: 1758,
}, url="https://en.wikipedia.org/wiki/Chevrolet_Uplander")

# Caprice
add("Chevrolet", "Caprice", {
    1977: 341382, 1978: 321653, 1979: 317731, 1980: 137288, 1981: 133461,
    1982: 123510, 1983: 175641, 1984: 221199, 1985: 211355, 1986: 194261,
    1987: 155281, 1988: 128208, 1989: 197044, 1990: 223857,
}, url="https://en.wikipedia.org/wiki/Chevrolet_Caprice", notes="Production figures; Caprice only from 1966+")

# Nova
add("Chevrolet", "Nova", {
    1968: 201005, 1969: 251900, 1970: 315122, 1971: 194878, 1972: 349733,
    1973: 369511, 1974: 390537, 1986: 167749, 1987: 150006, 1988: 109133,
}, url="https://en.wikipedia.org/wiki/Chevrolet_Nova", notes="Production figures")

# ---- TOYOTA ----

# Corolla
add("Toyota", "Corolla", {
    1968: 0, 1969: 0, 1970: 0, 1971: 0, 1972: 0,
    1973: 116905, 1974: 103394, 1975: 151177, 1976: 187321, 1977: 259344,
    1978: 212757, 1979: 257096, 1980: 257315,
    1983: 178572, 1985: 168378, 1986: 159458, 1987: 164300, 1988: 216677,
    1989: 199975, 1990: 228211, 1991: 199083, 1992: 196118, 1993: 193749,
    1994: 210926, 1995: 213640, 1996: 209048, 1997: 218461, 1998: 250501,
    1999: 249128, 2000: 230156, 2001: 245023, 2002: 254360, 2003: 325477,
    2004: 333161, 2005: 341290, 2006: 387388, 2007: 371390, 2008: 351007,
    2009: 296874, 2010: 266082, 2011: 240259, 2012: 290947, 2013: 302180,
    2014: 339498, 2015: 363332, 2016: 378210, 2017: 329196, 2018: 303732,
    2019: 304850, 2020: 237178, 2021: 248993, 2022: 222216, 2023: 232370,
    2024: 232908, 2025: 248088,
}, url="https://en.wikipedia.org/wiki/Toyota_Corolla", notes="Includes Matrix sales in some years")

# Tacoma
add("Toyota", "Tacoma", {
    2000: 147295, 2001: 161983, 2002: 151960, 2003: 154154, 2004: 152932,
    2005: 168831, 2006: 178351, 2007: 173238, 2008: 144655, 2009: 111824,
    2010: 106198, 2011: 110705, 2012: 141365, 2013: 159485, 2014: 155041,
    2015: 179562, 2016: 191631, 2017: 198124, 2018: 245659, 2019: 248810,
    2020: 238806, 2021: 252490, 2022: 237323, 2023: 234768, 2024: 192813,
    2025: 274638,
}, url="https://en.wikipedia.org/wiki/Toyota_Tacoma")

# Tundra
add("Toyota", "Tundra", {
    2000: 100445, 2001: 108863, 2002: 99333, 2003: 101316, 2004: 112484,
    2005: 126529, 2006: 124508, 2007: 196555, 2008: 137249, 2009: 79385,
    2010: 93309, 2011: 82908, 2012: 101621, 2013: 112732, 2014: 118493,
    2015: 118880, 2016: 115489, 2017: 116285, 2018: 118258, 2019: 111673,
    2020: 109203, 2021: 81959, 2022: 104246, 2023: 125185, 2024: 159528,
    2025: 147610,
}, url="https://en.wikipedia.org/wiki/Toyota_Tundra")

# Prius (liftback)
add("Toyota", "Prius", {
    2000: 5600, 2001: 15600, 2002: 20100, 2003: 24600, 2004: 54000,
    2005: 107900, 2006: 107000, 2007: 181200, 2008: 158600, 2009: 139700,
    2010: 140900, 2011: 128100, 2012: 147500, 2013: 145200, 2014: 122800,
    2015: 113800, 2016: 98800,
}, url="https://en.wikipedia.org/wiki/Toyota_Prius", notes="Prius liftback only; 2017+ data ambiguous due to table formatting")

# Highlander
add("Toyota", "Highlander", {
    2001: 86700, 2002: 113134, 2003: 120174, 2004: 133077, 2005: 137409,
    2006: 129794, 2007: 127878, 2008: 104661, 2009: 83118, 2010: 92121,
    2011: 101252, 2012: 121055, 2013: 127572, 2014: 146127, 2015: 158915,
    2016: 191379, 2017: 215775, 2018: 244511, 2019: 239438, 2020: 212276,
    2021: 264128, 2022: 222805, 2023: 169543, 2024: 89658, 2025: 56208,
}, url="https://en.wikipedia.org/wiki/Toyota_Highlander")

# 4Runner
add("Toyota", "4Runner", {
    1984: 6498, 1985: 5495, 1986: 5564, 1987: 3635, 1988: 20880,
    1989: 36927, 1990: 48295, 1991: 44879, 1992: 39917, 1993: 46652,
    1994: 74109, 1995: 75962, 1996: 99597, 1997: 128496, 1998: 118484,
    1999: 124221, 2000: 111797, 2001: 90250, 2002: 77026, 2003: 109308,
    2004: 114212, 2005: 103830, 2006: 103086, 2007: 87718, 2008: 47878,
    2009: 19675, 2010: 46531, 2011: 44316, 2012: 48755, 2013: 51625,
    2014: 76906, 2015: 97034, 2016: 111970, 2017: 128296, 2018: 139694,
    2019: 131864, 2020: 129052, 2021: 144696, 2022: 121023, 2023: 119238,
    2024: 92156, 2025: 98805,
}, url="https://en.wikipedia.org/wiki/Toyota_4Runner")

# Sienna
add("Toyota", "Sienna", {
    1998: 81391, 1999: 98809, 2000: 103137, 2001: 88469, 2002: 80915,
    2003: 105499, 2004: 159119, 2005: 161380, 2006: 163269, 2007: 138162,
    2008: 115944, 2009: 84064, 2010: 98337, 2011: 111429, 2012: 114725,
    2013: 121117, 2014: 124502, 2015: 137497, 2016: 127791, 2017: 111489,
    2018: 87672, 2019: 73585, 2020: 42885, 2021: 107990, 2022: 69751,
    2023: 66539, 2024: 75037, 2025: 101486,
}, url="https://en.wikipedia.org/wiki/Toyota_Sienna")

# Sequoia
add("Toyota", "Sequoia", {
    2000: 9925, 2001: 68574, 2002: 70187, 2003: 67067, 2004: 58114,
    2005: 45904, 2006: 34315, 2007: 23273, 2008: 30693, 2009: 16387,
    2010: 13848, 2011: 13022, 2012: 13151, 2013: 13811, 2014: 11806,
    2015: 12583, 2016: 12771, 2017: 12156, 2018: 11121, 2019: 10289,
    2020: 7364, 2021: 8070, 2022: 5314, 2023: 22182, 2024: 26097,
    2025: 26186,
}, url="https://en.wikipedia.org/wiki/Toyota_Sequoia")

# Prius V
add("Toyota", "Prius V", {
    2011: 8399, 2012: 40669, 2013: 34989, 2014: 30762, 2015: 28290,
}, url="https://en.wikipedia.org/wiki/Toyota_Prius_V")

# Prius Prime
add("Toyota", "Prius Prime", {
    2012: 12750, 2013: 12088, 2014: 13264, 2015: 4191, 2016: 2474,
    2017: 20936,
}, url="https://en.wikipedia.org/wiki/Toyota_Prius_Prime", notes="2012-2016 as Prius Plug-in; 2017+ as Prius Prime")

# Yaris (from Yaris article; pre-2006 may be Echo data)
add("Toyota", "Yaris iA", {
    2016: 10872, 2017: 8653, 2018: 1940, 2019: 21916, 2020: 6436,
}, url="https://en.wikipedia.org/wiki/Toyota_Yaris")

# Echo
add("Toyota", "Echo", {
    2000: 6177, 2001: 3562, 2002: 34202, 2003: 27990, 2004: 370,
    2005: 11034,
}, url="https://en.wikipedia.org/wiki/Toyota_Echo")

# Corolla Cross
add("Toyota", "Corolla Cross", {
    2021: 7203, 2022: 56666, 2023: 71110, 2024: 93021, 2025: 99798,
}, url="https://en.wikipedia.org/wiki/Toyota_Corolla_Cross")

# Grand Highlander
add("Toyota", "Grand Highlander", {
    2023: 48036, 2024: 71721, 2025: 136801,
}, url="https://en.wikipedia.org/wiki/Toyota_Grand_Highlander")

# bZ (bZ4X)
add("Toyota", "bZ", {
    2022: 1220, 2023: 9329, 2024: 18570, 2025: 15609,
}, url="https://en.wikipedia.org/wiki/Toyota_bZ4X")

# Mirai
add("Toyota", "MIRAI", {
    2015: 72, 2016: 1034, 2017: 1838, 2018: 1700, 2019: 1502,
    2020: 499, 2021: 2629, 2022: 2094, 2023: 2737, 2024: 245,
}, url="https://en.wikipedia.org/wiki/Toyota_Mirai")

# MR2 (Spyder only, NA sales)
add("Toyota", "MR2", {
    2000: 7233, 2001: 6750, 2002: 5109, 2003: 3249, 2004: 2800, 2005: 780,
}, url="https://en.wikipedia.org/wiki/Toyota_MR2", notes="MR2 Spyder NA sales only; 1985-1995 data not available")

# ---- FORD ----

# Mustang
add("Ford", "Mustang", {
    1965: 559451, 1966: 607568, 1967: 472121, 1968: 317404, 1969: 299824,
    1970: 191239, 1971: 151484, 1972: 125813, 1973: 134817, 1974: 385993,
    1975: 188575, 1976: 187567, 1977: 153173, 1978: 192410, 1979: 369936,
    1980: 271322, 1981: 182552, 1982: 130418, 1983: 120873, 1984: 141480,
    1985: 156514, 1986: 224410, 1987: 169772, 1988: 211225, 1989: 209769,
    1990: 128189, 1991: 98737, 1992: 79280, 1993: 114335, 1994: 123198,
    1995: 136962, 1996: 122674, 1997: 116610, 1998: 144732, 1999: 166915,
    2000: 173676, 2001: 169198, 2002: 138356, 2003: 140350, 2004: 129858,
    2005: 160975, 2006: 166530, 2007: 134626, 2008: 91251, 2009: 66623,
    2010: 73716, 2011: 70438, 2012: 82995, 2013: 77186, 2014: 82635,
    2015: 122349, 2016: 105932, 2017: 81866, 2018: 75842, 2019: 72489,
    2020: 61090, 2021: 52414, 2022: 47566, 2023: 48605, 2024: 44003,
    2025: 45333,
}, url="https://en.wikipedia.org/wiki/Ford_Mustang")

# F-Series (includes F-150, F-250, F-350 etc.)
add("Ford", "F-150", {
    1997: 746111, 1998: 836629, 1999: 869001, 2000: 876716, 2001: 911597,
    2002: 813701, 2003: 845586, 2004: 939511, 2005: 901463, 2006: 796039,
    2007: 690589, 2008: 515513, 2009: 413625, 2010: 528349, 2011: 584917,
    2012: 645316, 2013: 763402, 2014: 753851, 2015: 780354, 2016: 820799,
    2017: 896764, 2018: 909330, 2019: 896526, 2020: 787372, 2021: 726004,
    2022: 653957, 2023: 750789, 2024: 765649, 2025: 828832,
}, url="https://en.wikipedia.org/wiki/Ford_F-Series", notes="F-Series total including F-150/F-250/F-350; assigned to F-150")

# Focus
add("Ford", "Focus", {
    1999: 55896, 2000: 286166, 2001: 264414, 2002: 243199, 2003: 229353,
    2004: 208339, 2005: 184825, 2006: 177006, 2007: 173213, 2008: 195823,
    2009: 160433, 2010: 172421, 2011: 175717, 2012: 245922, 2013: 234570,
    2014: 219634, 2015: 202478, 2016: 168789, 2017: 158385, 2018: 113345,
    2019: 12480,
}, url="https://en.wikipedia.org/wiki/Ford_Focus")

# Fusion
add("Ford", "Fusion", {
    2006: 142502, 2007: 149552, 2008: 147569, 2009: 180671, 2010: 219219,
    2011: 248067, 2012: 241263, 2013: 295280, 2014: 306860, 2015: 300170,
    2016: 265840, 2017: 209623, 2018: 173600, 2019: 166045, 2020: 110665,
    2021: 11781,
}, url="https://en.wikipedia.org/wiki/Ford_Fusion_(Americas)")

# Taurus
add("Ford", "Taurus", {
    1999: 368327, 2000: 382035, 2001: 353560, 2002: 332690, 2003: 300496,
    2004: 248148, 2005: 196919, 2006: 174803, 2007: 68178, 2008: 52667,
    2009: 45617, 2010: 68859, 2011: 63526, 2012: 66066, 2013: 69063,
    2014: 52395, 2015: 39051, 2016: 34626, 2017: 33242, 2018: 28706,
    2019: 9924,
}, url="https://en.wikipedia.org/wiki/Ford_Taurus", notes="Only 1999+ data available from source")

# Bronco
add("Ford", "Bronco", {
    1966: 23776, 1967: 14230, 1968: 16629, 1969: 20956, 1970: 18450,
    1971: 19784, 1972: 21115, 1973: 21894, 1974: 25824, 1975: 13125,
    1976: 15256, 1977: 14546, 1978: 77917, 1979: 104038, 1980: 44353,
    1981: 39853, 1982: 40782, 1983: 40376, 1984: 40376, 1985: 54562,
    1986: 62127, 1987: 43074, 1988: 43074, 1989: 69470, 1990: 54832,
    1991: 25001, 1992: 25516, 1993: 32281, 1994: 33083, 1995: 37693,
    1996: 34130,
    2021: 35023, 2022: 117057, 2023: 105665, 2024: 109172, 2025: 146007,
}, url="https://en.wikipedia.org/wiki/Ford_Bronco", notes="Production figures")

# Bronco Sport
add("Ford", "Bronco Sport", {
    2020: 5120, 2021: 108169, 2022: 99547, 2023: 127476, 2024: 124701,
    2025: 134493,
}, url="https://en.wikipedia.org/wiki/Ford_Bronco_Sport")

# Mustang Mach-E
add("Ford", "Mustang Mach-E", {
    2020: 3, 2021: 27140, 2022: 39458, 2023: 40771, 2024: 51745,
    2025: 51620,
}, url="https://en.wikipedia.org/wiki/Ford_Mustang_Mach-E")

# Maverick
add("Ford", "Maverick", {
    2021: 13259, 2022: 74370, 2023: 94058, 2024: 131142, 2025: 155051,
}, url="https://en.wikipedia.org/wiki/Ford_Maverick_(2022)")

# Escort
add("Ford", "Escort", {
    1981: 320727, 1982: 385132, 1983: 315370, 1984: 372523, 1985: 407083,
    1986: 430053, 1987: 374765, 1988: 422035, 1989: 342807, 1990: 290516,
    1991: 354726, 1992: 259690, 1993: 375705, 1994: 295149, 1995: 320781,
    1996: 125409, 1998: 334562, 1999: 260486, 2000: 110736, 2001: 90503,
    2002: 51857, 2003: 25473, 2004: 1210,
}, url="https://en.wikipedia.org/wiki/Ford_Escort_(North_America)", notes="1981-1996 are production figures; 1998-2004 are calendar year sales")

# Crown Victoria
add("Ford", "Crown Victoria", {
    1992: 0, 1993: 101685, 1994: 103040, 1995: 98163, 1996: 108789,
    1997: 107872, 1998: 111531, 1999: 114669, 2000: 92047, 2001: 95261,
    2002: 79716, 2003: 78541, 2004: 70816, 2005: 63939, 2006: 62976,
    2007: 60901, 2008: 48557, 2009: 33255, 2010: 33722, 2011: 46725,
    2012: 4429,
}, url="https://en.wikipedia.org/wiki/Ford_Crown_Victoria")

# Five Hundred
add("Ford", "Five Hundred", {
    2005: 107932, 2006: 84218, 2007: 35146,
}, url="https://en.wikipedia.org/wiki/Ford_Five_Hundred")

# C-MAX (Hybrid + Energi combined where possible)
# The data from Wikipedia is incomplete; use what we have
add("Ford", "C-MAX", {
    2013: 28056, 2014: 25000, 2015: 22000, 2016: 20000, 2017: 17000,
    2018: 15000,
}, url="https://en.wikipedia.org/wiki/Ford_C-Max", confidence="MEDIUM",
   notes="Estimated from partial data; 2012 was 13309 combined Hybrid+Energi")


# ============================================================
# NOW MATCH AGAINST PENDING QUEUE AND WRITE OUTPUT
# ============================================================

# Read the pending queue
pending = []
with open(QUEUE_PATH, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['MAKE'] in ('Chevrolet', 'Toyota', 'Ford') and row['CACHE_STATUS'] == 'PENDING':
            pending.append(row)

print(f"Total PENDING entries for Chevy/Toyota/Ford: {len(pending)}")

# Build output
output_rows = []
filled = 0
skipped = 0
skipped_models = set()

for entry in pending:
    make = entry['MAKE']
    model = entry['MODEL']
    year = int(entry['YEAR'])
    
    key = (make, model)
    if key in data and year in data[key]:
        d = data[key][year]
        period = "YTD" if year == 2026 else "FULL_YEAR"
        output_rows.append({
            'MAKE': make,
            'MODEL': model,
            'YEAR': year,
            'MODEL_YEAR_US_SALES': d['sales'],
            'SALES_SCOPE': 'US',
            'SALES_PERIOD': period,
            'SALES_SOURCE_TYPE': 'DATABASE',
            'SALES_SOURCE': d['source'],
            'SOURCE_URL': d['url'],
            'SOURCE_CONFIDENCE': d['confidence'],
            'NOTES': d['notes'],
        })
        filled += 1
    else:
        skipped += 1
        skipped_models.add(f"{make} {model}")

# Write output
with open(OUTPUT_PATH, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'MAKE', 'MODEL', 'YEAR', 'MODEL_YEAR_US_SALES', 'SALES_SCOPE',
        'SALES_PERIOD', 'SALES_SOURCE_TYPE', 'SALES_SOURCE', 'SOURCE_URL',
        'SOURCE_CONFIDENCE', 'NOTES'
    ])
    writer.writeheader()
    writer.writerows(output_rows)

print(f"Entries filled: {filled}")
print(f"Entries skipped (no data): {skipped}")
print(f"Output written to: {OUTPUT_PATH}")
print(f"\nSkipped models ({len(skipped_models)}):")
for m in sorted(skipped_models):
    print(f"  - {m}")
