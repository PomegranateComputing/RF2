[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$BatchPath,
    [switch]$AllowReplace
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$BatchPath = [System.IO.Path]::GetFullPath($BatchPath)
$Incoming = [System.IO.Path]::GetFullPath((Join-Path $Root 'incoming\astra')).TrimEnd('\')
if (-not $BatchPath.StartsWith($Incoming + '\',[System.StringComparison]::OrdinalIgnoreCase)) { throw 'Batch hors de incoming\\astra.' }
$ManifestPath = Join-Path $BatchPath 'manifest.json'
if (-not (Test-Path -LiteralPath $ManifestPath)) { throw 'manifest.json absent.' }

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    & $python.Source (Join-Path $PSScriptRoot 'validate_astra_batch.py') $BatchPath
} else {
    & py -3 (Join-Path $PSScriptRoot 'validate_astra_batch.py') $BatchPath
}
if ($LASTEXITCODE -ne 0) { throw 'Validation Astra batch echouee.' }

$manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
$log = [System.Collections.Generic.List[object]]::new()
foreach ($f in $manifest.files) {
    $src = Join-Path $BatchPath ([string]$f.file)
    $rel = ([string]$f.target_relpath).Replace('/','\')
    if ([System.IO.Path]::IsPathRooted($rel) -or $rel -match '(^|\\)\.\.(\\|$)') { throw "target_relpath interdit: $rel" }
    $dst = Join-Path (Join-Path $Root 'src') $rel
    if ((Test-Path -LiteralPath $dst) -and -not $AllowReplace) { throw "Existe deja: $dst. Revoir puis utiliser -AllowReplace si le remplacement est voulu." }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dst) | Out-Null
    Copy-Item -LiteralPath $src -Destination $dst -Force
    $hash=(Get-FileHash -LiteralPath $dst -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($hash -ne ([string]$f.sha256).ToLowerInvariant()) { throw "Hash apres copie invalide: $dst" }
    $log.Add([pscustomobject]@{source=$src; target=$dst; sha256=$hash})
}
$stamp=Get-Date -Format 'yyyyMMdd_HHmmss'
$logPath=Join-Path $Root ("docs\\ASTRA_PROMOTION_${stamp}.json")
$log | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $logPath -Encoding utf8
Write-Host "PROMOTION OK: $($log.Count) fichier(s). Log: $logPath"
