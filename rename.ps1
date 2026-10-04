# Fills in the template placeholders across every file in the mod.
#
#   .\rename.ps1 -Civ AKSUM -CivDisplay "Aksum" -Leader EZANA -LeaderDisplay "Ezana" -Author "Hamza"
#
# -Civ / -Leader are database IDs: UPPERCASE, letters/digits/underscores only.
# Run it once on a fresh copy; afterwards the placeholders are gone.
param(
	[Parameter(Mandatory)][ValidatePattern('^[A-Z][A-Z0-9_]*$')][string]$Civ,
	[Parameter(Mandatory)][string]$CivDisplay,
	[Parameter(Mandatory)][ValidatePattern('^[A-Z][A-Z0-9_]*$')][string]$Leader,
	[Parameter(Mandatory)][string]$LeaderDisplay,
	[string]$Author = 'AUTHOR'
)

$root = $PSScriptRoot
$utf8 = New-Object System.Text.UTF8Encoding($false)

# Display names first: "CIVNAME_DISPLAY" contains "CIVNAME".
$map = [ordered]@{
	'CIVNAME_DISPLAY'    = $CivDisplay
	'LEADERNAME_DISPLAY' = $LeaderDisplay
	'CIVNAME'            = $Civ
	'LEADERNAME'         = $Leader
	'AUTHOR'             = $Author
}

Get-ChildItem $root -Recurse -File -Include *.xml, *.modinfo, *.sql, *.lua | ForEach-Object {
	$text = [IO.File]::ReadAllText($_.FullName)
	foreach ($k in $map.Keys) { $text = $text.Replace($k, $map[$k]) }
	[IO.File]::WriteAllText($_.FullName, $text, $utf8)
}

$modinfo = Join-Path $root 'CIVNAME.modinfo'
if (Test-Path $modinfo) { Rename-Item $modinfo "$Civ.modinfo" }

# Fresh mod ID so this mod never collides with another copy of the template.
$newId = [guid]::NewGuid().ToString()
$mi = Join-Path $root "$Civ.modinfo"
$text = [IO.File]::ReadAllText($mi) -replace '<Mod id="[^"]+"', "<Mod id=`"$newId`""
[IO.File]::WriteAllText($mi, $text, $utf8)

Write-Host "Done. Mod ID: $newId"
