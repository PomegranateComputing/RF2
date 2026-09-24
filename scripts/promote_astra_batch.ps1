[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$BatchPath,
    [switch]$AllowReplace,
    # 'old/prefix/=new/prefix/' pairs applied to target_relpath (Astra proposals sometimes point
    # at sprites/ with long names that the engine would truncate to one 8-character lump name).
    [string[]]$Remap = @(),
    # Take the target file name from a manifest field instead of the proposed one:
    # 'sprite_alias_proposal' (alias + .png) or 'cached_source' (basename of the legacy source).
    [ValidateSet('', 'sprite_alias_proposal', 'cached_source')][string]$NameFrom = ''
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

$pairs = foreach ($r in $Remap) {
    $i = $r.IndexOf('=')
    if ($i -lt 1) { throw "Remap invalide: $r (attendu 'ancien/=nouveau/')" }
    [pscustomobject]@{ From = $r.Substring(0, $i); To = $r.Substring($i + 1) }
}

$manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
$log = [System.Collections.Generic.List[object]]::new()
$seen = @{}
foreach ($f in $manifest.files) {
    $src = Join-Path $BatchPath ([string]$f.file)
    $proposed = [string]$f.target_relpath
    $relposix = $proposed
    foreach ($p in $pairs) {
        if ($relposix.StartsWith($p.From, [System.StringComparison]::OrdinalIgnoreCase)) { $relposix = $p.To + $relposix.Substring($p.From.Length); break }
    }
    if ($NameFrom) {
        $value = [string]$f.$NameFrom
        if (-not $value) { throw "Champ $NameFrom absent pour $($f.file)" }
        $name = if ($NameFrom -eq 'cached_source') { [System.IO.Path]::GetFileName($value) } else { $value + [System.IO.Path]::GetExtension($relposix) }
        $dir = $relposix.Substring(0, [Math]::Max(0, $relposix.LastIndexOf('/')))
        $relposix = if ($dir) { "$dir/$name" } else { $name }
    }
    $rel = $relposix.Replace('/','\')
    if ([System.IO.Path]::IsPathRooted($rel) -or $rel -match '(^|\\)\.\.(\\|$)') { throw "target_relpath interdit: $rel" }
    if ($seen.ContainsKey($rel.ToLowerInvariant())) { throw "Deux fichiers visent la meme cible: $rel" }
    $seen[$rel.ToLowerInvariant()] = $true
    $dst = Join-Path (Join-Path $Root 'src') $rel
    if ((Test-Path -LiteralPath $dst) -and -not $AllowReplace) { throw "Existe deja: $dst. Revoir puis utiliser -AllowReplace si le remplacement est voulu." }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dst) | Out-Null
    Copy-Item -LiteralPath $src -Destination $dst -Force
    $hash=(Get-FileHash -LiteralPath $dst -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($hash -ne ([string]$f.sha256).ToLowerInvariant()) { throw "Hash apres copie invalide: $dst" }
    $log.Add([pscustomobject]@{source=$src; proposed_target=$proposed; target=$dst; sha256=$hash})
}
$stamp=Get-Date -Format 'yyyyMMdd_HHmmss'
$batchId=Split-Path -Leaf $BatchPath
$logPath=Join-Path $Root ("docs\\ASTRA_PROMOTION_${batchId}_${stamp}.json")
$log | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $logPath -Encoding utf8
Write-Host "PROMOTION OK: $($log.Count) fichier(s). Log: $logPath"
