param(
    [Parameter(ValueFromRemainingArguments = $true)]
    $RemainingArgs
)

$scriptPath = Join-Path $PSScriptRoot "agy_rr.py"
& python $scriptPath @RemainingArgs
