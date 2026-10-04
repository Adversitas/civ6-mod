"""Builds ArtDefs/Units.artdef + Assyria.dep so the Kisir Sharruti uses the Swordsman's 3D model.

The unit entry is copied verbatim from the base game's UNIT_SWORDSMAN artdef and renamed; it only
references assets already in the game, so no ModBuddy cooking / BLP packages are needed.
The .dep follows the layout of Firaxis's own DLC .dep files (e.g. DLC/Babylon/Babylon.dep).

    python art_src/make_artdefs.py
"""
import re
from pathlib import Path

GAME = Path(r"D:\SteamLibrary\steamapps\common\Sid Meier's Civilization VI")
ROOT = Path(__file__).resolve().parent.parent
UNIT = "UNIT_ASSYRIA_UU"
DEP_ID = "5f0e3c2a-8d41-4c7b-9a3e-2b6d1e7f4a90"

base = (GAME / "Base" / "ArtDefs" / "Units.artdef").read_text(encoding="utf-8").split("\n")

# 1. the Swordsman element inside the root "Units" collection (3-tab indented <Element>)
i = next(n for n, l in enumerate(base) if '<m_Name text="UNIT_SWORDSMAN"/>' in l)
s = i
while base[s] != "\t\t\t<Element>":
    s -= 1
e = i
while base[e] != "\t\t\t</Element>":
    e += 1
unit_block = "\n".join(base[s:e + 1]).replace('<m_Name text="UNIT_SWORDSMAN"/>', f'<m_Name text="{UNIT}"/>')

# 2. every root collection name, so the merged file has the same shape as the base one
roots = re.findall(r'^\t\t\t<m_CollectionName text="([^"]+)"/>$', "\n".join(base), flags=re.M)

parts = ['<?xml version="1.0" encoding="UTF-8" ?>',
         "<AssetObjects..ArtDefSet>",
         "\t<m_Version>\n\t\t<major>1</major>\n\t\t<minor>0</minor>\n\t\t<build>0</build>\n\t\t<revision>0</revision>\n\t</m_Version>",
         '\t<m_TemplateName text="Units"/>',
         "\t<m_RootCollections>"]
for name in roots:
    parts.append("\t\t<Element>")
    parts.append(f'\t\t\t<m_CollectionName text="{name}"/>')
    parts.append("\t\t\t<m_ReplaceMergedCollectionElements>false</m_ReplaceMergedCollectionElements>")
    if name == "Units":
        parts.append(unit_block)
    parts.append("\t\t</Element>")
parts += ["\t</m_RootCollections>", "</AssetObjects..ArtDefSet>", ""]

(ROOT / "ArtDefs").mkdir(exist_ok=True)
(ROOT / "ArtDefs" / "Units.artdef").write_text("\n".join(parts), encoding="utf-8")

DEP = f"""<?xml version="1.0" encoding="UTF-8" ?>
<AssetObjects..GameDependencyData>
	<ID>
		<name text="Assyria"/>
		<id text="{DEP_ID}"/>
	</ID>
	<RequiredGameArtIDs/>
	<SystemDependencies>
		<Element>
			<ConsumerName text="Audio"/>
			<ArtDefDependencyPaths>
				<Element text="Units.artdef"/>
			</ArtDefDependencyPaths>
			<LibraryDependencies/>
			<LoadsLibraries>true</LoadsLibraries>
		</Element>
		<Element>
			<ConsumerName text="Units"/>
			<ArtDefDependencyPaths>
				<Element text="Units.artdef"/>
			</ArtDefDependencyPaths>
			<LibraryDependencies>
				<Element text="Unit"/>
			</LibraryDependencies>
			<LoadsLibraries>true</LoadsLibraries>
		</Element>
		<Element>
			<ConsumerName text="StrategicView_Translate"/>
			<ArtDefDependencyPaths>
				<Element text="Units.artdef"/>
			</ArtDefDependencyPaths>
			<LibraryDependencies/>
			<LoadsLibraries>true</LoadsLibraries>
		</Element>
	</SystemDependencies>
	<ArtDefDependencies>
		<Element>
			<ArtDefPath text="Units.artdef"/>
			<ArtDefDependencyPaths>
				<Element text="Units.artdef"/>
			</ArtDefDependencyPaths>
		</Element>
	</ArtDefDependencies>
	<LibraryDependencies/>
</AssetObjects..GameDependencyData>
"""
(ROOT / "Assyria.dep").write_text(DEP, encoding="utf-8")
print(f"Units.artdef: {len(roots)} root collections, unit block {len(unit_block)} chars")
