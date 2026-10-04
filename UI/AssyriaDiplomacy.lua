-- Diplomacy screen art for Tiglath-Pileser III.
--
-- Leaders without a 3D model get a 2D "fallback" image, which the engine normally loads from a cooked
-- texture package (.blp) that only ModBuddy can build. Instead, this script puts our loose .dds
-- (Textures/Assyria_Diplomacy_Leader.dds, imported via <ImportFiles>) on the diplomacy screen's own
-- FallbackLeaderImage control whenever his screen is shown.

local LEADER   = "LEADER_TIGLATH_PILESER"
local TEXTURE  = "Assyria_Diplomacy_Leader.dds"
local IMG_W, IMG_H = 800, 1080
local CONTROL_PATH = "/InGame/DiplomacyActionView/FallbackLeaderImage"

local m_showing = false

local function ApplyImage()
	if not m_showing then return end
	local img = ContextPtr:LookUpControl(CONTROL_PATH)
	if img == nil then
		print("ASSYRIA_DIPLO: diplomacy image control not found at " .. CONTROL_PATH)
		return
	end
	img:SetTexture(TEXTURE)
	-- Full screen height, centred on the leader anchor (the control is anchored by its left edge).
	local _, screenH = UIManager:GetScreenSizeVal()
	local w = math.floor(screenH * IMG_W / IMG_H)
	img:SetSizeVal(w, screenH)
	img:SetOffsetX(-math.floor(w / 2))
	img:SetHide(false)
end

-- Fires before the leader starts loading: remember whether it's ours.
local function OnShowLeaderScreen(leaderName)
	m_showing = (leaderName == LEADER)
	ApplyImage()
end

-- The diplomacy screen re-shows FallbackLeaderImage once loading finishes; set ours again on top.
local function OnLeaderLoaded()
	ApplyImage()
end

Events.ShowLeaderScreen.Add(OnShowLeaderScreen)
Events.LeaderScreenFinishedLoading.Add(OnLeaderLoaded)
Events.HideLeaderScreen.Add(function() m_showing = false end)
