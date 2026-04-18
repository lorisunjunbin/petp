#Requires -Version 5.1
<#
.SYNOPSIS
    Start PETP in background (nogui) mode.
.EXAMPLE
    .\scripts\windows\start_petp_background.ps1 --run-execution ENDECODER --no-http
#>

[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments)]
    [string[]]$ExtraArgs
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
& "$ScriptDir\start_petp.ps1" bg @ExtraArgs
exit $LASTEXITCODE

