[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$errors = [System.Collections.Generic.List[string]]::new()

function NeedFile([string]$Path) { if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { $errors.Add("missing file: $Path") } }
function NeedDir([string]$Path) { if (-not (Test-Path -LiteralPath $Path -PathType Container)) { $errors.Add("missing dir: $Path") } }

NeedDir (Join-Path $Root 'src')
NeedDir (Join-Path $Root 'src\maps')
NeedDir (Join-Path $Root 'campaign\blockouts_v1')
NeedDir (Join-Path $Root 'incoming\astra')
NeedFile (Join-Path $Root 'src\MAPINFO')
NeedFile 'C:\PROJECTS\TOOLS\UZDoom-5.0.1\uzdoom.exe'
NeedFile 'C:\PROJECTS\TOOLS\UZDoom-5.0.1\uzdoom.pk3'
NeedFile 'C:\PROJECTS\TOOLS\Freedoom-0.13.0\freedoom2.wad'

for ($i=1; $i -le 23; $i++) {
    $name = ('RF{0:D2}.wad' -f $i)
    NeedFile (Join-Path $Root ('src\maps\' + $name))
}

if ($errors.Count) {
    $errors | ForEach-Object { Write-Error $_ }
    throw "VALIDATION FAIL: $($errors.Count) erreur(s)."
}
Write-Host 'VALIDATION PASS: structure, engine, IWAD, MAPINFO and RF01-RF23 present.'
