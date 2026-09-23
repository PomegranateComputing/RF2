$ErrorActionPreference='Stop'
$Root=Split-Path -Parent $PSScriptRoot
$Maps=Get-Content -LiteralPath (Join-Path $Root 'docs\CAMPAIGN.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$Maps | ForEach-Object { Write-Host ('{0:00}  {1}' -f $_.number,$_.title) }
$Raw=Read-Host 'Carte (1 a 23)'
$Number=0
if (-not [int]::TryParse($Raw,[ref]$Number) -or $Number -lt 1 -or $Number -gt 23) { throw 'Numero invalide.' }
$Code='RF{0:00}' -f $Number
$Userdata=Join-Path $Root 'userdata'
New-Item -ItemType Directory -Force -Path $Userdata | Out-Null
& (Join-Path $Root 'runtime\uzdoom.exe') '-noautoload' '-iwad' (Join-Path $Root 'iwads\freedoom2.wad') '-file' (Join-Path $Root 'build\RF2_MAPS_V1.pk3') '-config' (Join-Path $Userdata 'rf2.ini') '-savedir' $Userdata '-shotdir' $Userdata '+map' $Code
exit $LASTEXITCODE
