# Splittet db/types.xml in mehrere Kategorie-Dateien unter ce/custom_types/.
# Einmaliger Lauf nach Aufteilung. Original liegt als db/types.xml.bak vor.
import os
import re

BASE = r"C:\Program Files (x86)\Steam\steamapps\common\DayZServer\mpmissions\empty.deerisle"
SRC = os.path.join(BASE, "db", "types.xml")
DST_DIR = os.path.join(BASE, "ce", "custom_types")

os.makedirs(DST_DIR, exist_ok=True)

with open(SRC, "r", encoding="utf-8") as f:
    content = f.read()

# Greift jeden <type ...>...</type>-Block samt vorangehendem Whitespace,
# damit die Einrückung beim Wegschreiben unverändert erhalten bleibt.
TYPE_RE = re.compile(r'(\s*<type name="([^"]+)"[^>]*>.*?</type>)', re.DOTALL)
CAT_RE = re.compile(r'<category name="([^"]+)"')

# Building-Supplies (vor "tools" prüfen, da viele in category="tools" stehen)
BUILDING_SUBSTRINGS = (
    "Nail", "Plank", "BarbedWire", "MetalWire", "Sheetmetal", "Tarp",
    "Netting", "Lumber", "Firewood", "WoodenLog", "WoodenStick",
    "PileOfWoodenPlanks", "WoodenCrate", "WoodenStake",
)

# Aufsätze in category="weapons", die KEINE Schusswaffen sind
ATTACHMENT_SUBSTRINGS = (
    "Optic", "Scope", "Suppressor", "Compensator", "Bttstck", "Hndgrd",
    "Bayonet", "PistolFlashlight", "WeaponFlashlight", "UniversalLight",
    "KobraSight", "KashtanOptic", "M68Optic", "PUScope", "PSO",
    "Buttstock", "Handguard", "RedDot",
)

buckets = {
    "clothing": [],
    "ammo": [],
    "weapon_attachments": [],
    "firearms": [],
    "tools": [],
    "building_supplies": [],
    "food": [],
    "containers": [],
    "explosives": [],
    "animals": [],
    "infected": [],
    "vehicles": [],
    "misc": [],
}

VEHICLE_PREFIXES = (
    "Land_", "Boat_", "CivilianSedan", "Hatchback_", "OffroadHatchback",
    "Sedan_", "Truck_", "V3S_", "Offroad_",
    # Vehicle-Parts und Wracks
    "CivSedan", "Hatchback", "RFMosquito", "Wreck_", "SantasSleigh",
    "jmc_atv", "jmc_Boat",
    "StaticObj_Wreck_", "StaticObj_PatrolBoat", "StaticObj_Train_Wagon",
)


def has_substring(name, substrings):
    return any(s in name for s in substrings)


def categorize(name, block):
    cat_match = CAT_RE.search(block)
    cat = cat_match.group(1) if cat_match else None

    # Building Supplies zuerst (sonst landen sie in tools/misc)
    if has_substring(name, BUILDING_SUBSTRINGS):
        return "building_supplies"

    # Munition / Magazine via Namens-Präfix
    if name.startswith(("Ammo_", "AmmoBox", "Mag_")):
        return "ammo"

    if cat == "clothes":
        return "clothing"
    if cat in ("food", "industrialfood"):
        return "food"
    if cat == "containers":
        return "containers"
    if cat == "explosives":
        return "explosives"

    if cat == "weapons":
        if has_substring(name, ATTACHMENT_SUBSTRINGS):
            return "weapon_attachments"
        return "firearms"

    if cat == "tools":
        return "tools"

    # Items ohne <category> — nach Namens-Mustern aufteilen
    if name.startswith("Animal_"):
        return "animals"
    if name.startswith(("ZmbM_", "ZmbF_")):
        return "infected"
    if name.startswith(VEHICLE_PREFIXES):
        return "vehicles"

    return "misc"


for m in TYPE_RE.finditer(content):
    block = m.group(1)
    name = m.group(2)
    buckets[categorize(name, block)].append(block)

total = 0
for bucket_name, blocks in buckets.items():
    out_path = os.path.join(DST_DIR, f"types_{bucket_name}.xml")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n<types>')
        for b in blocks:
            f.write(b)
        f.write("\n</types>\n")
    print(f"  types_{bucket_name}.xml: {len(blocks):4d} items")
    total += len(blocks)

print(f"\nGesamt: {total} items geschrieben")
