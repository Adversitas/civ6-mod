# Copies the mod into Civ 6's Mods folder so the game picks it up (Additional Content > enable it).
$ErrorActionPreference = 'Stop'

$src  = $PSScriptRoot
$name = (Get-ChildItem $src -Filter *.modinfo | Select-Object -First 1).BaseName
$dest = Join-Path ([Environment]::GetFolderPath('MyDocuments')) "My Games\Sid Meier's Civilization VI\Mods\$name"

try {
	if (Test-Path -LiteralPath $dest) { Remove-Item -LiteralPath $dest -Recurse -Force }
	New-Item -ItemType Directory -Force -Path $dest | Out-Null
	Get-ChildItem $src -Exclude *.ps1, README.md, .git*, art_src | Copy-Item -Destination $dest -Recurse -Force
} catch {
	Write-Error "Install failed: $($_.Exception.Message)`nIf Windows Controlled Folder Access is on, it blocks writes to Documents; copy the folder by hand or allow PowerShell through it."
	exit 1
}

Write-Host "Installed to $dest"
