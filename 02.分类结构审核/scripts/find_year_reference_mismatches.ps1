param(
    [Parameter(Mandatory = $true)]
    [string]$InputPath,
    [Parameter(Mandatory = $true)]
    [string]$OutputPath
)

$rows = Import-Csv -LiteralPath $InputPath
$result = for ($index = 0; $index -lt $rows.Count; $index++) {
    $row = $rows[$index]
    $properties = @($row.PSObject.Properties)
    $targetYears = [regex]::Matches($row.YEAR, '(?<!\d)(19|20)\d{2}(?!\d)') | ForEach-Object { [int]$_.Value }
    $referenceValue = $properties[13].Value
    $referenceYears = [regex]::Matches($referenceValue, '(?<!\d)(19|20)\d{2}(?!\d)') | ForEach-Object { [int]$_.Value }

    if ($targetYears.Count -eq 0 -or $referenceYears.Count -eq 0) { continue }

    $targetMin = ($targetYears | Measure-Object -Minimum).Minimum
    $targetMax = ($targetYears | Measure-Object -Maximum).Maximum
    $referenceMin = ($referenceYears | Measure-Object -Minimum).Minimum
    $referenceMax = ($referenceYears | Measure-Object -Maximum).Maximum

    if ($referenceMax -lt $targetMin -or $referenceMin -gt $targetMax) {
        [pscustomobject]@{
            SOURCE_LINE = $index + 2
            'DIMENSION-ID' = $row.'DIMENSION-ID'
            MAKE = $row.MAKE
            MODEL = $row.MODEL
            VERSION = $properties[3].Value
            STRUCTURE = $properties[6].Value
            YEAR = $row.YEAR
            'L-IN' = $row.'L-IN'
            'W-IN' = $row.'W-IN'
            'H-IN' = $row.'H-IN'
            REFERENCE = $referenceValue
            NOTE = $properties[14].Value
            STATUS = $properties[15].Value
        }
    }
}

$parent = Split-Path -Parent $OutputPath
if ($parent -and -not (Test-Path -LiteralPath $parent)) {
    New-Item -ItemType Directory -Path $parent | Out-Null
}
$result | Export-Csv -LiteralPath $OutputPath -NoTypeInformation -Encoding UTF8
Write-Output "Wrote $($result.Count) rows to $OutputPath"
