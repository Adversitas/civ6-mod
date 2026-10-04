# Assyria (Tiglath-Pileser III): Civ 6 mod

A governor-themed civ, written in plain XML/SQL/Lua so you don't need ModBuddy. **Requires Rise & Fall or Gathering Storm.**
Schemas were verified against the installed game, and the gameplay database was test-built against Gathering Storm (see "Testing").

## Kit

**Civ ability: Yoke of Ashur.** Conquering a city grants a Governor Title. Conquered cities with an established Governor get +10% to all yields.

**Leader ability: Bel Pihati.** Governors establish in 1 turn.

**Unique unit: Kisir Sharruti.** Replaces the Swordsman. +3 Combat Strength within the borders of any city that has a Governor, whoever owns it.

**Unique district: Ekal Masharti.** Replaces the Government Plaza and doesn't count toward the population requirement for districts.

**Agenda: King of the Four Quarters.** Respects civilizations that govern their cities firmly.

## Names

The template placeholders were filled in with `rename.ps1` (`ASSYRIA` / `TIGLATH_PILESER`). All player-facing names are in `Text/Text_en_US.xml`.

## Layout

```
ASSYRIA.modinfo             manifest; gameplay only loads for R&F / GS rulesets
Config/Config.xml           civ picker entries (R&F, GS)
Gameplay/Civilization.xml   civ, city names, civ ability
Gameplay/Leader.xml         leader, leader trait, agenda
Gameplay/Governors.sql      leader ability (replacement governors)
Gameplay/UniqueUnit.xml     UU + its governed-territory ability
Gameplay/UniqueDistrict.sql UD (Government Plaza copy)
Gameplay/Expansion2.sql     Gathering Storm-only rows (UU Iron cost)
Scripts/UniqueUnit.lua      toggles the UU ability
Scripts/CivAbility.lua      governor title on conquest
Scripts/Compatibility.lua   World Congress governor list
UI/AssyriaDiplomacy.*       diplomacy-screen leader image
Text/Text_en_US.xml         every player-facing string
UI/Icons.xml                icon atlases for the generated textures
Textures/                   generated .dds art
ArtDefs/Units.artdef        unit model hookup (Swordsman model)
Assyria.dep                 art dependency file loading the artdef
art_src/                    art generators + previews (not installed)
UI/Colors.xml               player colours
```

## Testing

```powershell
.\install.ps1
```

If Windows' Controlled Folder Access blocks it, copy the folder into
`Documents\My Games\Sid Meier's Civilization VI\Mods\` by hand.

Logs: `%LOCALAPPDATA%\Firaxis Games\Sid Meier's Civilization VI\Logs\`, mainly `Database.log`, `Modding.log` and `Lua.log`.
In `Database.log`, look for **"Failed Validation"**. Errors from other enabled mods (e.g. BBG) show up there too.
The scripts log to `Lua.log` with the prefixes `ASSYRIA_UU:` and `ASSYRIA_CIV:`. Set `DEBUG = false` in each once it's verified.

### Check in game
- Governor panel: this leader shows 7 governors (not 14), each establishing in 1 turn.
- Government Plaza slot: it can be built in a 1-pop city, and building it grants a governor title.
- UU: the combat preview shows +3 inside a governed city's territory, both when attacking and when defending.
- Conquest: capturing a city adds a governor title (`ASSYRIA_CIV: governor title granted` in Lua.log).
  If the log says `no ChangeGovernorPoints function found`, tell Claude.
- Conquered city with an established governor: its yield breakdown shows +10%.

## Art

All art is generated, nothing is borrowed or copyrighted. Regenerate with:

```powershell
python art_src/make_art.py       # icons + loading screen -> Textures/*.dds (previews in art_src/preview/)
python art_src/make_artdefs.py   # unit model hookup -> ArtDefs/Units.artdef + Assyria.dep
```

| Asset | How |
|---|---|
| Civ symbol (winged sun disk), leader portrait, unit icon + portrait | Drawn procedurally in a palace-relief style, saved as uncompressed RGBA `.dds` at every size the game requests, loaded via `<ImportFiles>` and `UI/Icons.xml`. |
| Loading screen (leader + lapis brick wall) | Same pipeline; `LoadingInfo` in `Gameplay/Leader.xml`. |
| Kisir Sharruti 3D model | `ArtDefs/Units.artdef` is a copy of the Swordsman's unit art entry under the new unit's name, hooked in by `Assyria.dep` (modelled on Firaxis's DLC `.dep` files). It only references models already in the game, so no ModBuddy build is needed. |
| Ekal Masharti | Uses the Government Plaza's 3D model. Its own icon (palace gate) is generated: aliasing the Plaza icon failed on the setup screen. |
| Diplomacy screen leader | `Textures/Assyria_Diplomacy_Leader.dds` (detailed version of the king). `UI/AssyriaDiplomacy.lua` puts it on the diplomacy screen's fallback-leader image control, so no ModBuddy package is needed. |

### Still missing
- No voice lines, leader animation or music.

## Compatibility
- World Congress "Governance Doctrine" only offers governors without a trait; `Scripts/Compatibility.lua` restores the
  list after the originals got the hidden trait (if the base handler runs last, that resolution just won't appear).
- `Governors.sql`, `UniqueDistrict.sql` and `Expansion2.sql` copy existing rows, so they load last (LoadOrder 500000000).
  Loading them before BBG once broke BBG: its UPDATEs moved our copied promotion rows, its governor file aborted,
  and the game failed validation on `BBG_REQUIRES_PLOT_SIX_TILES_AWAY`.
