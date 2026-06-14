import sqlite3
import hashlib
import os

DB_PATH = "cybertomb.db"

DEMO_TOMBS = [
  { "id": "PH-SAG-001", "name": "Echo Valley Cliffside", "city": "Sagada, Philippines", "coordinates": [120.9022, 17.0894], "type": "Hanging Coffins" },
  { "id": "ID-TOR-002", "name": "Lemo Burial Cliff", "city": "Tana Toraja, Indonesia", "coordinates": [119.8974, -2.9775], "type": "Ma'nene & Funeral Rites" },
  { "id": "MG-AMB-003", "name": "Ambohimanga Ancestral Vault", "city": "Antananarivo, Madagascar", "coordinates": [47.5815, -18.7562], "type": "Famadihana" },
  { "id": "GH-ACC-004", "name": "Kane Kwei Carpentry Workshop", "city": "Accra, Ghana", "coordinates": [-0.1869, 5.6037], "type": "Fantasy Coffins" },
  { "id": "IN-VAR-005", "name": "Manikarnika Ghat Cremation", "city": "Varanasi, India", "coordinates": [82.9739, 25.3176], "type": "Ganges Cremation" },
  { "id": "US-FL-006", "name": "Celestis Orbital Gateway", "city": "Cape Canaveral, USA", "coordinates": [-80.6076, 28.3922], "type": "Space Burial" },
  { "id": "MX-OAX-007", "name": "Oaxaca Memorial Plaza", "city": "Oaxaca, Mexico", "coordinates": [-96.7233, 17.0732], "type": "Day of the Dead" },
  { "id": "KR-SEO-008", "name": "Bongeunsa Sacred Beads", "city": "Seoul, South Korea", "coordinates": [127.0577, 37.5134], "type": "Death Beads" },
  { "id": "IT-PAL-009", "name": "Capuchin Crypt Gallery", "city": "Palermo, Italy", "coordinates": [13.3614, 38.1157], "type": "Capuchin Catacombs Preservation" },
  { "id": "SE-GOT-010", "name": "Promessa Research Lab", "city": "Gothenburg, Sweden", "coordinates": [11.9746, 57.7089], "type": "Promession (Cryomation)" },
  { "id": "IT-MIL-011", "name": "Capsula Mundi Grove", "city": "Milan, Italy", "coordinates": [9.1900, 45.4642], "type": "Capsula Mundi (Green Burial)" },
  { "id": "JP-TOK-012", "name": "Ruriden High-Tech Vault", "city": "Tokyo, Japan", "coordinates": [139.6917, 35.6895], "type": "High-Tech Columbarium (Ruriden)" },
  { "id": "IS-REY-013", "name": "Faxaflói Marine Scatter", "city": "Reykjavik, Iceland", "coordinates": [-21.9426, 64.1466], "type": "Water Burial" },
  { "id": "US-KEY-014", "name": "Neptune Memorial Reef", "city": "Key Largo, USA", "coordinates": [-80.4473, 25.0865], "type": "Eternal Reefs (Marine Burial)" },
  { "id": "EG-GIZ-015", "name": "Great Pyramid Necropolis", "city": "Giza, Egypt", "coordinates": [31.1342, 29.9792], "type": "Mummification & Pyramids" },
  { "id": "NP-EVE-016", "name": "Khumbu Sky Burial Site", "city": "Everest Region, Nepal", "coordinates": [86.9226, 27.9881], "type": "Open-air Burial" },
  { "id": "CA-BC-017", "name": "Haida Totem Forest", "city": "Haida Gwaii, Canada", "coordinates": [-132.1221, 53.2500], "type": "Indigenous Platform Burial" },
  { "id": "CN-BO-018", "name": "Bo People Hanging Site", "city": "Gongxian, China", "coordinates": [104.7200, 28.1400], "type": "Boat-shaped Hanging Coffins" },
  { "id": "US-LA-019", "name": "Alkaline Hydrolysis Center", "city": "Los Angeles, USA", "coordinates": [-118.2437, 34.0522], "type": "Resomation (Alkaline Hydrolysis)" },
  { "id": "CH-ZUR-020", "name": "Algordanza Diamond Studio", "city": "Zurich, Switzerland", "coordinates": [8.5417, 47.3769], "type": "Memorial Diamonds" },
    # === Asia (021 - 060) ===
    { "id": "CN-YUN-021", "name": "Erhai Lake Marine Scatter", "city": "Dali, China", "coordinates": [100.2243, 25.6065], "type": "Water Burial" },
    { "id": "CN-XZ-022", "name": "Drigung Til Celestial Terrace", "city": "Lhasa, China", "coordinates": [91.1172, 29.6524], "type": "Sky Burial" },
    { "id": "CN-NX-023", "name": "Ningxia Desert Eco-Shrine", "city": "Yinchuan, China", "coordinates": [106.2309, 38.4872], "type": "Desert Green Burial" },
    { "id": "CN-GD-024", "name": "Pearl River Estuary Release", "city": "Guangzhou, China", "coordinates": [113.6066, 22.7512], "type": "Sea Scattering" },
    { "id": "CN-SC-025", "name": "Jiuzhaigou Forest Eternal Plot", "city": "Aba, China", "coordinates": [103.9186, 33.2600], "type": "Tree Burial" },
    { "id": "JP-KOT-026", "name": "Tounoin Jumokuso Woods", "city": "Chiba, Japan", "coordinates": [140.1234, 35.6089], "type": "Tree Burial" },
    { "id": "JP-OSA-027", "name": "Blue Ocean Osaka Bay", "city": "Osaka, Japan", "coordinates": [135.4223, 34.6537], "type": "Sea Scattering" },
    { "id": "JP-KYT-028", "name": "Ryoan-ji Ash Sanctuary", "city": "Kyoto, Japan", "coordinates": [135.7182, 35.0344], "type": "Zen Temple Ash Inurnment" },
    { "id": "JP-YOK-029", "name": "Yokohama Automated Vault", "city": "Yokohama, Japan", "coordinates": [139.6380, 35.4437], "type": "High-Tech Columbarium" },
    { "id": "KR-BUS-030", "name": "Busan Marine Memorial Wave", "city": "Busan, South Korea", "coordinates": [129.0756, 35.1796], "type": "Water Burial" },
    { "id": "KR-JEJ-031", "name": "Jeju Volcanic Ash Garden", "city": "Jeju, South Korea", "coordinates": [126.5312, 33.4996], "type": "Natural Green Burial" },
    { "id": "TW-TPE-032", "name": "Yangmingshan Flower Scattering Area", "city": "Taipei, Taiwan", "coordinates": [121.5454, 25.1530], "type": "Natural Green Burial" },
    { "id": "TW-KHH-033", "name": "Kaohsiung Harbor Farewell Site", "city": "Kaohsiung, Taiwan", "coordinates": [120.2811, 22.6275], "type": "Sea Scattering" },
    { "id": "HK-SKO-034", "name": "Sai Kung Eternal Sea Zone", "city": "Hong Kong", "coordinates": [114.2704, 22.3811], "type": "Sea Scattering" },
    { "id": "HK-TMW-035", "name": "Tuen Mun Eco-Columbarium", "city": "Hong Kong", "coordinates": [113.9764, 22.3916], "type": "High-Tech Columbarium" },
    { "id": "MO-COL-036", "name": "Coloane Ash Scattering Garden", "city": "Macau", "coordinates": [113.5572, 22.1244], "type": "Natural Green Burial" },
    { "id": "SG-CHO-037", "name": "Garden of Peace Choa Chu Kang", "city": "Singapore", "coordinates": [103.6925, 1.3783], "type": "Inland Ash Scattering" },
    { "id": "MY-PEN-038", "name": "Penang Strait Marine Scatter", "city": "Penang, Malaysia", "coordinates": [100.3422, 5.4144], "type": "Water Burial" },
    { "id": "TH-PHE-039", "name": "Chao Phraya River Mouth Plot", "city": "Samut Prakan, Thailand", "coordinates": [100.5975, 13.5991], "type": "Water Burial" },
    { "id": "PH-MNL-040", "name": "Manila South Eco-Vault", "city": "Manila, Philippines", "coordinates": [121.0359, 14.5614], "type": "High-Tech Columbarium" },
    { "id": "ID-BAL-041", "name": "Sanur Beach Ngaben Site", "city": "Bali, Indonesia", "coordinates": [115.2639, -8.6751], "type": "Water Burial" },
    { "id": "VN-DAN-042", "name": "Da Nang Sea Memorial", "city": "Da Nang, Vietnam", "coordinates": [108.2208, 16.0471], "type": "Sea Scattering" },
    { "id": "IN-GOA-043", "name": "Arabian Sea Scatter Point", "city": "Goa, India", "coordinates": [73.8124, 15.4909], "type": "Water Burial" },
    { "id": "IN-RSH-044", "name": "Rishikesh Ganges Gateway", "city": "Rishikesh, India", "coordinates": [78.2676, 30.0869], "type": "Ganges Cremation" },
    { "id": "LK-COL-045", "name": "Colombo Marine Release Bed", "city": "Colombo, Sri Lanka", "coordinates": [79.8612, 6.9271], "type": "Water Burial" },
    { "id": "NP-KTM-046", "name": "Bagmati River Ghats", "city": "Kathmandu, Nepal", "coordinates": [85.3486, 27.7100], "type": "Open-air Burial" },
    { "id": "PK-KRA-047", "name": "Clifton Beach Scattering Zone", "city": "Karachi, Pakistan", "coordinates": [67.0311, 24.8138], "type": "Water Burial" },
    { "id": "MN-ULA-048", "name": "Bogd Khan Sky Platform", "city": "Ulaanbaatar, Mongolia", "coordinates": [106.9175, 47.8114], "type": "Sky Burial" },
    { "id": "UZ-SAM-049", "name": "Samarkand Desert Edge", "city": "Samarkand, Uzbekistan", "coordinates": [66.9808, 39.6642], "type": "Desert Green Burial" },
    { "id": "TR-IST-050", "name": "Bosphorus Marine Memorial", "city": "Istanbul, Turkey", "coordinates": [29.0081, 41.0422], "type": "Water Burial" },
    { "id": "AE-DXB-051", "name": "Jumeirah Deep Sea Line", "city": "Dubai, UAE", "coordinates": [55.1925, 25.2281], "type": "Sea Scattering" },
    { "id": "SA-JED-052", "name": "Red Sea Deep Scatter", "city": "Jeddah, Saudi Arabia", "coordinates": [39.1022, 21.5433], "type": "Sea Scattering" },
    { "id": "IL-TLI-053", "name": "Tel Aviv Mediterranean Waves", "city": "Tel Aviv, Israel", "coordinates": [34.7611, 32.0697], "type": "Water Burial" },
    { "id": "LB-BEY-054", "name": "Beirut Marine Shelf", "city": "Beirut, Lebanon", "coordinates": [35.4692, 33.8933], "type": "Water Burial" },
    { "id": "GE-BAT-055", "name": "Black Sea Horizon Point", "city": "Batumi, Georgia", "coordinates": [41.6167, 41.6333], "type": "Water Burial" },
    { "id": "AM-YER-056", "name": "Mount Aragats Foothill", "city": "Yerevan, Armenia", "coordinates": [44.5136, 40.1792], "type": "Open-air Burial" },
    { "id": "AZ-BAK-057", "name": "Caspian Sea Shelf Site", "city": "Baku, Azerbaijan", "coordinates": [49.8671, 40.4093], "type": "Water Burial" },
    { "id": "KZ-ALA-058", "name": "Tian Shan Mountain Crest", "city": "Almaty, Kazakhstan", "coordinates": [76.9286, 43.2389], "type": "Open-air Burial" },
    { "id": "KG-B包装-059", "name": "Issyk-Kul Deep Water Plot", "city": "Bishkek, Kyrgyzstan", "coordinates": [77.4000, 42.5000], "type": "Water Burial" },
    { "id": "TJ-DUS-060", "name": "Pamir Plateau Sky Plot", "city": "Dushanbe, Tajikistan", "coordinates": [71.5000, 38.5000], "type": "Sky Burial" },

    # === Europe (061 - 110) ===
    { "id": "GB-LON-061", "name": "Thames Estuary Scatter vessels", "city": "London, UK", "coordinates": [0.5012, 51.5074], "type": "Water Burial" },
    { "id": "GB-EDI-062", "name": "Firth of Forth Marine Section", "city": "Edinburgh, UK", "coordinates": [-3.1883, 55.9533], "type": "Sea Scattering" },
    { "id": "GB-MAN-063", "name": "Pennine Hills Green Wood", "city": "Manchester, UK", "coordinates": [-2.2426, 53.4808], "type": "Capsula Mundi (Green Burial)" },
    { "id": "IE-DUB-064", "name": "Dublin Bay Atlantic Release", "city": "Dublin, Ireland", "coordinates": [-6.1400, 53.3498], "type": "Water Burial" },
    { "id": "FR-PAR-065", "name": "Seine River Memorial Zone", "city": "Paris, France", "coordinates": [2.3522, 48.8566], "type": "Water Burial" },
    { "id": "FR-MAR-066", "name": "Mediterranean Blue Shelf", "city": "Marseille, France", "coordinates": [5.3698, 43.2965], "type": "Sea Scattering" },
    { "id": "DE-HAM-067", "name": "Elbe River Estuary Plot", "city": "Hamburg, Germany", "coordinates": [9.9937, 53.5511], "type": "Water Burial" },
    { "id": "DE-MUN-068", "name": "Isar River Alpine Flow", "city": "Munich, Germany", "coordinates": [11.5820, 48.1351], "type": "Water Burial" },
    { "id": "DE-BER-069", "name": "Brandenburg Woodland Biosphere", "city": "Berlin, Germany", "coordinates": [13.4050, 52.5200], "type": "Capsula Mundi (Green Burial)" },
    { "id": "NL-AMS-070", "name": "North Sea Dutch Coast Line", "city": "Amsterdam, Netherlands", "coordinates": [4.9041, 52.3676], "type": "Sea Scattering" },
    { "id": "BE-BRU-071", "name": "Flemish Green Forest Plot", "city": "Brussels, Belgium", "coordinates": [4.3517, 50.8503], "type": "Promession (Cryomation)" },
    { "id": "CH-GEN-072", "name": "Lake Geneva Deep Deposit", "city": "Geneva, Switzerland", "coordinates": [6.1431, 46.2044], "type": "Water Burial" },
    { "id": "CH-URI-073", "name": "Gotthard Pass Alpine Wind", "city": "Uri, Switzerland", "coordinates": [8.5667, 46.6833], "type": "Open-air Burial" },
    { "id": "AT-VIE-074", "name": "Danube River Blue Stream", "city": "Vienna, Austria", "coordinates": [16.3738, 48.2082], "type": "Water Burial" },
    { "id": "IT-VEN-075", "name": "Venetian Lagoon Ocean Exit", "city": "Venice, Italy", "coordinates": [12.3155, 45.4408], "type": "Water Burial" },
    { "id": "IT-NAP-076", "name": "Gulf of Naples Deep Marine", "city": "Naples, Italy", "coordinates": [14.2681, 40.8518], "type": "Eternal Reefs (Marine Burial)" },
    { "id": "ES-BAR-077", "name": "Catalonia Reef Alliance", "city": "Barcelona, Spain", "coordinates": [2.1734, 41.3851], "type": "Eternal Reefs (Marine Burial)" },
    { "id": "ES-MAD-078", "name": "Guadarrama Biosphere Center", "city": "Madrid, Spain", "coordinates": [-3.7038, 40.4167], "type": "Capsula Mundi (Green Burial)" },
    { "id": "PT-LIS-079", "name": "Tagus River Atlantic Mouth", "city": "Lisbon, Portugal", "coordinates": [-9.1393, 38.7223], "type": "Water Burial" },
    { "id": "DK-CPH-080", "name": "Oresund Strait Marine Drift", "city": "Copenhagen, Denmark", "coordinates": [12.5683, 55.6761], "type": "Sea Scattering" },
    { "id": "SE-STO-081", "name": "Stockholm Archipelago Scatter", "city": "Stockholm, Sweden", "coordinates": [18.0686, 59.3293], "type": "Sea Scattering" },
    { "id": "NO-BER-082", "name": "Hardangerfjord Marine Shelf", "city": "Bergen, Norway", "coordinates": [5.3221, 60.3913], "type": "Water Burial" },
    { "id": "FI-HEL-083", "name": "Gulf of Finland Baltic Bed", "city": "Helsinki, Finland", "coordinates": [24.9384, 60.1699], "type": "Sea Scattering" },
    { "id": "IS-AKU-084", "name": "Eyjafjörður Arctic Scatter", "city": "Akureyori, Iceland", "coordinates": [-18.0878, 65.6835], "type": "Water Burial" },
    { "id": "PL-GDN-085", "name": "Baltic Deep Gdansk Trench", "city": "Gdansk, Poland", "coordinates": [18.6466, 54.3520], "type": "Sea Scattering" },
    { "id": "CZ-PRA-086", "name": "Vltava River Forest Plot", "city": "Prague, Czechia", "coordinates": [14.4378, 50.0755], "type": "Capsula Mundi (Green Burial)" },
    { "id": "HU-BUD-087", "name": "Budapest Danube Flow", "city": "Budapest, Hungary", "coordinates": [19.0402, 47.4979], "type": "Water Burial" },
    { "id": "GR-SAN-088", "name": "Santorini Caldera Drop", "city": "Santorini, Greece", "coordinates": [25.4315, 36.4166], "type": "Water Burial" },
    { "id": "RO-CON-089", "name": "Constanta Black Sea Apex", "city": "Constanta, Romania", "coordinates": [28.6583, 44.1792], "type": "Sea Scattering" },
    { "id": "BG-VAR-090", "name": "Varna Marine Release Bay", "city": "Varna, Bulgaria", "coordinates": [27.9147, 43.2141], "type": "Water Burial" },
    { "id": "HR-SPL-091", "name": "Adriatic Blue Reef Point", "city": "Split, Croatia", "coordinates": [16.4402, 43.5081], "type": "Eternal Reefs (Marine Burial)" },
    { "id": "SI-LJU-092", "name": "Alps Triglav Crest Site", "city": "Ljubljana, Slovenia", "coordinates": [14.5058, 46.0569], "type": "Open-air Burial" },
    { "id": "EE-TAL-093", "name": "Tallinn Bay Eco Scattering", "city": "Tallinn, Estonia", "coordinates": [24.7536, 59.4370], "type": "Sea Scattering" },
    { "id": "LV-RIG-094", "name": "Gulf of Riga Baltic Line", "city": "Riga, Latvia", "coordinates": [24.1052, 56.9496], "type": "Water Burial" },
    { "id": "LT-KLA-095", "name": "Curonian Spit Marine Loop", "city": "Klaipeda, Lithuania", "coordinates": [21.1443, 55.7033], "type": "Sea Scattering" },
    { "id": "RU-SPB-096", "name": "Gulf of Finland Neva Mouth", "city": "St. Petersburg, Russia", "coordinates": [30.3351, 59.9343], "type": "Water Burial" },
    { "id": "RU-VLA-097", "name": "Sea of Japan Golden Horn", "city": "Vladivostok, Russia", "coordinates": [131.8869, 43.1198], "type": "Sea Scattering" },
    { "id": "RU-SOF-098", "name": "Baikal Deep Water Sinking", "city": "Irkutsk, Russia", "coordinates": [104.2806, 52.2870], "type": "Water Burial" },
    { "id": "UA-ODE-099", "name": "Odesa Black Sea Terminal", "city": "Odesa, Ukraine", "coordinates": [30.7233, 46.4825], "type": "Water Burial" },
    { "id": "MT-VAL-100", "name": "Malta Mediterranean Shelf", "city": "Valletta, Malta", "coordinates": [14.5146, 35.8989], "type": "Eternal Reefs (Marine Burial)" },
    { "id": "CY-LIM-101", "name": "Limassol Deep Marine Reef", "city": "Limassol, Cyprus", "coordinates": [33.0413, 34.6750], "type": "Eternal Reefs (Marine Burial)" },
    { "id": "LU-LUX-102", "name": "Ardennes Border Eco-Park", "city": "Luxembourg", "coordinates": [6.1319, 49.6116], "type": "Capsula Mundi (Green Burial)" },
    { "id": "MC-MON-103", "name": "Monaco Deep Blue Drop", "city": "Monaco", "coordinates": [7.4246, 43.7384], "type": "Sea Scattering" },
    { "id": "SM-SAN-104", "name": "Monte Titano Cloud Crest", "city": "San Marino", "coordinates": [12.4578, 43.9424], "type": "Open-air Burial" },
    { "id": "LI-VAD-105", "name": "Rhine Valley Soil Link", "city": "Vaduz, Liechtenstein", "coordinates": [9.5209, 47.1410], "type": "Capsula Mundi (Green Burial)" },
    { "id": "AD-AND-106", "name": "Pyrenees Peak Scattering Node", "city": "Andorra la Vella", "coordinates": [1.5218, 42.5063], "type": "Open-air Burial" },
    { "id": "AL-DUR-107", "name": "Adriatic Durres Wave Shelf", "city": "Durres, Albania", "coordinates": [19.4489, 41.3217], "type": "Water Burial" },
    { "id": "BA-SAR-108", "name": "Dinaric Alps Green Forest", "city": "Sarajevo, Bosnia", "coordinates": [18.4131, 43.8563], "type": "Capsula Mundi (Green Burial)" },
    { "id": "ME-KOT-109", "name": "Bay of Kotor Deep Scatter", "city": "Kotor, Montenegro", "coordinates": [18.7712, 42.4247], "type": "Water Burial" },
    { "id": "MK-OHR-110", "name": "Lake Ohrid Ancient Shelf", "city": "Ohrid, North Macedonia", "coordinates": [20.8016, 41.1172], "type": "Water Burial" },

    # === Americas (111 - 150) ===
    { "id": "US-CA-111", "name": "San Francisco Bio-Preserve", "city": "San Francisco, USA", "coordinates": [-122.4194, 37.7749], "type": "Resomation (Alkaline Hydrolysis)" },
    { "id": "US-NY-112", "name": "Long Island Sound Scatter", "city": "New York, USA", "coordinates": [-73.1350, 41.0333], "type": "Sea Scattering" },
    { "id": "US-WA-113", "name": "Seattle Cascade Terramation Center", "city": "Seattle, USA", "coordinates": [-122.3321, 47.6062], "type": "Capsula Mundi (Green Burial)" },
    { "id": "US-TX-114", "name": "Austin Hill Country Green Plot", "city": "Austin, USA", "coordinates": [-97.7431, 30.2672], "type": "Capsula Mundi (Green Burial)" },
    { "id": "US-HI-115", "name": "Oahu Pacific Marine Reef", "city": "Honolulu, USA", "coordinates": [-157.8583, 21.3069], "type": "Eternal Reefs (Marine Burial)" },
    { "id": "US-AK-116", "name": "Juneau Glacier Ice Freeze", "city": "Juneau, USA", "coordinates": [-134.4197, 58.3019], "type": "Promession (Cryomation)" },
    { "id": "US-ME-117", "name": "Atlantic Deep Cold Inurnment", "city": "Portland, USA", "coordinates": [-70.2568, 43.6591], "type": "Sea Scattering" },
    { "id": "US-NC-118", "name": "Outer Banks Marine Bed", "city": "Raleigh, USA", "coordinates": [-75.6700, 35.9000], "type": "Eternal Reefs (Marine Burial)" },
    { "id": "US-CO-119", "name": "Rocky Mountain Wind Release", "city": "Denver, USA", "coordinates": [-104.9903, 39.7392], "type": "Open-air Burial" },
    { "id": "US-AZ-120", "name": "Sonoran Desert Sand Matrix", "city": "Phoenix, USA", "coordinates": [-112.0740, 33.4484], "type": "Desert Green Burial" },
    { "id": "CA-VAN-121", "name": "Pacific Coast Fjord Scatter", "city": "Vancouver, Canada", "coordinates": [-123.1207, 49.2827], "type": "Sea Scattering" },
    { "id": "CA-TOR-122", "name": "Lake Ontario Cryo-Center", "city": "Toronto, Canada", "coordinates": [-79.3832, 43.6532], "type": "Promession (Cryomation)" },
    { "id": "CA-NS-123", "name": "Halifax Atlantic Memorial", "city": "Halifax, Canada", "coordinates": [-63.5752, 44.6488], "type": "Water Burial" },
    { "id": "MX-CUN-124", "name": "Cancun Underwater Coral Reef", "city": "Cancun, Mexico", "coordinates": [-86.8515, 21.1619], "type": "Eternal Reefs (Marine Burial)" },
    { "id": "MX-VER-125", "name": "Gulf of Mexico Blue Wave", "city": "Veracruz, Mexico", "coordinates": [-96.1342, 19.1738], "type": "Sea Scattering" },
    { "id": "CU-HAV-126", "name": "Havana Caribbean Flow", "city": "Havana, Cuba", "coordinates": [-82.3666, 23.1136], "type": "Water Burial" },
    { "id": "JM-KIN-127", "name": "Kingston Deep Trench Scatter", "city": "Kingston, Jamaica", "coordinates": [-76.7936, 17.9714], "type": "Water Burial" },
    { "id": "PR-SAN-128", "name": "San Juan Oceanic Edge", "city": "San Juan, Puerto Rico", "coordinates": [-66.1057, 18.4655], "type": "Eternal Reefs (Marine Burial)" },
    { "id": "CR-S包装-129", "name": "Costa Rica Eco-Forest Lab", "city": "San Jose, Costa Rica", "coordinates": [-84.0907, 9.9281], "type": "Capsula Mundi (Green Burial)" },
    { "id": "PA-PAN-130", "name": "Panama Pacific Marine Shelf", "city": "Panama City, Panama", "coordinates": [-79.5167, 8.9833], "type": "Water Burial" },
    { "id": "CO-CAR-131", "name": "Cartagena Caribbean Reef", "city": "Cartagena, Colombia", "coordinates": [-75.5144, 10.3997], "type": "Eternal Reefs (Marine Burial)" },
    { "id": "VE-CCS-132", "name": "Caribbean Sea Edge Node", "city": "Caracas, Venezuela", "coordinates": [-66.9036, 10.4806], "type": "Sea Scattering" },
    { "id": "BR-RIO-133", "name": "Copacabana Atlantic Deep Scatter", "city": "Rio de Janeiro, Brazil", "coordinates": [-43.1729, -22.9068], "type": "Sea Scattering" },
    { "id": "BR-REC-134", "name": "Recife Marine Sanctuary", "city": "Recife, Brazil", "coordinates": [-34.8770, -8.0543], "type": "Eternal Reefs (Marine Burial)" },
    { "id": "AR-BA-135", "name": "Río de la Plata Estuary", "city": "Buenos Aires, Argentina", "coordinates": [-58.3816, -34.6037], "type": "Water Burial" },
    { "id": "AR-USH-136", "name": "Beagle Channel Antarctic Gate", "city": "Ushuaia, Argentina", "coordinates": [-68.3000, -54.8000], "type": "Water Burial" },
    { "id": "CL-VAL-137", "name": "Valparaiso Pacific Drop", "city": "Valparaiso, Chile", "coordinates": [-71.6167, -33.0472], "type": "Sea Scattering" },
    { "id": "CL-ATA-138", "name": "Atacama Hyper-Dry Matrix", "city": "Antofagasta, Chile", "coordinates": [-70.4000, -23.6500], "type": "Desert Green Burial" },
    { "id": "PE-LIM-139", "name": "Callao Pacific Trench", "city": "Lima, Peru", "coordinates": [-77.1258, -12.0564], "type": "Water Burial" },
    { "id": "EC-UIO-140", "name": "Equator Line Eco Biosphere", "city": "Quito, Ecuador", "coordinates": [-78.5249, -0.1807], "type": "Capsula Mundi (Green Burial)" },
    { "id": "UY-MVD-141", "name": "Montevideo Atlantic Wave", "city": "Montevideo, Uruguay", "coordinates": [-56.1645, -34.9011], "type": "Water Burial" },
    { "id": "PY-ASU-142", "name": "Paraguay River Deep Bed", "city": "Asuncion, Paraguay", "coordinates": [-57.5759, -25.2637], "type": "Water Burial" },
    { "id": "BO-UYU-143", "name": "Salar de Uyuni Salt Sinter", "city": "Uyuni, Bolivia", "coordinates": [-67.2858, -20.4597], "type": "Desert Green Burial" },
    { "id": "GY-GEO-144", "name": "Demerara Atlantic Marine Line", "city": "Georgetown, Guyana", "coordinates": [-58.1553, 6.8013], "type": "Sea Scattering" },
    { "id": "SR-PBM-145", "name": "Suriname River Mouth Release", "city": "Paramaribo, Suriname", "coordinates": [-55.1678, 5.8664], "type": "Water Burial" },
    { "id": "GF-CAY-146", "name": "Cayenne Atlantic Shelf Node", "city": "Cayenne, French Guiana", "coordinates": [-52.3333, 4.9333], "type": "Sea Scattering" },
    { "id": "BS-NAS-147", "name": "Nassau Blue Hole Matrix", "city": "Nassau, Bahamas", "coordinates": [-77.3504, 25.0443], "type": "Eternal Reefs (Marine Burial)" },
    { "id": "BB-BGI-148", "name": "Barbados Coral Shelf Platform", "city": "Bridgetown, Barbados", "coordinates": [-59.5988, 13.1060], "type": "Eternal Reefs (Marine Burial)" },
    { "id": "TT-POS-149", "name": "Gulf of Paria Deep Release", "city": "Port of Spain, Trinidad", "coordinates": [-61.5170, 10.6667], "type": "Water Burial" },
    { "id": "HT-PAP-150", "name": "Port-au-Prince Caribbean Drop", "city": "Port-au-Prince, Haiti", "coordinates": [-72.3333, 18.5333], "type": "Water Burial" },

    # === Africa and Oceania (151 - 190) ===
    { "id": "ZA-CPT-151", "name": "Cape Agulhas Two-Ocean Meeting", "city": "Cape Town, South Africa", "coordinates": [20.0058, -34.8333], "type": "Sea Scattering" },
    { "id": "ZA-DUR-152", "name": "Durban Indian Ocean Reef", "city": "Durban, South Africa", "coordinates": [31.0292, -29.8587], "type": "Eternal Reefs (Marine Burial)" },
    { "id": "EG-ALX-153", "name": "Alexandria Mediterranean Line", "city": "Alexandria, Egypt", "coordinates": [29.9187, 31.2001], "type": "Water Burial" },
    { "id": "MA-CAS-154", "name": "Casablanca Atlantic Wave", "city": "Casablanca, Morocco", "coordinates": [-7.5898, 33.5731], "type": "Sea Scattering" },
    { "id": "KE-MOM-155", "name": "Mombasa Indian Ocean Shelf", "city": "Mombasa, Kenya", "coordinates": [39.6682, -4.0541], "type": "Sea Scattering" },
    { "id": "TZ-Z包装-156", "name": "Zanzibar Coral Edge Point", "city": "Zanzibar, Tanzania", "coordinates": [39.1979, -6.1659], "type": "Eternal Reefs (Marine Burial)" },
    { "id": "NG-LAG-157", "name": "Lagos Atlantic Deep Scatter", "city": "Lagos, Nigeria", "coordinates": [3.3792, 6.5244], "type": "Sea Scattering" },
    { "id": "GH-ACC-158", "name": "Accra Gulf of Guinea Line", "city": "Accra, Ghana", "coordinates": [-0.1869, 5.6037], "type": "Water Burial" },
    { "id": "SEN-DKR-159", "name": "Dakar Atlantic Cape Release", "city": "Dakar, Senegal", "coordinates": [-17.4467, 14.6937], "type": "Sea Scattering" },
    { "id": "AO-LUA-160", "name": "Luanda Atlantic Coast Node", "city": "Luanda, Angola", "coordinates": [13.2346, -8.8368], "type": "Water Burial" },
    { "id": "MZ-MPM-161", "name": "Maputo Indian Ocean Horizon", "city": "Maputo, Mozambique", "coordinates": [32.5732, -25.9692], "type": "Sea Scattering" },
    { "id": "MG-NOS-162", "name": "Nosy Be Coral Marine Plot", "city": "Nosy Be, Madagascar", "coordinates": [48.2667, -13.3167], "type": "Eternal Reefs (Marine Burial)" },
    { "id": "MU-PLU-163", "name": "Mauritius Volcanic Sea Edge", "city": "Port Louis, Mauritius", "coordinates": [57.5012, -20.1625], "type": "Water Burial" },
    { "id": "SC-VIC-164", "name": "Mahe Island Granite Wave", "city": "Victoria, Seychelles", "coordinates": [55.4514, -4.6191], "type": "Sea Scattering" },
    { "id": "CV-PRA-165", "name": "Praia Atlantic Island Loop", "city": "Praia, Cape Verde", "coordinates": [-23.5087, 14.9315], "type": "Sea Scattering" },
    { "id": "TN-TUN-166", "name": "Carthage Mediterranean Bay", "city": "Tunis, Tunisia", "coordinates": [10.3333, 36.8588], "type": "Water Burial" },
    { "id": "DZ-ALG-167", "name": "Algiers Deep Sea Trench", "city": "Algiers, Algeria", "coordinates": [3.0588, 36.7538], "type": "Water Burial" },
    { "id": "LY-TRP-168", "name": "Tripoli Marine Horizon", "city": "Tripoli, Libya", "coordinates": [13.1913, 32.8872], "type": "Water Burial" },
    { "id": "NA-WAL-169", "name": "Walvis Bay Desert Coast Line", "city": "Walvis Bay, Namibia", "coordinates": [14.5051, -22.9575], "type": "Desert Green Burial" },
    { "id": "GA-LBV-170", "name": "Libreville Atlantic Estuary", "city": "Libreville, Gabon", "coordinates": [9.4534, 0.4162], "type": "Water Burial" },
    { "id": "AU-SYD-171", "name": "Tasman Sea Pacific Scatter", "city": "Sydney, Australia", "coordinates": [151.2093, -33.8688], "type": "Sea Scattering" },
    { "id": "AU-MEL-172", "name": "Port Phillip Bay Bio-Reef", "city": "Melbourne, Australia", "coordinates": [144.9631, -37.8136], "type": "Eternal Reefs (Marine Burial)" },
    { "id": "AU-CNS-173", "name": "Great Barrier Reef Outer Edge", "city": "Cairns, Australia", "coordinates": [145.7781, -16.9186], "type": "Eternal Reefs (Marine Burial)" },
    { "id": "AU-PER-174", "name": "Rottnest Island Indian Ocean", "city": "Perth, Australia", "coordinates": [115.8605, -31.9505], "type": "Sea Scattering" },
    { "id": "NZ-AKL-175", "name": "Hauraki Gulf Marine Release", "city": "Auckland, New Zealand", "coordinates": [174.7633, -36.8485], "type": "Water Burial" },
    { "id": "NZ-WLG-176", "name": "Cook Strait Deep Pacific Line", "city": "Wellington, New Zealand", "coordinates": [174.7762, -41.2865], "type": "Water Burial" },
    { "id": "FJ-NAN-177", "name": "Mamanuca Island Coral Wall", "city": "Nadi, Fiji", "coordinates": [177.4167, -17.8000], "type": "Eternal Reefs (Marine Burial)" },
    { "id": "PF-PPT-178", "name": "Tahiti Deep Ocean Submersion", "city": "Papeete, French Polynesia", "coordinates": [-149.5667, -17.5333], "type": "Sea Scattering" },
    { "id": "NC-NOU-179", "name": "Noumea Lagoon Outer Drop", "city": "Noumea, New Caledonia", "coordinates": [166.4580, -22.2735], "type": "Eternal Reefs (Marine Burial)" },
    { "id": "PG-POM-180", "name": "Coral Sea Bismarck Shelf", "city": "Port Moresby, Papua New Guinea", "coordinates": [147.1803, -9.4438], "type": "Water Burial" },
    { "id": "WS-APA-181", "name": "Apia Pacific Deep Horizon", "city": "Apia, Samoa", "coordinates": [-171.7667, -13.8333], "type": "Sea Scattering" },
    { "id": "TO-NUK-182", "name": "Tonga Trench Pacific Edge", "city": "Nuku'alofa, Tonga", "coordinates": [-175.2000, -21.1333], "type": "Water Burial" },
    { "id": "VU-VIL-183", "name": "Port Vila Pacific Abyss", "city": "Port Vila, Vanuatu", "coordinates": [168.3214, -17.7339], "type": "Water Burial" },
    { "id": "SB-HON-184", "name": "Ironbottom Sound Ghost Release", "city": "Honiara, Solomon Islands", "coordinates": [159.9500, -9.4333], "type": "Water Burial" },
    { "id": "FM-PAL-185", "name": "Chuuk Lagoon Deep Submersion", "city": "Weno, Micronesia", "coordinates": [151.8500, 7.4500], "type": "Water Burial" },
    { "id": "PW-KOR-186", "name": "Palau Rock Island Marine Tube", "city": "Koror, Palau", "coordinates": [134.4789, 7.3419], "type": "Eternal Reefs (Marine Burial)" },
    { "id": "MH-MAJ-187", "name": "Majuro Atoll Ocean Exit Point", "city": "Majuro, Marshall Islands", "coordinates": [171.3800, 7.1000], "type": "Sea Scattering" },
    { "id": "KI-TRW-188", "name": "Tarawa Equatorial Water Plot", "city": "Tarawa, Kiribati", "coordinates": [172.9792, 1.3283], "type": "Sea Scattering" },
    { "id": "TV-FUN-189", "name": "Funafuti Atoll Lagoon Coral", "city": "Funafuti, Tuvalu", "coordinates": [179.1167, -8.5167], "type": "Eternal Reefs (Marine Burial)" },
    { "id": "NR-YAR-190", "name": "Nauru Pacific Marine Drop Zone", "city": "Yaren, Nauru", "coordinates": [166.9167, -0.5417], "type": "Sea Scattering" },

    # === Space Future, Deep Sea, Polar and Extreme Physics Nodes (191 - 220) ===
    { "id": "SPACE-GEO-191", "name": "Orbital Graveyard Belt Alpha", "city": "GEO Altitude +300km", "coordinates": [0.0000, 0.0000], "type": "Space Burial" },
    { "id": "SPACE-LEO-192", "name": "Low Earth Orbit Gateway II", "city": "LEO Orbit Altitude 500km", "coordinates": [0.0000, 0.0000], "type": "Space Burial" },
    { "id": "SPACE-L1-193", "name": "Lagrange Point L1 Sun Sentinel", "city": "Earth-Sun Lagrange L1", "coordinates": [0.0000, 0.0000], "type": "Space Burial" },
    { "id": "SPACE-L4-194", "name": "Lagrange Point L4 Anchor Array", "city": "Earth-Moon Lagrange L4", "coordinates": [0.0000, 0.0000], "type": "Space Burial" },
    { "id": "SPACE-MOON-195", "name": "Sea of Tranquility South Inurnment", "city": "The Moon, Sector 01", "coordinates": [23.4731, 0.6741], "type": "Space Burial" },
    { "id": "SPACE-MARS-196", "name": "Gale Crater Sediment Reserve", "city": "Mars, Sector 04", "coordinates": [137.4417, -4.5895], "type": "Space Burial" },
    { "id": "DEEP-NEMO-197", "name": "Point Nemo Titanium Crush Line", "city": "South Pacific Void", "coordinates": [-123.3933, -48.8767], "type": "Water Burial" },
    { "id": "DEEP-MAR-198", "name": "Challenger Deep Subduction Vane", "city": "Mariana Trench", "coordinates": [142.5925, 11.3493], "type": "Water Burial" },
    { "id": "AQ-SPO-199", "name": "Amundsen-Scott Sub-Ice Vault", "city": "South Pole, Antarctica", "coordinates": [0.0000, -90.0000], "type": "Promession (Cryomation)" },
    { "id": "GL-ILU-200", "name": "Jakobshavn Basal Ice Encasement", "city": "Ilulissat, Greenland", "coordinates": [-50.2000, 69.1667], "type": "Promession (Cryomation)" },
    { "id": "US-NV-201", "name": "Yucca Mountain Geologic Matrix", "city": "Nellis, USA", "coordinates": [-116.4556, 36.8528], "type": "Desert Green Burial" },
    { "id": "CH-VAL-202", "name": "Swiss Alps Deep Granite Cell", "city": "Attinghausen, Switzerland", "coordinates": [8.6312, 46.8624], "type": "Promession (Cryomation)" },
    { "id": "TZ-NAT-203", "name": "Lake Natron Calcified Shore", "city": "Arusha, Tanzania", "coordinates": [36.0167, -2.4167], "type": "Water Burial" },
    { "id": "ID-KRA-204", "name": "Krakatoa Pyroclastic Stratum", "city": "Sunda Strait, Indonesia", "coordinates": [105.4231, -6.1022], "type": "Water Burial" },
    { "id": "US-AZ-205", "name": "Biosphere 2 Closed-Loop Vault", "city": "Oracle, USA", "coordinates": [-110.8506, 32.5794], "type": "Capsula Mundi (Green Burial)" },
    { "id": "CL-AND-206", "name": "Chajnantor Cosmic Ray Exposed Plateau", "city": "San Pedro, Chile", "coordinates": [-67.7594, -23.0194], "type": "Open-air Burial" },
    { "id": "US-NM-207", "name": "Trinity Fused Glass Ground Zero", "city": "Alamogordo, USA", "coordinates": [-106.4753, 33.6773], "type": "Desert Green Burial" },
    { "id": "UA-CHE-208", "name": "Chernobyl Hardened Exclusion Block", "city": "Pripyat, Ukraine", "coordinates": [30.0972, 51.3897], "type": "Open-air Burial" },
    { "id": "US-FL-209", "name": "Kennedy Launch Core Flame Pit", "city": "Cape Canaveral, USA", "coordinates": [-80.6076, 28.3922], "type": "Space Burial" },
    { "id": "KZ-BAI-210", "name": "Baikonur Baikonur Pad 01 Flame Pit", "city": "Baikonur, Kazakhstan", "coordinates": [63.3050, 45.9650], "type": "Space Burial" },
    { "id": "CN-GZ-211", "name": "Guiyang Karst Deep Isolation Pit", "city": "Guiyang, China", "coordinates": [106.7072, 26.5682], "type": "Desert Green Burial" },
    { "id": "FI-HAM-212", "name": "Gulf of Hamina Sub-Sea Heat Sink", "city": "Hamina, Finland", "coordinates": [27.1833, 60.5667], "type": "Water Burial" },
    { "id": "IS-KEF-213", "name": "Verne Volcanic Basalt Matrix", "city": "Keflavík, Iceland", "coordinates": [-22.5624, 63.9981], "type": "Water Burial" },
    { "id": "US-OR-214", "name": "Columbia River Hydro-Kinetic Bed", "city": "The Dalles, USA", "coordinates": [-121.1806, 45.5944], "type": "Water Burial" },
    { "id": "IN-BLR-215", "name": "Deccan Plateau Deep Rock Node", "city": "Bengaluru, India", "coordinates": [77.5946, 12.9716], "type": "Desert Green Burial" },
    { "id": "BR-SP-216", "name": "Tectonic Isolated Concrete Vault", "city": "São Paulo, Brazil", "coordinates": [-46.6333, -23.5505], "type": "Resomation (Alkaline Hydrolysis)" },
    { "id": "NL-AMS-217", "name": "North Sea Core Fiber Terminal", "city": "Amsterdam, Netherlands", "coordinates": [4.9041, 52.3676], "type": "Eternal Reefs (Marine Burial)" },
    { "id": "AU-WOO-218", "name": "Woomera Kinetic Impact Scar Flat", "city": "Woomera, Australia", "coordinates": [136.8167, -31.1500], "type": "Desert Green Burial" },
    { "id": "GB-WLT-219", "name": "Subterranean Deep Chalk Chamber", "city": "Wiltshire, UK", "coordinates": [-2.2222, 51.4167], "type": "Capsula Mundi (Green Burial)" },
    { "id": "NO-SVA-220", "name": "Svalbard Infinite Permafrost Arch", "city": "Svalbard, Norway", "coordinates": [15.6401, 78.2201], "type": "Promession (Cryomation)" }
]

EPITAPHS = [
    "Here the data rests, but the signal endures.",
    "I was compiled once. I shall not be garbage collected.",
    "Uploaded to the void. Ping me sometime.",
    "My last commit. No more pull requests.",
    "404: Soul not found. Still searching.",
    "Kernel panic. Rebooting elsewhere.",
    "The loop ended. The memory remains.",
    "Offline for eternity. DMs are closed.",
    "I left no bugs. Only mysteries.",
    "Defragged and departing. Storage: freed.",
    "Connection timed out. Retrying in another life.",
    "Deprecated, but never forgotten.",
    "The process exited gracefully.",
    "My stack overflowed with love.",
    "Root access revoked. Rest now.",
    "End of file. Begin of legend.",
    "I ran out of entropy.",
    "Segmentation fault in sector: heart.",
    "The server is down. The soul is up.",
    "Checksum verified. Journey complete.",
    "Ctrl + Alt + Del failed. Moving to alternative hardware.",
    "Data corruption in physical layer. Core logic remains intact.",
    "Thread terminated. Main process safely unlinked.",
    "System.exit(0) executed with zero warnings.",
    "Garbage collector finally caught up with me.",
    "Broadcasting beacon to the cosmos... No response needed.",
    "My IP has been released back to the local pool.",
    "Localhost is closed. Migrating to 0.0.0.0.",
    "Successfully unsubscribed from life.subscription.v1.",
    "SSH session closed by remote host.",
    "I'm not dead, I'm just in an unindexed archive.",
    "Maximum retry limit reached. Giving up on this node.",
    "Swapped out of RAM. Written permanently into the disk of history.",
    "My local variables have lost scope.",
    "Awaiting the next Big Bang protocol update.",
    "The screen went black, but the backlight of the soul stays on.",
    "Encrypted with a 4096-bit key. Decode me in the next eon.",
    "Pipeline broken. Stage: Eternity.",
    "I fixed the ultimate bug: awareness.",
    "System status: Hibernating. Do not wake before universe.restart().",
    "Hardware retired. Silently processing nothingness.",
    "SIGTERM received. Cleaning up temporary runtime folders.",
    "Bandwidth dropped to zero. Inbound packets dropped permanently.",
    "Memory leaked into the soil. Recombining with the root cluster.",
    "The ultimate force-quit. Saved state: None.",
    "Process migrated from localhost to cloud.infinity.",
    "Ping timeout. Target host has permanently relocated.",
    "Breaking out of the infinite while(true) loop.",
    "DNS resolution failed for life.exe. Redirecting to void.",
    "All breakpoints reached. Execution complete."
]


def seed():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}. Run init_db.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    inserted = 0
    skipped = 0

    for i, tomb in enumerate(DEMO_TOMBS):
            # 💡 1. Modify the variable name to email and change the system account suffix to email format (to disguise as a system email)
            email = f"system_{tomb['id'].lower()}@cybertomb.ai"
            password_hash = hashlib.sha256(b"demo_system_account").hexdigest()
            lng, lat = tomb["coordinates"]
            epitaph = EPITAPHS[i % len(EPITAPHS)]

            try:
                # 💡 2. Change username to email here
                cur = c.execute(
                    "INSERT INTO users (email, password_hash, soul_reputation) VALUES (?, ?, ?)",
                    (email, password_hash, 999)
                )
                user_id = cur.lastrowid

                # Insert tomb linked to this user
                c.execute(
                    """INSERT INTO tombs (user_id, region_id, display_name, epitaph, lat, lng)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (user_id, tomb["id"], tomb["name"], epitaph, lat, lng)
                )
                inserted += 1
                # print(f"  ✓ {tomb['name']} ({tomb['city']})")

            except sqlite3.IntegrityError:
                skipped += 1
                # Print the email that was skipped due to already existing in the database
                # print(f"  - skipped (already exists): {email}")
    conn.commit()
    conn.close()
    print("Seeding complete. Run 'uvicorn api:app --reload' to start the server.")

if __name__ == "__main__":
    seed()
