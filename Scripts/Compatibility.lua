-- World Congress "Governance Doctrine" (Gathering Storm) offers only governors with no TraitType
-- (DLC/Expansion2/Scripts/WorldCongress.lua). Governors.sql gives the 7 standard governors a hidden trait
-- (so Tiglath-Pileser can't appoint them), which would leave that resolution with no options.
-- This handler supplies the full list again. If the base handler happens to run after this one it
-- overwrites it and the resolution simply doesn't appear; nothing breaks either way.

local STANDARD_TRAIT = "TRAIT_ASSYRIA_STANDARD_GOVERNORS"
local cached = nil

local function GovernanceDoctrineOptions(resolutionType, playerId, options)
	if cached == nil then
		cached = {}
		for row in GameInfo.Governors() do
			if row.TraitType == nil or row.TraitType == STANDARD_TRAIT then
				table.insert(cached, row.Hash)
			end
		end
	end
	options.ResolutionOptions = cached
end

if GameEvents.WC_ValidateGovernanceDoctrine ~= nil then
	GameEvents.WC_ValidateGovernanceDoctrine.Add(GovernanceDoctrineOptions)
end
