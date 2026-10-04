-- Gathering Storm only: tables that don't exist in Rise & Fall.
-- (A row aimed at a missing table fails the whole database load, so these are kept in their own action.)

-- Same Iron cost as the Swordsman it replaces
INSERT INTO Units_XP2 (UnitType, ResourceCost)
	SELECT 'UNIT_ASSYRIA_UU', ResourceCost FROM Units_XP2 WHERE UnitType = 'UNIT_SWORDSMAN';
