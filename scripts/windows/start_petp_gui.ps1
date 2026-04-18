#Requires -Version 5.1
<#
.SYNOPSIS
    Start PETP in GUI mode.
.EXAMPLE
    .\scripts\windows\start_petp_gui.ps1
#>

[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments)]
    [string[]]$ExtraArgs
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
& "$ScriptDir\start_petp.ps1" gui @ExtraArgs
exit $LASTEXITCODE

