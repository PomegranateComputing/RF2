[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Src = Join-Path $Root 'src'
$Build = Join-Path $Root 'build'
$Dist = Join-Path $Root 'dist'
$Stage = Join-Path $Build 'pk3_stage'
$Out = Join-Path $Dist 'RF2_DEV.pk3'

if (-not (Test-Path -LiteralPath $Src -PathType Container)) { throw "src absent: $Src" }
if (-not (Test-Path -LiteralPath (Join-Path $Src 'MAPINFO') -PathType Leaf)) { throw 'src\\MAPINFO absent.' }

$maps = @(Get-ChildItem -LiteralPath (Join-Path $Src 'maps') -Filter 'RF??.wad' -File -ErrorAction Stop)
if ($maps.Count -lt 23) { throw "23 maps attendues, trouvees: $($maps.Count)" }

if (Test-Path -LiteralPath $Stage) { Remove-Item -LiteralPath $Stage -Recurse -Force }
New-Item -ItemType Directory -Force -Path $Stage,$Dist | Out-Null
Copy-Item -Path (Join-Path $Src '*') -Destination $Stage -Recurse -Force

if (Test-Path -LiteralPath $Out) { Remove-Item -LiteralPath $Out -Force }
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory(
    $Stage,
    $Out,
    [System.IO.Compression.CompressionLevel]::Fastest,
    $false
)

$hash = (Get-FileHash -LiteralPath $Out -Algorithm SHA256).Hash.ToLowerInvariant()
Write-Host "BUILD OK: $Out"
Write-Host "SHA256  : $hash"
