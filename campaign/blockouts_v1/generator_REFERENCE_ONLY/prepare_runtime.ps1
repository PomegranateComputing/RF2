$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Runtime = Join-Path $Root 'runtime'
$Iwads = Join-Path $Root 'iwads'
$Downloads = Join-Path $Root 'downloads'
New-Item -ItemType Directory -Force -Path $Runtime,$Iwads,$Downloads | Out-Null
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

function Get-VerifiedArchive([string]$Uri,[string]$Path,[string]$Expected) {
    if (Test-Path -LiteralPath $Path) {
        if ((Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() -eq $Expected) { return }
        throw "Archive existante de hash different : $Path. Renommer ce seul fichier, puis relancer."
    }
    $Part = $Path + '.part'
    Write-Host "Telechargement : $Uri"
    Invoke-WebRequest -UseBasicParsing -Uri $Uri -OutFile $Part
    $Actual = (Get-FileHash -LiteralPath $Part -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($Actual -ne $Expected) { throw "Hash incorrect pour $Part : $Actual" }
    Move-Item -LiteralPath $Part -Destination $Path
}

if (-not (Test-Path -LiteralPath (Join-Path $Runtime 'uzdoom.exe'))) {
    $EngineZip = Join-Path $Downloads 'UZDoom-5.0.1-Windows-x64.zip'
    Get-VerifiedArchive 'https://github.com/UZDoom/UZDoom/releases/download/5.0.1/Windows-UZDoom-Release-x86_64.zip' $EngineZip 'abc39ceea3d266d471e1b5db860c8e29edba4e7ebefc3ba60a9abec13138ef74'
    $Stage = Join-Path $Downloads ('engine-' + [Guid]::NewGuid().ToString('N'))
    Expand-Archive -LiteralPath $EngineZip -DestinationPath $Stage
    $Exe = @(Get-ChildItem -LiteralPath $Stage -Recurse -Filter 'uzdoom.exe' -File)
    if ($Exe.Count -ne 1) { throw 'Un unique uzdoom.exe etait attendu.' }
    Get-ChildItem -LiteralPath $Exe[0].DirectoryName -Force | Copy-Item -Destination $Runtime -Recurse
}
if (-not (Test-Path -LiteralPath (Join-Path $Iwads 'freedoom2.wad'))) {
    $FreeZip = Join-Path $Downloads 'freedoom-0.13.0.zip'
    Get-VerifiedArchive 'https://github.com/freedoom/freedoom/releases/download/v0.13.0/freedoom-0.13.0.zip' $FreeZip '3f9b264f3e3ce503b4fb7f6bdcb1f419d93c7b546f4df3e874dd878db9688f59'
    $Stage = Join-Path $Downloads ('freedoom-' + [Guid]::NewGuid().ToString('N'))
    Expand-Archive -LiteralPath $FreeZip -DestinationPath $Stage
    $Wad = @(Get-ChildItem -LiteralPath $Stage -Recurse -Filter 'freedoom2.wad' -File)
    if ($Wad.Count -ne 1) { throw 'Un unique freedoom2.wad etait attendu.' }
    Copy-Item -LiteralPath $Wad[0].FullName -Destination $Iwads
    Get-ChildItem -LiteralPath $Wad[0].DirectoryName -File | Where-Object { $_.Extension -ne '.wad' } | Copy-Item -Destination $Iwads
}
if (-not (Test-Path -LiteralPath (Join-Path $Runtime 'uzdoom.pk3'))) { throw 'uzdoom.pk3 absent du runtime.' }
Write-Host 'Preparation terminee. Lancer JOUER.cmd.'
