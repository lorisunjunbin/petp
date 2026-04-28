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
    { $_ -in 'bgd','bg-detach','detach' } {
        $entry      = 'PETP_backgroud.py'
        $mode_label = 'background-detached'
    }
    'stop' {
        Set-Location $RootDir
        & $PythonBin PETP_backgroud.py --stop
        exit $LASTEXITCODE
    }
    { $_ -in '-h','--help','help' } {
        Write-Host @"
Usage:
  .\scripts\windows\start_petp.ps1 [gui|bg|bgd|stop] [args...]

Modes:
  gui          Launch desktop GUI (default)
  bg           Launch background mode (attached to terminal)
  bgd          Launch background mode detached (hidden window, survives terminal close)
  stop         Stop a running background instance (via PID file)

Examples:
  .\scripts\windows\start_petp.ps1 gui
  .\scripts\windows\start_petp.ps1 bg --run-execution ENDECODER --no-http
  .\scripts\windows\start_petp.ps1 bg --run-execution MY_EXEC --headless --no-http
  .\scripts\windows\start_petp.ps1 bgd
  .\scripts\windows\start_petp.ps1 bgd --headless
  .\scripts\windows\start_petp.ps1 stop

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

if ($mode_label -eq 'background-detached') {
    $LogFile = if ($env:PETP_BG_LOG) { $env:PETP_BG_LOG } else { 'petp_bg.log' }
    $allArgs = @($entry) + $ExtraArgs
    $proc = Start-Process -FilePath $PythonBin -ArgumentList $allArgs `
        -WindowStyle Hidden -RedirectStandardOutput $LogFile -RedirectStandardError "$LogFile.err" `
        -PassThru
    Write-Host "[PETP] Background started (PID=$($proc.Id), log=$LogFile)"
} else {
    $allArgs = @($entry) + $ExtraArgs
    & $PythonBin @allArgs
    exit $LASTEXITCODE
}

