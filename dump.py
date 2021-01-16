import struct
import json
import collections
from typing import Dict
import xml.etree.ElementTree as ET
import glob, os

modType = {
    "VMT_SPOILER": 0,
    "VMT_BUMPER_F": 1,
    "VMT_BUMPER_R": 2,
    "VMT_SKIRT": 3,
    "VMT_EXHAUST": 4,
    "VMT_CHASSIS": 5,
    "VMT_GRILL": 6,
    "VMT_BONNET": 7,
    "VMT_WING_L": 8,
    "VMT_WING_R": 9,
    "VMT_ROOF": 10,
    "VMT_ENGINE": 11,
    "VMT_BRAKES": 12,
    "VMT_GEARBOX": 13,
    "VMT_HORN": 14,
    "VMT_SUSPENSION": 15,
    "VMT_ARMOUR": 16,
    "VMT_PLTHOLDER": 25,
    "VMT_PLTVANITY": 26,
    "VMT_INTERIOR1": 27,
    "VMT_INTERIOR2": 28,
    "VMT_INTERIOR3": 29,
    "VMT_INTERIOR4": 30,
    "VMT_INTERIOR5": 31,
    "VMT_SEATS": 32,
    "VMT_STEERING": 33,
    "VMT_KNOB": 34,
    "VMT_PLAQUE": 35,
    "VMT_ICE": 36,
    "VMT_TRUNK": 37,
    "VMT_HYDRO": 38,
    "VMT_ENGINEBAY1": 39,
    "VMT_ENGINEBAY2": 40,
    "VMT_ENGINEBAY3": 41,
    "VMT_CHASSIS2": 42,
    "VMT_CHASSIS3": 43,
    "VMT_CHASSIS4": 44,
    "VMT_CHASSIS5": 45,
    "VMT_DOOR_L": 46,
    "VMT_WHEELS_REAR_OR_HYDRAULICS": 47,
    "VMT_LIVERY_MOD": 48
}

checkList = ["visibleMods/Item", "statMods/Item"]

def generateModkit(modkit: ET.Element):
    kitID = int(modkit.find("id").attrib["value"])

    kitTemp = {
        "ModNumTotal": 0,
        "Index": kitID,
        "Mods": {}
    }

    modCount = 0

    for check in checkList:
        for mod in modkit.findall(check):
            modIndex = int(modType.get(mod.find("type").text, 0xFF))

            if modIndex not in kitTemp["Mods"]:
                kitTemp["Mods"][modIndex] = []
            
            kitTemp["Mods"][modIndex].append(modCount)
            modCount = modCount + 1
    
    kitTemp["ModNumTotal"] = len(kitTemp["Mods"].keys())
    return kitTemp

def generateIthronJSON(modkits):
    ithron = {
        "MagicBytes":"TU8=",
        "Version": 1,
        "ModKits": []
    }

    for key in modkits:
        mod = modkits[key]
        modTemp = {
            "ModKitName": key,
            "ModNumTotal": mod["ModNumTotal"],
            "Index": mod["Index"],
            "Mods": []
        }

        for indexKey in mod["Mods"]:
            modArray = mod["Mods"][indexKey]
            modTemp["Mods"].append({
               "ModType": int(indexKey),
               "ModNum": len(modArray),
               "ModIndex": modArray
            })

        ithron["ModKits"].append(modTemp)

    ithron["ModKits"] = sorted(ithron["ModKits"], key=lambda k: k['Index'])

    with open('vehmods_ithron.json', 'w') as outfile:
        json.dump(ithron, outfile, indent=4)
        outfile.close()

def generateDrakeJSON(modkits: Dict):
    sortedModkits = collections.OrderedDict(sorted(modkits.items(), key=lambda t:t[1]["Index"]))

    with open('vehmods_drake.json', 'w') as outfile:
        json.dump(sortedModkits, outfile, indent=4)
        outfile.close()

def generateDrakeBin(modkits: Dict):
    modkits = collections.OrderedDict(sorted(modkits.items(), key=lambda t:t[1]["Index"]))
    with open('vehmods_drake.bin', 'wb') as outfile:

        outfile.write(struct.pack('<2c', *[char.encode("UTF-8") for char in "MO"]))
        outfile.write(struct.pack('<H', 1))

        for modkitKey in modkits:
            modkit = modkits[modkitKey]

            outfile.write(struct.pack('<H', modkit["Index"]))
            outfile.write(struct.pack('<H', len(modkitKey)))
            outfile.write(struct.pack(f'<{len(modkitKey)}c', *[char.encode("UTF-8") for char in modkitKey]))
            outfile.write(struct.pack('<B', len(modkit["Mods"].keys())))

            for modKey in modkit["Mods"]:
                print(modKey)
                mod = modkit["Mods"][modKey]

                outfile.write(struct.pack('<B', int(modKey)))
                outfile.write(struct.pack('<B', len(mod)))

                for modID in mod:
                    outfile.write(struct.pack('<H', int(modID)))

        # json.dump(modkits, outfile, indent=4)
        outfile.close()



def main():

    modkits = {}
    for file in glob.glob('*.meta'):
        tree = ET.parse(file)
        root = tree.getroot()

        for kit in root.findall('Kits/Item'):
            kitName = kit.find("kitName").text

            if kitName not in modkits.keys():
                modkits[kitName] = generateModkit(kit)
            else:
                for check in checkList:
                    if len(kit.findall(check)) > sum([len(modkits[kitName]["Mods"][x]) for x in modkits[kitName]["Mods"] if isinstance(modkits[kitName]["Mods"][x], list)]):
                        modkits[kitName] = generateModkit(kit)

    generateDrakeJSON(modkits)
    generateIthronJSON(modkits)
    generateDrakeBin(modkits)    
        

if __name__ == "__main__":
    main()