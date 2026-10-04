-- Unique unit: +3 Combat Strength (attacking and defending) inside the borders of a city that has a governor
-- (any owner: own, allied, neutral or enemy).
--
-- The game has no requirement for "the city owning this tile has a governor", so this script keeps
-- ABILITY_ASSYRIA_UU_GOVERNED switched on exactly while the unit stands in such territory.
--
-- "Has a governor" = a governor is assigned to the city, established or not.
-- To require an established governor instead, set REQUIRE_ESTABLISHED = true.

local ABILITY             = "ABILITY_ASSYRIA_UU_GOVERNED"
local UNIT_INDEX          = GameInfo.Units["UNIT_ASSYRIA_UU"].Index
local REQUIRE_ESTABLISHED = false
local DEBUG               = true   -- prints to Lua.log; turn off once verified in game

local function Log(...)
	if DEBUG then print("ASSYRIA_UU:", ...) end
end

-- ---------------------------------------------------------------------------
local function CityHasGovernor(pCity)
	local ok, pGovernor = pcall(function() return pCity:GetAssignedGovernor() end)
	if not ok then
		Log("GetAssignedGovernor failed:", pGovernor)
		return false
	end
	if pGovernor == nil then return false end
	if REQUIRE_ESTABLISHED then
		local okE, established = pcall(function() return pGovernor:IsEstablished() end)
		return okE and established == true
	end
	return true
end

local function IsInGovernedTerritory(pUnit)
	local pPlot = Map.GetPlot(pUnit:GetX(), pUnit:GetY())
	if pPlot == nil or not pPlot:IsOwned() then return false end
	local pCity = Cities.GetPlotPurchaseCity(pPlot)
	return pCity ~= nil and CityHasGovernor(pCity)
end

local function UpdateUnit(pUnit)
	if pUnit == nil or pUnit:GetType() ~= UNIT_INDEX then return end
	local pAbility = pUnit:GetAbility()
	local have = pAbility:GetAbilityCount(ABILITY)
	local want = IsInGovernedTerritory(pUnit) and 1 or 0
	if have ~= want then
		pAbility:ChangeAbilityCount(ABILITY, want - have)
		Log("unit", pUnit:GetOwner(), pUnit:GetID(), "at", pUnit:GetX(), pUnit:GetY(), "bonus", want == 1 and "ON" or "OFF")
	end
end

local function UpdateAllUnits()
	for _, playerID in ipairs(PlayerManager.GetAliveMajorIDs()) do
		for _, pUnit in Players[playerID]:GetUnits():Members() do
			UpdateUnit(pUnit)
		end
	end
end

-- ---------------------------------------------------------------------------
-- Triggers: the unit's own movement, plus anything that can change which tiles are "governed".
local function OnUnitChanged(playerID, unitID)
	UpdateUnit(UnitManager.GetUnit(playerID, unitID))
end

GameEvents.OnUnitMoved.Add(OnUnitChanged)
GameEvents.UnitInitialized.Add(OnUnitChanged)

-- Governors assigned/moved/removed anywhere. These are UI-side events; guarded in case this context lacks them
-- (the turn-start refresh below still catches every change, one turn later at worst).
for _, name in ipairs({ "GovernorAssigned", "GovernorChanged" }) do
	if Events[name] then Events[name].Add(UpdateAllUnits) else Log("event not available:", name) end
end

-- Borders shifting, cities changing hands
GameEvents.CityConquered.Add(UpdateAllUnits)
GameEvents.PlayerTurnStarted.Add(UpdateAllUnits)

Log("script loaded, unit index", UNIT_INDEX)
