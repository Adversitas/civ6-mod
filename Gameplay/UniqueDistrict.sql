-- Unique district: replaces the Government Plaza and doesn't count toward the population-based district limit.
--
-- Everything is copied from DISTRICT_GOVERNMENT at load time (stats, trade yields, modifiers, adjacencies),
-- so the only differences are RequiresPopulation = 0 and the trait that makes it unique.

INSERT INTO Types (Type, Kind) VALUES
	('DISTRICT_ASSYRIA_UD', 'KIND_DISTRICT'),
	('TRAIT_CIVILIZATION_DISTRICT_ASSYRIA_UD', 'KIND_TRAIT');

INSERT INTO Traits (TraitType, Name) VALUES
	('TRAIT_CIVILIZATION_DISTRICT_ASSYRIA_UD', 'LOC_DISTRICT_ASSYRIA_UD_NAME');

INSERT INTO CivilizationTraits (CivilizationType, TraitType) VALUES
	('CIVILIZATION_ASSYRIA', 'TRAIT_CIVILIZATION_DISTRICT_ASSYRIA_UD');

INSERT INTO Districts (DistrictType, Name, Description, TraitType, RequiresPopulation,
		PrereqTech, PrereqCivic, Coast, Cost, RequiresPlacement, NoAdjacentCity, CityCenter, Aqueduct, InternalOnly, ZOC,
		FreeEmbark, HitPoints, CaptureRemovesBuildings, CaptureRemovesCityDefenses, PlunderType, PlunderAmount, TradeEmbark,
		MilitaryDomain, CostProgressionModel, CostProgressionParam1, Appeal, Housing, Entertainment, OnePerCity,
		AllowsHolyCity, Maintenance, AirSlots, CitizenSlots, TravelTime, CityStrengthModifier, AdjacentToLand, CanAttack,
		AdvisorType, CaptureRemovesDistrict, MaxPerPlayer)
	SELECT 'DISTRICT_ASSYRIA_UD', 'LOC_DISTRICT_ASSYRIA_UD_NAME', 'LOC_DISTRICT_ASSYRIA_UD_DESCRIPTION',
		'TRAIT_CIVILIZATION_DISTRICT_ASSYRIA_UD', 0,
		PrereqTech, PrereqCivic, Coast, Cost, RequiresPlacement, NoAdjacentCity, CityCenter, Aqueduct, InternalOnly, ZOC,
		FreeEmbark, HitPoints, CaptureRemovesBuildings, CaptureRemovesCityDefenses, PlunderType, PlunderAmount, TradeEmbark,
		MilitaryDomain, CostProgressionModel, CostProgressionParam1, Appeal, Housing, Entertainment, OnePerCity,
		AllowsHolyCity, Maintenance, AirSlots, CitizenSlots, TravelTime, CityStrengthModifier, AdjacentToLand, CanAttack,
		AdvisorType, CaptureRemovesDistrict, MaxPerPlayer
	FROM Districts WHERE DistrictType = 'DISTRICT_GOVERNMENT';

INSERT INTO DistrictReplaces (CivUniqueDistrictType, ReplacesDistrictType) VALUES
	('DISTRICT_ASSYRIA_UD', 'DISTRICT_GOVERNMENT');

-- Per-district child tables
INSERT INTO District_TradeRouteYields (DistrictType, YieldType, YieldChangeAsOrigin, YieldChangeAsDomesticDestination, YieldChangeAsInternationalDestination)
	SELECT 'DISTRICT_ASSYRIA_UD', YieldType, YieldChangeAsOrigin, YieldChangeAsDomesticDestination, YieldChangeAsInternationalDestination
	FROM District_TradeRouteYields WHERE DistrictType = 'DISTRICT_GOVERNMENT';

INSERT INTO District_Adjacencies (DistrictType, YieldChangeId)
	SELECT 'DISTRICT_ASSYRIA_UD', YieldChangeId FROM District_Adjacencies WHERE DistrictType = 'DISTRICT_GOVERNMENT';

INSERT INTO District_CitizenYieldChanges (DistrictType, YieldType, YieldChange)
	SELECT 'DISTRICT_ASSYRIA_UD', YieldType, YieldChange FROM District_CitizenYieldChanges WHERE DistrictType = 'DISTRICT_GOVERNMENT';

INSERT INTO District_GreatPersonPoints (DistrictType, GreatPersonClassType, PointsPerTurn)
	SELECT 'DISTRICT_ASSYRIA_UD', GreatPersonClassType, PointsPerTurn FROM District_GreatPersonPoints WHERE DistrictType = 'DISTRICT_GOVERNMENT';

INSERT INTO District_ValidTerrains (DistrictType, TerrainType)
	SELECT 'DISTRICT_ASSYRIA_UD', TerrainType FROM District_ValidTerrains WHERE DistrictType = 'DISTRICT_GOVERNMENT';

-- Loyalty pressure etc.
INSERT INTO DistrictModifiers (DistrictType, ModifierId)
	SELECT 'DISTRICT_ASSYRIA_UD', ModifierId FROM DistrictModifiers WHERE DistrictType = 'DISTRICT_GOVERNMENT';

-- Other districts get +1 yield for being next to the Government Plaza. The game doesn't treat a unique
-- district as its base for AdjacentDistrict (e.g. the Mahavihara has separate Lavra rows), so mirror them.
INSERT INTO Adjacency_YieldChanges (ID, Description, YieldType, YieldChange, TilesRequired, OtherDistrictAdjacent,
		AdjacentSeaResource, AdjacentTerrain, AdjacentFeature, AdjacentRiver, AdjacentWonder, AdjacentNaturalWonder,
		AdjacentImprovement, AdjacentDistrict, PrereqCivic, PrereqTech, ObsoleteCivic, ObsoleteTech, AdjacentResource,
		AdjacentResourceClass, Self)
	SELECT 'ASSYRIA_UD_' || ID, Description, YieldType, YieldChange, TilesRequired, OtherDistrictAdjacent,
		AdjacentSeaResource, AdjacentTerrain, AdjacentFeature, AdjacentRiver, AdjacentWonder, AdjacentNaturalWonder,
		AdjacentImprovement, 'DISTRICT_ASSYRIA_UD', PrereqCivic, PrereqTech, ObsoleteCivic, ObsoleteTech, AdjacentResource,
		AdjacentResourceClass, Self
	FROM Adjacency_YieldChanges WHERE AdjacentDistrict = 'DISTRICT_GOVERNMENT';

INSERT INTO District_Adjacencies (DistrictType, YieldChangeId)
	SELECT da.DistrictType, 'ASSYRIA_UD_' || da.YieldChangeId
	FROM District_Adjacencies da JOIN Adjacency_YieldChanges a ON a.ID = da.YieldChangeId
	WHERE a.AdjacentDistrict = 'DISTRICT_GOVERNMENT';

INSERT INTO Improvement_Adjacencies (ImprovementType, YieldChangeId)
	SELECT ia.ImprovementType, 'ASSYRIA_UD_' || ia.YieldChangeId
	FROM Improvement_Adjacencies ia JOIN Adjacency_YieldChanges a ON a.ID = ia.YieldChangeId
	WHERE a.AdjacentDistrict = 'DISTRICT_GOVERNMENT';

-- The Plaza's free governor title is a game-wide modifier gated on "player has DISTRICT_GOVERNMENT".
-- Widen that check to "has the Plaza OR this district", so the title is granted exactly once either way.
INSERT INTO Requirements (RequirementId, RequirementType) VALUES
	('ASSYRIA_PLAYER_HAS_UD', 'REQUIREMENT_PLAYER_HAS_DISTRICT');

INSERT INTO RequirementArguments (RequirementId, Name, Value) VALUES
	('ASSYRIA_PLAYER_HAS_UD', 'DistrictType', 'DISTRICT_ASSYRIA_UD');

UPDATE RequirementSets SET RequirementSetType = 'REQUIREMENTSET_TEST_ANY'
	WHERE RequirementSetId = 'PLAYER_HAS_GOVERNMENT_DISTRICT_REQUIREMENTS';

INSERT INTO RequirementSetRequirements (RequirementSetId, RequirementId) VALUES
	('PLAYER_HAS_GOVERNMENT_DISTRICT_REQUIREMENTS', 'ASSYRIA_PLAYER_HAS_UD');
