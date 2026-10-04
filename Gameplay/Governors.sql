-- Leader ability: governors establish in 1 turn.
--
-- There is no modifier for establish time, and the Lua API can only read it. Establish time comes from each
-- governor's TransitionStrength:  turns = GOVERNOR_BASE_TURNS_TO_ESTABLISH (5) * 100 / TransitionStrength
--   100 -> 5 turns, 125 -> 4 (BBG), 150 -> 3 (Victor), 500 -> 1.
--
-- So Tiglath-Pileser gets his own copy of each of the 7 governors (same names, portraits, promotions), and
-- each set is locked to its owners with Governors.TraitType, the mechanism Suleiman's Ibrahim uses:
--   * copies    -> TRAIT_LEADER_TIGLATH_PILESER_UA (only he can appoint them)
--   * originals -> TRAIT_ASSYRIA_STANDARD_GOVERNORS, given to every OTHER leader (so he can't)
--
-- NOTE: the GovernorReplaces table looks made for this, but the engine doesn't honour it (Firaxis never uses
-- it): in testing the originals stayed appointable next to the copies (two Amanis), so it isn't used here.
--
-- This file runs last (LoadOrder 500000000) so it copies the governors as other mods (BBG) left them.

-- 1. The copies -------------------------------------------------------------------------------------------
INSERT INTO Types (Type, Kind)
	SELECT 'GOVERNOR_TIGLATH_PILESER_' || substr(GovernorType, 10), 'KIND_GOVERNOR'
	FROM Governors
	WHERE GovernorType IN ('GOVERNOR_THE_DEFENDER', 'GOVERNOR_THE_AMBASSADOR', 'GOVERNOR_THE_CARDINAL',
		'GOVERNOR_THE_RESOURCE_MANAGER', 'GOVERNOR_THE_BUILDER', 'GOVERNOR_THE_EDUCATOR', 'GOVERNOR_THE_MERCHANT');

INSERT INTO Governors (GovernorType, Name, Description, IdentityPressure, Title, ShortTitle, TransitionStrength,
		AssignCityState, Image, PortraitImage, PortraitImageSelected, TraitType)
	SELECT 'GOVERNOR_TIGLATH_PILESER_' || substr(GovernorType, 10), Name, Description, IdentityPressure, Title, ShortTitle, 500,
		AssignCityState, Image, PortraitImage, PortraitImageSelected, 'TRAIT_LEADER_TIGLATH_PILESER_UA'
	FROM Governors
	WHERE GovernorType IN ('GOVERNOR_THE_DEFENDER', 'GOVERNOR_THE_AMBASSADOR', 'GOVERNOR_THE_CARDINAL',
		'GOVERNOR_THE_RESOURCE_MANAGER', 'GOVERNOR_THE_BUILDER', 'GOVERNOR_THE_EDUCATOR', 'GOVERNOR_THE_MERCHANT');

-- Same promotion trees (promotions are shared, only the set membership is copied).
-- Copy -> original name: GOVERNOR_TIGLATH_PILESER_THE_X -> GOVERNOR_THE_X
INSERT INTO GovernorPromotionSets (GovernorType, GovernorPromotion)
	SELECT g.GovernorType, s.GovernorPromotion
	FROM Governors g
	JOIN GovernorPromotionSets s ON s.GovernorType = 'GOVERNOR_' || substr(g.GovernorType, length('GOVERNOR_TIGLATH_PILESER_') + 1)
	WHERE g.TraitType = 'TRAIT_LEADER_TIGLATH_PILESER_UA';

INSERT INTO GovernorModifiers (GovernorType, ModifierId)
	SELECT g.GovernorType, gm.ModifierId
	FROM Governors g
	JOIN GovernorModifiers gm ON gm.GovernorType = 'GOVERNOR_' || substr(g.GovernorType, length('GOVERNOR_TIGLATH_PILESER_') + 1)
	WHERE g.TraitType = 'TRAIT_LEADER_TIGLATH_PILESER_UA';

INSERT INTO GovernorsCannotAssign (GovernorType, CannotAssign)
	SELECT g.GovernorType, c.CannotAssign
	FROM Governors g
	JOIN GovernorsCannotAssign c ON c.GovernorType = 'GOVERNOR_' || substr(g.GovernorType, length('GOVERNOR_TIGLATH_PILESER_') + 1)
	WHERE g.TraitType = 'TRAIT_LEADER_TIGLATH_PILESER_UA';

-- 2. Lock the originals away from him ------------------------------------------------------------------------
-- Hidden trait, same shape as the base game's TRAIT_LEADER_MAJOR_CIV (no name, InternalOnly).
INSERT INTO Types (Type, Kind) VALUES ('TRAIT_ASSYRIA_STANDARD_GOVERNORS', 'KIND_TRAIT');
INSERT INTO Traits (TraitType, InternalOnly) VALUES ('TRAIT_ASSYRIA_STANDARD_GOVERNORS', 1);

-- Every major-civ leader except him. Not via LEADER_DEFAULT: he inherits from it, so he'd get it back.
-- Not city-states: they never appoint governors, and their suzerain tooltip lists every leader trait
-- (CityStates_Expansion2.lua), so the hidden trait would show up there as an empty "unique bonus".
INSERT INTO LeaderTraits (LeaderType, TraitType)
	SELECT DISTINCT cl.LeaderType, 'TRAIT_ASSYRIA_STANDARD_GOVERNORS'
	FROM CivilizationLeaders cl
	JOIN Civilizations c ON c.CivilizationType = cl.CivilizationType
	WHERE c.StartingCivilizationLevelType = 'CIVILIZATION_LEVEL_FULL_CIV'
	AND cl.LeaderType <> 'LEADER_TIGLATH_PILESER';

UPDATE Governors SET TraitType = 'TRAIT_ASSYRIA_STANDARD_GOVERNORS'
	WHERE GovernorType IN ('GOVERNOR_THE_DEFENDER', 'GOVERNOR_THE_AMBASSADOR', 'GOVERNOR_THE_CARDINAL',
		'GOVERNOR_THE_RESOURCE_MANAGER', 'GOVERNOR_THE_BUILDER', 'GOVERNOR_THE_EDUCATOR', 'GOVERNOR_THE_MERCHANT')
	AND TraitType IS NULL;
