[CmdletBinding()]
param(
    [ValidatePattern('^RF(0[1-9]|1[0-9]|2[0-3])$')]
    [string]$Map = 'RF01',
    [switch]$NoBuild
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Engine = 'C:\PROJECTS\TOOLS\UZDoom-5.0.1\uzdoom.exe'
$IwAD = 'C:\PROJECTS\TOOLS\Freedoom-0.13.0\freedoom2.wad'
$Game = Join-Path $Root 'dist\RF2_DEV.pk3'
$User = Join-Path $Root 'user'
$Config = Join-Path $User 'uzdoom.ini'
$SaveDir = Join-Path $User 'savegames'

if (-not $NoBuild) { & (Join-Path $PSScriptRoot 'build.ps1') }
if (-not (Test-Path -LiteralPath $Engine)) { throw "UZDoom absent: $Engine" }
if (-not (Test-Path -LiteralPath $IwAD)) { throw "Freedoom absent: $IwAD" }
if (-not (Test-Path -LiteralPath $Game)) { throw "Build absent: $Game" }
New-Item -ItemType Directory -Force -Path $User,$SaveDir | Out-Null

$args = @('-iwad',$IwAD,'-file',$Game,'-config',$Config,'-savedir',$SaveDir,"+map",$Map)
Write-Host "RUN: $Map"
& $Engine @args
exit $LASTEXITCODE
