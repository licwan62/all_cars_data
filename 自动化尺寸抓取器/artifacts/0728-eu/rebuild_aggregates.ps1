$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$tableDir = Join-Path $scriptDir 'tables'

Write-Host "Rebuilding aggregate TSV files from batch files in: $tableDir"

# --- Rebuild dimension_groups_final.tsv ---
$dimHeader = $null
$dimById = [ordered]@{}
$dimFiles = Get-ChildItem (Join-Path $tableDir 'all_*_dimension_groups_final.tsv') | Sort-Object Name
Write-Host "Found $($dimFiles.Count) dimension_groups batch files"

foreach ($f in $dimFiles) {
    $lines = Get-Content $f.FullName -Encoding UTF8
    if ($lines.Count -lt 2) { continue }
    if ($null -eq $dimHeader) { $dimHeader = $lines[0].TrimStart([char]0xFEFF) }
    for ($i = 1; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        $cols = $line.Split("`t")
        $id = $cols[0].Trim()
        if ($id -and -not $dimById.Contains($id)) {
            $dimById[$id] = $line
        }
    }
}

$dimOut = @($dimHeader) + @($dimById.Values)
$dimOutPath = Join-Path $tableDir 'dimension_groups_final.tsv'
$dimText = ($dimOut -join "`r`n") + "`r`n"
[System.IO.File]::WriteAllText($dimOutPath, $dimText, (New-Object System.Text.UTF8Encoding $false))
Write-Host "dimension_groups_final.tsv rebuilt: $($dimById.Count) unique rows"

# --- Rebuild ktype_mapping_final.tsv ---
$ktypeHeader = $null
$ktypeById = [ordered]@{}
$ktypeFiles = Get-ChildItem (Join-Path $tableDir 'all_*_ktype_dimension_mapping_final.tsv') | Sort-Object Name
Write-Host "Found $($ktypeFiles.Count) ktype_mapping batch files"

foreach ($f in $ktypeFiles) {
    $lines = Get-Content $f.FullName -Encoding UTF8
    if ($lines.Count -lt 2) { continue }
    if ($null -eq $ktypeHeader) { $ktypeHeader = $lines[0].TrimStart([char]0xFEFF) }
    for ($i = 1; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        $cols = $line.Split("`t")
        $id = $cols[0].Trim()
        if ($id -and -not $ktypeById.Contains($id)) {
            $ktypeById[$id] = $line
        }
    }
}

$ktypeOut = @($ktypeHeader) + @($ktypeById.Values)
$ktypeOutPath = Join-Path $tableDir 'ktype_mapping_final.tsv'
$ktypeText = ($ktypeOut -join "`r`n") + "`r`n"
[System.IO.File]::WriteAllText($ktypeOutPath, $ktypeText, (New-Object System.Text.UTF8Encoding $false))
Write-Host "ktype_mapping_final.tsv rebuilt: $($ktypeById.Count) unique rows"

Write-Host "`nDone."
