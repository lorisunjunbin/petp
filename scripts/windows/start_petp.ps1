#Requires -Version 5.1
<#
.SYNOPSIS
    Start PETP in gui or background (nogui) mode.

.DESCRIPTION
    Equivalent of scripts/macos/start_petp.sh for Windows.

.PARAMETER Mode
    Run mode: gui (default) | bg | background | help

.PARAMETER Args
    Extra arguments forwarded to the Python entry point.

.EXAMPLE
    .\scripts\windows\start_petp.ps1
    .\scripts\windows\start_petp.ps1 gui
    .\scripts\windows\start_petp.ps1 bg --run-execution ENDECODER --no-http

.NOTES
    Environment variables (optional, set before calling this script):
      PYTHON_BIN              Python executable  (default: python)
      PYTHONUNBUFFERED        Unbuffered stdout  (default: 1)
      PYTHONDONTWRITEBYTECODE Disable .pyc writes(default: 1)
      PETP_ECHO_ENV           Set to 1 to print effective settings
#>

[CmdletBinding()]
param(
    [string]$Mode = 'gui',
    [Parameter(ValueFromRemainingArguments)]
    [string[]]$ExtraArgs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ── Resolve paths ────────────────────────────────────────────────────────────
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RootDir   = (Resolve-Path (Join-Path $ScriptDir '..\..')).Path

# ── Environment defaults ──────────────────────────────────────────────────────
if (-not $env:PYTHON_BIN)              { $env:PYTHON_BIN              = 'python' }
if (-not $env:PYTHONUNBUFFERED)        { $env:PYTHONUNBUFFERED        = '1'      }
if (-not $env:PYTHONDONTWRITEBYTECODE) { $env:PYTHONDONTWRITEBYTECODE = '1'      }

$PythonBin = $env:PYTHON_BIN

# ── Mode selection ────────────────────────────────────────────────────────────
$entry      = ''
$mode_label = ''

switch ($Mode.ToLower()) {
    'gui' {
        $entry      = 'PETP.py'
        $mode_label = 'gui'
    }
    { $_ -in 'bg','background' } {
        $entry      = 'PETP_backgroud.py'
        $mode_label = 'background'
    }
    { $_ -in '-h','--help','help' } {
        Write-Host @"
Usage:
  .\scripts\windows\start_petp.ps1 [gui|bg|background] [args...]

Examples:
  .\scripts\windows\start_petp.ps1 gui
  .\scripts\windows\start_petp.ps1 bg --run-execution ENDECODER --no-http

Environment variables (optional, set before calling):
  PYTHON_BIN              Python executable (default: python)
  PYTHONUNBUFFERED        Unbuffered stdout/stderr (default: 1)
  PYTHONDONTWRITEBYTECODE Disable .pyc writes (default: 1)
  PETP_ECHO_ENV           Set to 1 to print effective settings
"@
        exit 0
    }
    default {
        Write-Error "Unsupported mode: $Mode`nTry: .\scripts\windows\start_petp.ps1 help"
        exit 2
    }
}

# ── Optional diagnostics ──────────────────────────────────────────────────────
if ($env:PETP_ECHO_ENV -eq '1') {
    Write-Host "[PETP] mode=$mode_label"
    Write-Host "[PETP] root=$RootDir"
    Write-Host "[PETP] python_bin=$PythonBin"
    Write-Host "[PETP] PYTHONUNBUFFERED=$env:PYTHONUNBUFFERED"
    Write-Host "[PETP] PYTHONDONTWRITEBYTECODE=$env:PYTHONDONTWRITEBYTECODE"
}

# ── Launch ────────────────────────────────────────────────────────────────────
Set-Location $RootDir

$allArgs = @($entry) + $ExtraArgs
& $PythonBin @allArgs
exit $LASTEXITCODE

