$ErrorActionPreference = "Stop"
$env:FITMENT_OPENCLAW_LIBRARY_ONLY = "1"
. (Join-Path (Split-Path -Parent $PSScriptRoot) "qclaw_fitment_automation.ps1")

$checkpointTestDir = Join-Path ([IO.Path]::GetTempPath()) ("fitment-checkpoint-branch-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $checkpointTestDir | Out-Null
$task = [pscustomobject]@{
    TaskId = "test"
    DisplayName = "test"
    SourceName = "test.tsv"
    CheckpointPath = (Join-Path $checkpointTestDir "checkpoint.json")
}

# Checkpoint v3 must serialize a one-item root lineage as a JSON array.
function Get-TaskCheckpoint { param($Task) return $null }

Save-TaskCheckpoint -Task $task -Status "进行中" -Phase "waiting_reply" `
    -Round 1 -SendCount 1 -OutputFile "unused.md" `
    -ConversationUrl "https://chatgpt.com/c/root"

$checkpoint = Get-Content -LiteralPath $task.CheckpointPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($checkpoint.version -ne 3) { throw "checkpoint version is not 3" }
if ($checkpoint.conversation_branch_count -ne 0) { throw "root branch count is not 0" }
if (@($checkpoint.conversation_lineage).Count -ne 1) { throw "root lineage is not a one-item array" }
if ($checkpoint.conversation_lineage[0].url -ne "https://chatgpt.com/c/root") {
    throw "root lineage URL mismatch"
}

# A length-limit transition must append the new branch and checkpoint its URL.
function Get-ChatGPTState {
    return [pscustomobject]@{ conversationLimitReached = $true }
}
function Get-CurrentChatGPTUrl { return "https://chatgpt.com/c/parent" }
function Start-ChatGPTConversationBranch {
    param([string]$ParentUrl)
    if ($ParentUrl -ne "https://chatgpt.com/c/parent") { throw "parent URL mismatch" }
    return "https://chatgpt.com/c/branch"
}
function Add-Content {
    param(
        [string]$LiteralPath,
        [object]$Value,
        [string]$Encoding
    )
}
$script:savedLineage = $null
$script:savedUrl = ""
function Save-TaskCheckpoint {
    param(
        $Task,
        [string]$Status,
        [string]$Phase,
        [int]$Round,
        [int]$SendCount,
        [string]$OutputFile,
        [string]$ConversationUrl,
        [string]$Remarks,
        [object[]]$ConversationLineage
    )
    $script:savedLineage = @($ConversationLineage)
    $script:savedUrl = $ConversationUrl
}

$branchUrl = Ensure-TaskConversationCapacity -Task $task -OutputFile "unused.md" `
    -Round 7 -SendCount 6 -ConversationUrl "https://chatgpt.com/c/parent"

if ($branchUrl -ne "https://chatgpt.com/c/branch") { throw "new branch URL mismatch" }
if ($script:savedUrl -ne $branchUrl) { throw "checkpoint current URL mismatch" }
if ($script:savedLineage.Count -ne 2) { throw "branch lineage count mismatch" }
if ($script:savedLineage[1].parent_url -ne "https://chatgpt.com/c/parent") {
    throw "branch parent URL mismatch"
}
if ($script:savedLineage[1].trigger -ne "conversation_length_limit") {
    throw "branch trigger mismatch"
}
if ($script:savedLineage[1].round -ne 7) { throw "branch round mismatch" }

Remove-Item -LiteralPath $checkpointTestDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Output "checkpoint_branch_smoke: OK"
