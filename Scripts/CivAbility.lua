-- Civ ability, part 1: conquering a city grants a governor title.
-- (Part 2, +10% yields in conquered cities with a governor, is pure data in Gameplay/Civilization.xml.)
--
-- No modifier fires on conquest, so this listens for GameEvents.CityConquered.
-- Anti-exploit: each city grants at most one title ever (stored on the city, survives save/load),
-- and retaking a city you originally founded grants nothing.

local CIV_TYPE   = "CIVILIZATION_ASSYRIA"
local PROPERTY   = "ASSYRIA_TITLE_GRANTED"
local DEBUG      = true   -- prints to Lua.log; turn off once verified in game

local function Log(...)
	if DEBUG then print("ASSYRIA_CIV:", ...) end
end

local function IsOurCiv(playerID)
	local cfg = PlayerConfigurations[playerID]
	return cfg ~= nil and cfg:GetCivilizationTypeName() == CIV_TYPE
end

-- The binding exists in the gameplay DLL (ChangeGovernorPoints), but which object owns it isn't documented:
-- try the player's governor object first, then the player itself.
local function GrantGovernorTitle(playerID)
	local pPlayer = Players[playerID]
	local pGovs = pPlayer:GetGovernors()
	if pGovs ~= nil and pGovs.ChangeGovernorPoints ~= nil then
		pGovs:ChangeGovernorPoints(1)
		return true
	end
	if pPlayer.ChangeGovernorPoints ~= nil then
		pPlayer:ChangeGovernorPoints(1)
		return true
	end
	Log("ERROR: no ChangeGovernorPoints function found; title not granted")
	return false
end

local function OnCityConquered(capturerID, previousOwnerID, cityID, x, y)
	if not IsOurCiv(capturerID) then return end

	local pCity = Cities.GetCityInPlot(x, y)
	if pCity == nil then
		Log("conquered city not found at", x, y)
		return
	end
	if pCity:GetProperty(PROPERTY) ~= nil then
		Log(pCity:GetName(), "already granted a title before")
		return
	end
	if pCity:GetOriginalOwner() == capturerID then
		Log(pCity:GetName(), "was founded by us; recapture grants nothing")
		return
	end

	if GrantGovernorTitle(capturerID) then
		pCity:SetProperty(PROPERTY, 1)
		Log("governor title granted for", pCity:GetName())
	end
end

GameEvents.CityConquered.Add(OnCityConquered)
Log("script loaded")
